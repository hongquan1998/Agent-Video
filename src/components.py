import math
import numpy as np
import cairo

W, H = 1920, 1080

def hex_rgb(h):
    h = h.lstrip("#")
    if len(h) == 6:
        return tuple(int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))
    elif len(h) == 8:
        return tuple(int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4, 6))
    return (1.0, 1.0, 1.0)

def rounded_rect(ctx, x, y, w, h, r):
    r = min(r, abs(w) / 2.0, abs(h) / 2.0)
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    ctx.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
    ctx.close_path()

def draw_vignette(ctx, intensity=0.42):
    ctx.save()
    rad = math.hypot(W, H) / 1.6
    pat = cairo.RadialGradient(W / 2, H / 2, rad * 0.4, W / 2, H / 2, rad)
    pat.add_color_stop_rgba(0.0, 0, 0, 0, 0.0)
    pat.add_color_stop_rgba(1.0, 0, 0, 0, intensity)
    ctx.rectangle(0, 0, W, H)
    ctx.set_source(pat)
    ctx.fill()
    ctx.restore()

# -------------------------------------------------------------
# Detailed USS Squalus (SS-192) Profile Rig
# -------------------------------------------------------------
def draw_squalus_detailed(ctx, x, y, scale=1.0, pitch_deg=0.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(math.radians(pitch_deg))
    ctx.scale(scale, scale)
    
    # 1. Main Ballast Hull
    ctx.new_path()
    ctx.move_to(480, 5)
    ctx.curve_to(465, -35, 380, -48, 260, -48)
    ctx.line_to(-390, -48)
    ctx.curve_to(-470, -48, -535, -28, -570, -5)
    ctx.line_to(-570, 12)
    ctx.curve_to(-530, 38, -440, 52, -320, 52)
    ctx.line_to(280, 52)
    ctx.curve_to(410, 52, 465, 30, 480, 5)
    ctx.close_path()
    
    hull_grad = cairo.LinearGradient(0, -50, 0, 55)
    hull_grad.add_color_stop_rgb(0.0, *hex_rgb("#415059"))
    hull_grad.add_color_stop_rgb(0.4, *hex_rgb("#29353B"))
    hull_grad.add_color_stop_rgb(1.0, *hex_rgb("#161F23"))
    ctx.set_source(hull_grad)
    ctx.fill_preserve()
    ctx.set_source_rgb(*hex_rgb("#0F1518"))
    ctx.set_line_width(2.8)
    ctx.stroke()
    
    # Hull plating seams & wet steel specular reflection
    ctx.set_source_rgba(0.05, 0.08, 0.10, 0.45)
    ctx.set_line_width(1.5)
    for px in range(-480, 420, 65):
        ctx.move_to(px, -42); ctx.line_to(px, 45); ctx.stroke()
        
    # Wet steel highlight streak along hull curve
    pat_wet = cairo.LinearGradient(0, -25, 0, 5)
    pat_wet.add_color_stop_rgba(0.0, 1, 1, 1, 0.0)
    pat_wet.add_color_stop_rgba(0.5, 0.8, 0.92, 1.0, 0.22)
    pat_wet.add_color_stop_rgba(1.0, 1, 1, 1, 0.0)
    ctx.rectangle(-450, -25, 880, 30)
    ctx.set_source(pat_wet); ctx.fill()
    
    # Limber holes (water escape louvers)
    ctx.set_source_rgb(*hex_rgb("#101518"))
    for lx in range(-460, 360, 32):
        rounded_rect(ctx, lx, 18, 18, 7, 3); ctx.fill()

    # 2. Conning Tower Fairing (Sargo-class design)
    ctx.new_path()
    ctx.move_to(95, -48)
    ctx.line_to(108, -135)
    ctx.curve_to(102, -152, 60, -154, -20, -154)
    ctx.line_to(-95, -154)
    ctx.curve_to(-120, -154, -132, -135, -145, -48)
    ctx.close_path()
    
    tower_grad = cairo.LinearGradient(0, -155, 0, -48)
    tower_grad.add_color_stop_rgb(0.0, *hex_rgb("#4C5C66"))
    tower_grad.add_color_stop_rgb(1.0, *hex_rgb("#242F35"))
    ctx.set_source(tower_grad)
    ctx.fill_preserve()
    ctx.set_source_rgb(*hex_rgb("#0E1418"))
    ctx.set_line_width(2.5)
    ctx.stroke()
    
    # Bridge Railing & Windshield with Lookout Silhouettes
    ctx.set_source_rgb(*hex_rgb("#1A2227"))
    ctx.rectangle(20, -166, 80, 12); ctx.fill()
    ctx.set_source_rgba(0.7, 0.85, 0.95, 0.45)
    ctx.rectangle(30, -164, 60, 8); ctx.fill()
    
    # Naval Bridge Lookouts (Officer of the Deck & Lookout with binoculars)
    for lx, ly, has_bino in [(42, -166, False), (75, -166, True)]:
        ctx.save()
        ctx.translate(lx, ly)
        # Head with cap
        ctx.set_source_rgb(*hex_rgb("#121A20"))
        ctx.arc(0, -18, 9, 0, 2 * math.pi); ctx.fill()
        rounded_rect(ctx, -10, -26, 20, 6, 2); ctx.fill()
        # Torso in pea coat
        rounded_rect(ctx, -12, -9, 24, 18, 4); ctx.fill()
        if has_bino:
            # Binoculars to eyes
            ctx.set_source_rgb(*hex_rgb("#2E3A42"))
            ctx.rectangle(6, -20, 12, 6); ctx.fill()
            ctx.set_source_rgb(*hex_rgb("#D4AF37"))
            ctx.arc(18, -17, 3.5, 0, 2 * math.pi); ctx.fill()
        ctx.restore()

    # Periscopes & Masts
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_source_rgb(*hex_rgb("#5A6B75"))
    ctx.set_line_width(4.5)
    ctx.move_to(35, -154); ctx.line_to(35, -235); ctx.stroke()
    ctx.move_to(-10, -154); ctx.line_to(-10, -260); ctx.stroke()
    ctx.move_to(-55, -154); ctx.line_to(-55, -215); ctx.stroke()
    
    # Bronze Lens Collars
    ctx.set_source_rgb(*hex_rgb("#CD7F32"))
    ctx.rectangle(31, -238, 8, 8); ctx.fill()
    ctx.rectangle(-14, -263, 8, 8); ctx.fill()

    # Hull Number "192"
    ctx.save()
    ctx.set_source_rgba(0.92, 0.95, 0.98, 0.9)
    ctx.select_font_face("Segoe UI", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(26)
    ctx.move_to(-35, -82)
    ctx.show_text("192")
    ctx.restore()

    # Deck Gun (3-inch / 50 cal)
    ctx.save()
    ctx.translate(210, -48)
    ctx.set_source_rgb(*hex_rgb("#1C2428"))
    ctx.arc(0, 0, 14, math.pi, 2 * math.pi); ctx.fill()
    ctx.set_source_rgb(*hex_rgb("#2A363D"))
    ctx.set_line_width(5.0)
    ctx.move_to(0, -6); ctx.line_to(65, -18); ctx.stroke()
    ctx.restore()

    # Twin Bronze Propellers & Rudder
    ctx.save()
    ctx.translate(-565, 5)
    ctx.set_source_rgb(*hex_rgb("#1E272C"))
    ctx.rectangle(-25, -20, 20, 42); ctx.fill()
    ctx.set_source_rgb(*hex_rgb("#C68A4C"))
    for blade_y in [-12, 12]:
        ctx.arc(-22, blade_y, 11, 0, 2 * math.pi); ctx.fill()
    ctx.restore()
    
    ctx.set_source_rgb(*hex_rgb("#182024"))
    ctx.arc(430, -12, 14, 0, 2 * math.pi); ctx.fill()

    ctx.restore()

# -------------------------------------------------------------
# Detailed Historical Character: Lieutenant Oliver Naquin
# -------------------------------------------------------------
def draw_officer_naquin(ctx, x, y, scale=1.0, expression="determined", t=0.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(scale, scale)
    
    # 1. Torso & Navy Officer Service Dress Blue Coat
    ctx.new_path()
    ctx.move_to(-110, 480)
    ctx.line_to(-85, 140)
    ctx.curve_to(-75, 75, 75, 75, 85, 140)
    ctx.line_to(110, 480)
    ctx.close_path()
    
    coat_grad = cairo.LinearGradient(0, 75, 0, 480)
    coat_grad.add_color_stop_rgb(0.0, *hex_rgb("#1A252E"))
    coat_grad.add_color_stop_rgb(1.0, *hex_rgb("#0E161C"))
    ctx.set_source(coat_grad); ctx.fill_preserve()
    ctx.set_source_rgb(*hex_rgb("#080D11")); ctx.set_line_width(3.0); ctx.stroke()
    
    # White Officer Shirt Collar & Navy Black Tie
    ctx.set_source_rgb(*hex_rgb("#EDEFEF"))
    ctx.move_to(-25, 95); ctx.line_to(0, 145); ctx.line_to(25, 95); ctx.close_path(); ctx.fill()
    ctx.set_source_rgb(*hex_rgb("#0A0E11"))
    ctx.move_to(-8, 120); ctx.line_to(8, 120); ctx.line_to(14, 210); ctx.line_to(-14, 210); ctx.close_path(); ctx.fill()
    
    # Double-Breasted Gold Eagle Buttons
    ctx.set_source_rgb(*hex_rgb("#D4AF37"))
    for by in [180, 240, 300]:
        ctx.arc(-35, by, 7.5, 0, 2 * math.pi); ctx.fill()
        ctx.arc(35, by, 7.5, 0, 2 * math.pi); ctx.fill()
        
    # Gold Lieutenant Shoulder Board Stripes
    for bx in [-75, 60]:
        ctx.set_source_rgb(*hex_rgb("#D4AF37"))
        ctx.rectangle(bx, 100, 18, 5); ctx.fill()
        ctx.rectangle(bx, 110, 18, 5); ctx.fill()

    # 2. Neck & Head
    ctx.set_source_rgb(*hex_rgb("#D6A784"))
    rounded_rect(ctx, -26, 45, 52, 65, 12); ctx.fill()
    
    ctx.new_path()
    ctx.move_to(-42, 45)
    ctx.curve_to(-48, 10, -45, -30, -38, -55)
    ctx.curve_to(-20, -75, 20, -75, 38, -55)
    ctx.curve_to(45, -30, 48, 10, 42, 45)
    ctx.curve_to(28, 62, -28, 62, -42, 45)
    ctx.close_path()
    ctx.set_source_rgb(*hex_rgb("#E0B492")); ctx.fill_preserve()
    ctx.set_source_rgb(*hex_rgb("#B88463")); ctx.set_line_width(2.0); ctx.stroke()
    
    # Eyes & Eyebrows
    if expression == "horror":
        ctx.set_source_rgb(*hex_rgb("#2A1F18")); ctx.set_line_width(3.8)
        ctx.move_to(-28, -20); ctx.line_to(-6, -12); ctx.stroke()
        ctx.move_to(28, -20); ctx.line_to(6, -12); ctx.stroke()
        ctx.set_source_rgb(1, 1, 1)
        rounded_rect(ctx, -24, -10, 16, 12, 4); ctx.fill()
        rounded_rect(ctx, 8, -10, 16, 12, 4); ctx.fill()
        ctx.set_source_rgb(*hex_rgb("#10151A"))
        ctx.arc(-16, -4, 4, 0, 2 * math.pi); ctx.fill()
        ctx.arc(16, -4, 4, 0, 2 * math.pi); ctx.fill()
        # Open shocked mouth
        ctx.set_source_rgb(*hex_rgb("#3D1414"))
        rounded_rect(ctx, -14, 18, 28, 18, 6); ctx.fill()
        ctx.set_source_rgb(*hex_rgb("#F0E6DF"))
        ctx.rectangle(-10, 18, 20, 5); ctx.fill()
    else:
        ctx.set_source_rgb(*hex_rgb("#2A1F18")); ctx.set_line_width(3.2)
        ctx.move_to(-26, -14); ctx.line_to(-8, -12); ctx.stroke()
        ctx.move_to(8, -12); ctx.line_to(26, -14); ctx.stroke()
        ctx.set_source_rgb(*hex_rgb("#1F2D38"))
        ctx.arc(-16, -5, 4.5, 0, 2 * math.pi); ctx.fill()
        ctx.arc(16, -5, 4.5, 0, 2 * math.pi); ctx.fill()
        ctx.set_source_rgb(*hex_rgb("#7A452B")); ctx.set_line_width(2.8)
        ctx.move_to(-14, 25); ctx.line_to(14, 25); ctx.stroke()

    # Firm Nose
    ctx.set_source_rgb(*hex_rgb("#B88463")); ctx.set_line_width(2.5)
    ctx.move_to(0, -10); ctx.line_to(4, 8); ctx.line_to(-5, 12); ctx.stroke()

    # 3. Naval Officer Visor Cap
    ctx.new_path()
    ctx.move_to(-75, -55)
    ctx.curve_to(-70, -105, 70, -105, 75, -55)
    ctx.close_path()
    ctx.set_source_rgb(*hex_rgb("#F0F2F5")); ctx.fill_preserve()
    ctx.set_source_rgb(*hex_rgb("#B8C0C8")); ctx.set_line_width(2.0); ctx.stroke()
    
    rounded_rect(ctx, -68, -55, 136, 26, 4)
    ctx.set_source_rgb(*hex_rgb("#101418")); ctx.fill()
    
    ctx.set_source_rgb(*hex_rgb("#D4AF37"))
    ctx.arc(0, -42, 10, 0, 2 * math.pi); ctx.fill()
    
    ctx.set_source_rgb(*hex_rgb("#D4AF37")); ctx.set_line_width(3.5)
    ctx.move_to(-65, -34); ctx.curve_to(-25, -28, 25, -28, 65, -34); ctx.stroke()
    ctx.arc(-64, -34, 4, 0, 2 * math.pi); ctx.fill()
    ctx.arc(64, -34, 4, 0, 2 * math.pi); ctx.fill()
    
    ctx.new_path()
    ctx.move_to(-68, -32)
    ctx.curve_to(-25, -16, 25, -16, 68, -32)
    ctx.curve_to(50, -40, -50, -40, -68, -32)
    ctx.close_path()
    ctx.set_source_rgb(*hex_rgb("#0A0D10")); ctx.fill()
    ctx.set_source_rgba(1, 1, 1, 0.35); ctx.set_line_width(2.0)
    ctx.move_to(-45, -28); ctx.curve_to(-15, -22, 15, -22, 45, -28); ctx.stroke()

    # Hand actions
    if expression == "horror":
        ctx.save()
        ctx.translate(-55, 10)
        ctx.set_source_rgb(*hex_rgb("#1A252E"))
        ctx.new_path()
        ctx.move_to(-35, 170); ctx.line_to(-52, 45); ctx.line_to(-15, 20); ctx.line_to(12, 145); ctx.close_path(); ctx.fill()
        ctx.set_source_rgb(*hex_rgb("#D6A784"))
        rounded_rect(ctx, -5, 5, 38, 42, 12); ctx.fill()
        ctx.set_source_rgb(*hex_rgb("#0A0D10"))
        rounded_rect(ctx, -14, -38, 44, 115, 18); ctx.fill()
        ctx.set_source_rgb(*hex_rgb("#1A1A1A")); ctx.set_line_width(4.0)
        ctx.move_to(8, 77); ctx.curve_to(25, 140, 65, 220, 125, 280); ctx.stroke()
        ctx.restore()
    else:
        ctx.save()
        ctx.translate(-85, 260)
        ctx.set_source_rgb(*hex_rgb("#1A252E"))
        rounded_rect(ctx, -24, -40, 48, 50, 10); ctx.fill()
        ctx.set_source_rgb(*hex_rgb("#D6A784"))
        rounded_rect(ctx, -20, 5, 40, 35, 12); ctx.fill()
        ctx.set_source_rgb(*hex_rgb("#C8D1D8"))
        ctx.arc(0, 22, 18, 0, 2 * math.pi); ctx.fill()
        ctx.set_source_rgb(*hex_rgb("#FFFFFF"))
        ctx.arc(0, 22, 14, 0, 2 * math.pi); ctx.fill()
        ctx.set_source_rgb(*hex_rgb("#1A1A1A")); ctx.set_line_width(1.8)
        ctx.move_to(0, 22); ctx.line_to(6, 15); ctx.stroke()
        ctx.move_to(0, 22); ctx.line_to(-2, 28); ctx.stroke()
        ctx.restore()

    ctx.restore()

# -------------------------------------------------------------
# Detailed Watertight Bulkhead Door Rig (Scene 13)
# -------------------------------------------------------------
def draw_watertight_door_detailed(ctx, t, water_pct=0.3):
    st = t - 77.0
    
    # 1. Outer Heavy Steel Bulkhead Wall
    ctx.set_source_rgb(*hex_rgb("#141C21"))
    ctx.rectangle(0, 0, W, H); ctx.fill()
    
    # Structural Rivets
    ctx.set_source_rgb(*hex_rgb("#0D1317"))
    ctx.set_line_width(3.0)
    ctx.move_to(320, 0); ctx.line_to(320, H); ctx.stroke()
    ctx.move_to(1600, 0); ctx.line_to(1600, H); ctx.stroke()
    for ry in range(40, H, 60):
        ctx.arc(320, ry, 5, 0, 2 * math.pi); ctx.fill()
        ctx.arc(1600, ry, 5, 0, 2 * math.pi); ctx.fill()

    # 2. Oval Watertight Door Portal Aperture
    dw, dh = 720, 880
    dx, dy = (W - dw) / 2 + 60, (H - dh) / 2
    
    # Door Open Frame Cutout
    ctx.save()
    rounded_rect(ctx, dx, dy, dw, dh, 220)
    ctx.clip()
    
    # Flooded Aft Compartment in darkness beyond
    ctx.set_source_rgb(*hex_rgb("#050B0E"))
    ctx.rectangle(dx, dy, dw, dh); ctx.fill()
    
    # Rising Ice Water in the Flooded Compartment
    water_h = dh * min(1.0, 0.22 + water_pct * 0.78)
    wy = dy + dh - water_h
    
    water_pat = cairo.LinearGradient(W/2, wy, W/2, dy + dh)
    water_pat.add_color_stop_rgba(0.0, 0.12, 0.35, 0.48, 0.95)
    water_pat.add_color_stop_rgba(0.5, 0.06, 0.20, 0.30, 0.98)
    water_pat.add_color_stop_rgba(1.0, 0.02, 0.08, 0.14, 1.0)
    
    ctx.new_path()
    ctx.move_to(dx, dy + dh)
    ctx.line_to(dx, wy)
    for x in range(int(dx), int(dx + dw + 20), 20):
        wave_y = wy + 8.0 * math.sin((x + st * 150) * 0.02 + st * 5.0)
        ctx.line_to(x, wave_y)
    ctx.line_to(dx + dw, dy + dh)
    ctx.close_path()
    ctx.set_source(water_pat); ctx.fill()
    
    ctx.set_source_rgba(0.75, 0.90, 0.98, 0.85)
    for i in range(35):
        sx = dx + (i * 22 + int(st * 40)) % int(dw)
        sy = wy + math.sin(i * 1.5 + st * 8.0) * 16 - 8
        ctx.arc(sx, sy, 5 + (i % 4) * 2, 0, 2 * math.pi); ctx.fill()
        
    ctx.restore() # End clip
    
    # 3. Heavy Cast Steel Frame Coaming
    rounded_rect(ctx, dx, dy, dw, dh, 220)
    ctx.set_source_rgb(*hex_rgb("#32404A")); ctx.set_line_width(38.0); ctx.stroke()
    rounded_rect(ctx, dx, dy, dw, dh, 220)
    ctx.set_source_rgb(*hex_rgb("#182126")); ctx.set_line_width(12.0); ctx.stroke()
    
    # Rubber Gasket
    rounded_rect(ctx, dx + 6, dy + 6, dw - 12, dh - 12, 215)
    ctx.set_source_rgb(*hex_rgb("#090D0F")); ctx.set_line_width(6.0); ctx.stroke()

    # 4. Eight Bronze Locking Dogs
    for d_i in range(8):
        ang = d_i * (math.pi / 4.0) + math.pi / 8.0
        cx = (dx + dw/2) + (dw / 2) * math.cos(ang)
        cy = (dy + dh/2) + (dh / 2) * math.sin(ang)
        ctx.save()
        ctx.translate(cx, cy)
        ctx.rotate(ang)
        ctx.set_source_rgb(*hex_rgb("#B8860B"))
        rounded_rect(ctx, -15, -30, 30, 60, 8); ctx.fill()
        ctx.set_source_rgb(*hex_rgb("#4A3708"))
        ctx.arc(0, 0, 8, 0, 2 * math.pi); ctx.fill()
        ctx.restore()

    # 5. Open Watertight Door Panel (Swinging into frame from left)
    # Heavy 3-inch thick steel door slab
    door_swing_x = dx - 140
    ctx.save()
    rounded_rect(ctx, door_swing_x - 180, dy + 30, 240, dh - 60, 110)
    door_plate_grad = cairo.LinearGradient(door_swing_x - 180, 0, door_swing_x + 60, 0)
    door_plate_grad.add_color_stop_rgb(0.0, *hex_rgb("#1E272D"))
    door_plate_grad.add_color_stop_rgb(0.7, *hex_rgb("#3A4852"))
    door_plate_grad.add_color_stop_rgb(1.0, *hex_rgb("#141B1F"))
    ctx.set_source(door_plate_grad); ctx.fill_preserve()
    ctx.set_source_rgb(*hex_rgb("#0D1316")); ctx.set_line_width(6.0); ctx.stroke()
    
    # Door Hinges
    for hy in [dy + 160, dy + dh - 200]:
        ctx.set_source_rgb(*hex_rgb("#556772"))
        rounded_rect(ctx, door_swing_x + 30, hy, 45, 60, 8); ctx.fill()
    ctx.restore()

    # 6. Door Locking Handwheel mounted on the Door Panel
    ctx.save()
    ctx.translate(door_swing_x - 20, H / 2 + 40)
    
    # Cast Iron Wheel
    ctx.set_source_rgb(*hex_rgb("#4E5E68"))
    ctx.arc(0, 0, 125, 0, 2 * math.pi); ctx.set_line_width(22.0); ctx.stroke()
    ctx.set_line_width(16.0)
    ctx.move_to(-125, 0); ctx.line_to(125, 0); ctx.stroke()
    ctx.move_to(0, -125); ctx.line_to(0, 125); ctx.stroke()
    ctx.arc(0, 0, 30, 0, 2 * math.pi); ctx.fill()
    
    # Sailor's Forearm (Rolled-up Chambray Shirt)
    ctx.set_source_rgb(*hex_rgb("#324A5E"))
    ctx.new_path()
    ctx.move_to(-320, 180); ctx.line_to(-160, 90); ctx.line_to(-175, 10); ctx.line_to(-340, 75); ctx.close_path(); ctx.fill()
    
    # Muscular Forearm
    ctx.set_source_rgb(*hex_rgb("#D6A784"))
    ctx.new_path()
    ctx.move_to(-160, 90); ctx.line_to(-40, 50); ctx.line_to(-50, -10); ctx.line_to(-175, 10); ctx.close_path(); ctx.fill()
    
    # White-knuckle hand gripping wheel rim
    hand_tremor = math.sin(st * 45.0) * 2.5
    ctx.translate(hand_tremor, hand_tremor)
    ctx.set_source_rgb(*hex_rgb("#D6A784"))
    rounded_rect(ctx, -70, -40, 105, 80, 24); ctx.fill()
    ctx.set_source_rgb(*hex_rgb("#B88463")); ctx.set_line_width(4.5)
    for fy in [-20, 2, 24]:
        ctx.move_to(-25, fy); ctx.line_to(25, fy); ctx.stroke()
    ctx.restore()

    # Red Emergency Lighting Strobe
    pat = cairo.RadialGradient(W / 2, 120, 50, W / 2, 120, 850)
    pat.add_color_stop_rgba(0.0, 1.0, 0.15, 0.1, 0.35)
    pat.add_color_stop_rgba(1.0, 0.0, 0.0, 0.0, 0.0)
    ctx.rectangle(0, 0, W, H); ctx.set_source(pat); ctx.fill()

print("components.py updated with Vietnamese support and enhanced assets")
