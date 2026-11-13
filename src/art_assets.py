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

# =============================================================
# HIGH-END ARTISTIC ASSET: Lieutenant Oliver Naquin (Full Portrait)
# =============================================================
def draw_naquin_cinematic(ctx, x, y, scale=1.0, expression="determined", t=0.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(scale, scale)
    
    # 1. Subtle Chiaroscuro Rim Light
    rim_color = (0.85, 0.18, 0.12, 0.35) if expression == "horror" else (0.45, 0.70, 0.88, 0.22)
    pat_rim = cairo.RadialGradient(0, 150, 80, 0, 150, 380)
    pat_rim.add_color_stop_rgba(0.0, *rim_color)
    pat_rim.add_color_stop_rgba(1.0, rim_color[0], rim_color[1], rim_color[2], 0.0)
    ctx.arc(0, 150, 380, 0, 2 * math.pi); ctx.set_source(pat_rim); ctx.fill()

    # 2. Service Dress Blue Coat (Tailored wool)
    ctx.new_path()
    ctx.move_to(-125, 480)
    ctx.curve_to(-115, 320, -95, 160, -90, 135)
    ctx.curve_to(-80, 75, -45, 68, 0, 72)
    ctx.curve_to(45, 68, 80, 75, 90, 135)
    ctx.curve_to(95, 160, 115, 320, 125, 480)
    ctx.close_path()
    
    coat_grad = cairo.LinearGradient(0, 65, 0, 480)
    coat_grad.add_color_stop_rgb(0.0, *hex_rgb("#1C2730"))
    coat_grad.add_color_stop_rgb(0.4, *hex_rgb("#141D24"))
    coat_grad.add_color_stop_rgb(1.0, *hex_rgb("#0A0F13"))
    ctx.set_source(coat_grad); ctx.fill_preserve()
    ctx.set_source_rgb(*hex_rgb("#060A0D")); ctx.set_line_width(2.8); ctx.stroke()
    
    # Coat Lapels & Shading
    ctx.new_path()
    ctx.move_to(-45, 78); ctx.line_to(-65, 180); ctx.line_to(-18, 260); ctx.line_to(0, 140); ctx.close_path()
    ctx.set_source_rgb(*hex_rgb("#162028")); ctx.fill()
    ctx.new_path()
    ctx.move_to(45, 78); ctx.line_to(65, 180); ctx.line_to(18, 260); ctx.line_to(0, 140); ctx.close_path()
    ctx.set_source_rgb(*hex_rgb("#121A21")); ctx.fill()
    
    # White Officer Shirt Collar & Navy Black Tie
    ctx.new_path()
    ctx.move_to(-28, 92); ctx.line_to(0, 145); ctx.line_to(28, 92); ctx.close_path()
    ctx.set_source_rgb(*hex_rgb("#E8ECF0")); ctx.fill()
    
    ctx.set_source_rgb(*hex_rgb("#090D10"))
    ctx.rectangle(-8, 122, 16, 20); ctx.fill()
    ctx.new_path()
    ctx.move_to(-10, 142); ctx.line_to(10, 142); ctx.line_to(14, 250); ctx.line_to(-14, 250); ctx.close_path(); ctx.fill()

    # Double-Breasted Naval Gold Buttons
    for by in [175, 235, 295]:
        for bx in [-38, 38]:
            ctx.set_source_rgb(*hex_rgb("#997A15"))
            ctx.arc(bx, by, 9, 0, 2 * math.pi); ctx.fill()
            ctx.set_source_rgb(*hex_rgb("#D4AF37"))
            ctx.arc(bx, by, 7.5, 0, 2 * math.pi); ctx.fill()
            ctx.set_source_rgb(*hex_rgb("#FFF2A3"))
            ctx.arc(bx - 2, by - 2, 2.5, 0, 2 * math.pi); ctx.fill()

    # Lieutenant Rank Lace (Gold Braids)
    for bx in [-78, 58]:
        for ly in [102, 114]:
            ctx.set_source_rgb(*hex_rgb("#D4AF37"))
            ctx.rectangle(bx, ly, 20, 6); ctx.fill()
            ctx.set_source_rgb(*hex_rgb("#7A5F10"))
            ctx.rectangle(bx, ly + 4, 20, 2); ctx.fill()

    # 3. Neck & Chiseled Jaw
    ctx.new_path()
    ctx.move_to(-25, 48); ctx.line_to(-22, 110); ctx.line_to(22, 110); ctx.line_to(25, 48); ctx.close_path()
    neck_grad = cairo.LinearGradient(-25, 0, 25, 0)
    neck_grad.add_color_stop_rgb(0.0, *hex_rgb("#B88463"))
    neck_grad.add_color_stop_rgb(0.5, *hex_rgb("#D6A784"))
    neck_grad.add_color_stop_rgb(1.0, *hex_rgb("#A87455"))
    ctx.set_source(neck_grad); ctx.fill()
    
    # Head & Officer Jawline
    ctx.new_path()
    ctx.move_to(-44, 45)
    ctx.curve_to(-50, 12, -46, -28, -38, -55)
    ctx.curve_to(-20, -78, 20, -78, 38, -55)
    ctx.curve_to(46, -28, 50, 12, 44, 45)
    ctx.curve_to(28, 64, -28, 64, -44, 45)
    ctx.close_path()
    
    face_grad = cairo.LinearGradient(0, -60, 0, 60)
    face_grad.add_color_stop_rgb(0.0, *hex_rgb("#F0C4A4"))
    face_grad.add_color_stop_rgb(0.6, *hex_rgb("#E0B492"))
    face_grad.add_color_stop_rgb(1.0, *hex_rgb("#C69371"))
    ctx.set_source(face_grad); ctx.fill_preserve()
    ctx.set_source_rgb(*hex_rgb("#966343")); ctx.set_line_width(1.8); ctx.stroke()
    
    # Cheek Shading
    ctx.set_source_rgba(0.5, 0.25, 0.15, 0.18)
    ctx.arc(0, 52, 16, 0, math.pi); ctx.fill()
    
    # Nose
    ctx.new_path()
    ctx.move_to(-2, -14); ctx.line_to(5, 8); ctx.line_to(-6, 14); ctx.close_path()
    ctx.set_source_rgb(*hex_rgb("#D69F7A")); ctx.fill_preserve()
    ctx.set_source_rgb(*hex_rgb("#A86E47")); ctx.set_line_width(1.8); ctx.stroke()
    ctx.arc(4, 12, 2.5, 0, 2 * math.pi); ctx.fill()

    # Eyes & Mouth
    if expression == "horror":
        ctx.set_source_rgb(*hex_rgb("#241A12")); ctx.set_line_width(4.0)
        ctx.move_to(-30, -22); ctx.line_to(-6, -14); ctx.stroke()
        ctx.move_to(30, -22); ctx.line_to(6, -14); ctx.stroke()
        
        ctx.set_source_rgb(1, 1, 1)
        rounded_rect(ctx, -25, -12, 18, 14, 5); ctx.fill()
        rounded_rect(ctx, 7, -12, 18, 14, 5); ctx.fill()
        
        ctx.set_source_rgb(*hex_rgb("#1B2A36"))
        ctx.arc(-16, -5, 5, 0, 2 * math.pi); ctx.fill()
        ctx.arc(16, -5, 5, 0, 2 * math.pi); ctx.fill()
        ctx.set_source_rgb(1, 1, 1)
        ctx.arc(-18, -7, 2, 0, 2 * math.pi); ctx.fill()
        ctx.arc(14, -7, 2, 0, 2 * math.pi); ctx.fill()
        
        # Open Gasping / Shouting Mouth
        ctx.set_source_rgb(*hex_rgb("#301010"))
        rounded_rect(ctx, -16, 20, 32, 22, 8); ctx.fill_preserve()
        ctx.set_source_rgb(*hex_rgb("#150505")); ctx.set_line_width(2.0); ctx.stroke()
        ctx.set_source_rgb(*hex_rgb("#FAF5ED"))
        ctx.rectangle(-12, 20, 24, 6); ctx.fill()
        ctx.set_source_rgb(*hex_rgb("#963838"))
        ctx.arc(0, 38, 9, math.pi, 2 * math.pi); ctx.fill()
        
        # Cold sweat
        ctx.set_source_rgba(0.9, 0.95, 1.0, 0.75)
        ctx.arc(28, 6, 2.5, 0, 2 * math.pi); ctx.fill()
    else:
        ctx.set_source_rgb(*hex_rgb("#241A12")); ctx.set_line_width(3.4)
        ctx.move_to(-28, -16); ctx.line_to(-8, -13); ctx.stroke()
        ctx.move_to(8, -13); ctx.line_to(28, -16); ctx.stroke()
        
        ctx.set_source_rgb(1, 1, 1)
        rounded_rect(ctx, -24, -8, 16, 9, 3); ctx.fill()
        rounded_rect(ctx, 8, -8, 16, 9, 3); ctx.fill()
        ctx.set_source_rgb(*hex_rgb("#233544"))
        ctx.arc(-16, -4, 4.2, 0, 2 * math.pi); ctx.fill()
        ctx.arc(16, -4, 4.2, 0, 2 * math.pi); ctx.fill()
        ctx.set_source_rgb(1, 1, 1)
        ctx.arc(-18, -5, 1.5, 0, 2 * math.pi); ctx.fill()
        ctx.arc(14, -5, 1.5, 0, 2 * math.pi); ctx.fill()
        
        ctx.set_source_rgb(*hex_rgb("#854C34")); ctx.set_line_width(2.8)
        ctx.move_to(-14, 25); ctx.line_to(14, 25); ctx.stroke()
        ctx.set_source_rgb(*hex_rgb("#A66B50"))
        ctx.arc(0, 28, 8, 0, math.pi); ctx.fill()

    # 4. US Navy Officer Combination Cover
    ctx.new_path()
    ctx.move_to(-78, -52)
    ctx.curve_to(-72, -108, 72, -108, 78, -52)
    ctx.close_path()
    crown_grad = cairo.LinearGradient(0, -108, 0, -52)
    crown_grad.add_color_stop_rgb(0.0, *hex_rgb("#FFFFFF"))
    crown_grad.add_color_stop_rgb(0.7, *hex_rgb("#E8ECF0"))
    crown_grad.add_color_stop_rgb(1.0, *hex_rgb("#CCD5DC"))
    ctx.set_source(crown_grad); ctx.fill_preserve()
    ctx.set_source_rgb(*hex_rgb("#96A4AF")); ctx.set_line_width(2.0); ctx.stroke()
    
    rounded_rect(ctx, -70, -52, 140, 26, 4)
    ctx.set_source_rgb(*hex_rgb("#101418")); ctx.fill()
    
    ctx.set_source_rgb(*hex_rgb("#D4AF37"))
    ctx.arc(0, -39, 11, 0, 2 * math.pi); ctx.fill()
    ctx.set_source_rgb(*hex_rgb("#FFF2A3"))
    ctx.arc(0, -41, 6, 0, 2 * math.pi); ctx.fill()
    
    ctx.set_source_rgb(*hex_rgb("#D4AF37")); ctx.set_line_width(3.8)
    ctx.move_to(-66, -32); ctx.curve_to(-25, -26, 25, -26, 66, -32); ctx.stroke()
    ctx.arc(-65, -32, 4.5, 0, 2 * math.pi); ctx.fill()
    ctx.arc(65, -32, 4.5, 0, 2 * math.pi); ctx.fill()
    
    ctx.new_path()
    ctx.move_to(-70, -30)
    ctx.curve_to(-25, -14, 25, -14, 70, -30)
    ctx.curve_to(50, -38, -50, -38, -70, -30)
    ctx.close_path()
    visor_grad = cairo.LinearGradient(0, -35, 0, -14)
    visor_grad.add_color_stop_rgb(0.0, *hex_rgb("#1A2026"))
    visor_grad.add_color_stop_rgb(0.7, *hex_rgb("#0A0D10"))
    visor_grad.add_color_stop_rgb(1.0, *hex_rgb("#040608"))
    ctx.set_source(visor_grad); ctx.fill()
    
    ctx.set_source_rgba(1, 1, 1, 0.45); ctx.set_line_width(2.2)
    ctx.move_to(-48, -26); ctx.curve_to(-15, -20, 15, -20, 48, -26); ctx.stroke()
    
    ctx.set_source_rgba(0, 0, 0, 0.28)
    ctx.arc(0, -20, 36, 0, math.pi); ctx.fill()

    # 5. Hands: Phone or Pocket Watch
    if expression == "horror":
        ctx.save()
        ctx.translate(-55, 10)
        # Smooth anatomical curved arm
        ctx.new_path()
        ctx.move_to(-38, 200)
        ctx.curve_to(-58, 120, -68, 55, -45, 25)
        ctx.line_to(-16, 20)
        ctx.curve_to(-25, 60, -15, 120, 14, 180)
        ctx.close_path()
        ctx.set_source_rgb(*hex_rgb("#162028")); ctx.fill_preserve()
        ctx.set_source_rgb(*hex_rgb("#0A0E12")); ctx.set_line_width(2.5); ctx.stroke()
        
        # Hand gripping receiver
        ctx.set_source_rgb(*hex_rgb("#D6A784"))
        rounded_rect(ctx, -12, 10, 42, 44, 12); ctx.fill()
        ctx.set_source_rgb(*hex_rgb("#A87455")); ctx.set_line_width(2.5)
        for ky in [20, 32, 44]:
            ctx.move_to(-10, ky); ctx.line_to(14, ky); ctx.stroke()
            
        # Sound-Powered Handset
        ctx.set_source_rgb(*hex_rgb("#0E1215"))
        rounded_rect(ctx, -20, -35, 48, 120, 18); ctx.fill_preserve()
        ctx.set_source_rgb(*hex_rgb("#232D35")); ctx.set_line_width(2.5); ctx.stroke()
        ctx.arc(4, -20, 22, 0, 2 * math.pi); ctx.fill()
        ctx.arc(4, 70, 22, 0, 2 * math.pi); ctx.fill()
        
        # Coiled cable
        ctx.set_source_rgb(*hex_rgb("#14181B")); ctx.set_line_width(4.5)
        ctx.move_to(4, 90); ctx.curve_to(20, 150, 65, 230, 125, 290); ctx.stroke()
        ctx.restore()
    else:
        ctx.save()
        ctx.translate(-85, 260)
        ctx.set_source_rgb(*hex_rgb("#162028"))
        rounded_rect(ctx, -26, -45, 52, 55, 12); ctx.fill()
        ctx.set_source_rgb(*hex_rgb("#D4AF37"))
        ctx.rectangle(-26, -20, 52, 5); ctx.fill()
        ctx.rectangle(-26, -10, 52, 5); ctx.fill()
        
        ctx.set_source_rgb(*hex_rgb("#D6A784"))
        rounded_rect(ctx, -22, 6, 44, 38, 14); ctx.fill()
        ctx.set_source_rgb(*hex_rgb("#B88463")); ctx.set_line_width(2.2)
        ctx.move_to(-12, 20); ctx.line_to(12, 20); ctx.stroke()
        
        ctx.set_source_rgb(*hex_rgb("#A8B5BF"))
        ctx.arc(0, 24, 20, 0, 2 * math.pi); ctx.fill()
        ctx.set_source_rgb(*hex_rgb("#E8F0F5"))
        ctx.arc(0, 24, 16, 0, 2 * math.pi); ctx.fill()
        ctx.set_source_rgb(*hex_rgb("#101518")); ctx.set_line_width(1.8)
        ctx.move_to(0, 24); ctx.line_to(7, 16); ctx.stroke()
        ctx.move_to(0, 24); ctx.line_to(-3, 30); ctx.stroke()
        ctx.restore()

    ctx.restore()

# =============================================================
# HIGH-END ARTISTIC ASSET: Control Room Machinery & Periscope Well
# =============================================================
def draw_control_room_background(ctx, t, emergency_red=False):
    bg = cairo.LinearGradient(0, 0, W, H)
    if emergency_red:
        bg.add_color_stop_rgb(0.0, *hex_rgb("#230A0A"))
        bg.add_color_stop_rgb(0.5, *hex_rgb("#180707"))
        bg.add_color_stop_rgb(1.0, *hex_rgb("#0D0303"))
    else:
        bg.add_color_stop_rgb(0.0, *hex_rgb("#18232B"))
        bg.add_color_stop_rgb(0.4, *hex_rgb("#111A20"))
        bg.add_color_stop_rgb(1.0, *hex_rgb("#090D10"))
    ctx.rectangle(0, 0, W, H); ctx.set_source(bg); ctx.fill()

    # Structural T-Frames & Pressure Hull Ribs
    rib_col = "#2A0D0D" if emergency_red else "#22313B"
    ctx.set_source_rgb(*hex_rgb(rib_col)); ctx.set_line_width(14.0)
    for rx in range(160, W + 100, 320):
        ctx.move_to(rx, 0); ctx.line_to(rx, H); ctx.stroke()
        ctx.set_source_rgb(0.05, 0.05, 0.05)
        for ry in range(40, H, 55):
            ctx.arc(rx, ry, 4.5, 0, 2 * math.pi); ctx.fill()
        ctx.set_source_rgb(*hex_rgb(rib_col))

    # Overhead Pipe Runs
    pipes = [
        (110, 34, "#B87333", "#7A4315"),
        (165, 26, "#CD7F32", "#8A541E"),
        (215, 20, "#7E96A0", "#4B5F68"),
        (260, 24, "#A0522D", "#5C2B14"),
    ]
    for py, pw, c_light, c_dark in pipes:
        p_grad = cairo.LinearGradient(0, py - pw/2, 0, py + pw/2)
        p_grad.add_color_stop_rgb(0.0, *hex_rgb(c_light))
        p_grad.add_color_stop_rgb(0.6, *hex_rgb(c_dark))
        p_grad.add_color_stop_rgb(1.0, 0.05, 0.05, 0.05)
        ctx.set_source(p_grad); ctx.set_line_width(pw)
        ctx.move_to(0, py); ctx.line_to(W, py); ctx.stroke()
        
        for fx in range(280, W, 420):
            ctx.set_source_rgb(0.12, 0.15, 0.18)
            rounded_rect(ctx, fx - 22, py - pw/2 - 6, 44, pw + 12, 6); ctx.fill()
            ctx.set_source_rgb(*hex_rgb("#A83232" if fx % 2 == 0 else "#D4AF37"))
            ctx.arc(fx, py, 26, 0, 2 * math.pi); ctx.set_line_width(7.0); ctx.stroke()
            ctx.move_to(fx - 26, py); ctx.line_to(fx + 26, py); ctx.stroke()
            ctx.move_to(fx, py - 26); ctx.line_to(fx, py + 26); ctx.stroke()

    # Periscope Well Column
    ctx.save()
    rounded_rect(ctx, 860, 0, 200, 380, 20)
    peri_grad = cairo.LinearGradient(860, 0, 1060, 0)
    peri_grad.add_color_stop_rgb(0.0, *hex_rgb("#18232B"))
    peri_grad.add_color_stop_rgb(0.5, *hex_rgb("#30424E"))
    peri_grad.add_color_stop_rgb(1.0, *hex_rgb("#121A20"))
    ctx.set_source(peri_grad); ctx.fill()
    ctx.set_source_rgb(*hex_rgb("#090D10")); ctx.set_line_width(4.0); ctx.stroke()
    ctx.set_source_rgb(*hex_rgb("#D4AF37")); ctx.set_line_width(12.0)
    ctx.move_to(830, 260); ctx.line_to(880, 260); ctx.stroke()
    ctx.move_to(1040, 260); ctx.line_to(1090, 260); ctx.stroke()
    ctx.restore()

    # Bulkhead Lanterns
    for lx in [360, 1100, 1660]:
        ctx.set_source_rgb(*hex_rgb("#CD7F32"))
        ctx.arc(lx, 140, 24, 0, math.pi); ctx.fill()
        pat = cairo.RadialGradient(lx, 145, 15, lx, 145, 450)
        if emergency_red:
            pat.add_color_stop_rgba(0.0, 1.0, 0.2, 0.1, 0.55)
            pat.add_color_stop_rgba(1.0, 0.2, 0.0, 0.0, 0.0)
        else:
            pat.add_color_stop_rgba(0.0, 1.0, 0.90, 0.58, 0.42)
            pat.add_color_stop_rgba(1.0, 0.15, 0.12, 0.04, 0.0)
        ctx.rectangle(0, 0, W, H); ctx.set_source(pat); ctx.fill()

# =============================================================
# HIGH-END ARTISTIC ASSET: Sound-Powered Telephone Station (Scene 10)
# =============================================================
def draw_telephone_station(ctx, x, y, vibe=0.0):
    ctx.save()
    ctx.translate(x + vibe, y)
    
    # Cast Iron Wall Box
    rounded_rect(ctx, -150, -230, 300, 460, 22)
    box_grad = cairo.LinearGradient(-150, 0, 150, 0)
    box_grad.add_color_stop_rgb(0.0, *hex_rgb("#1C252B"))
    box_grad.add_color_stop_rgb(0.5, *hex_rgb("#2E3D46"))
    box_grad.add_color_stop_rgb(1.0, *hex_rgb("#141B20"))
    ctx.set_source(box_grad); ctx.fill_preserve()
    ctx.set_source_rgb(*hex_rgb("#0C1215")); ctx.set_line_width(6.0); ctx.stroke()
    
    # Corner Mounting Flange Screws
    for mx, my in [(-130, -210), (130, -210), (-130, 210), (130, 210)]:
        ctx.set_source_rgb(*hex_rgb("#4C5C66"))
        ctx.arc(mx, my, 8, 0, 2 * math.pi); ctx.fill()
        ctx.set_source_rgb(0.1, 0.1, 0.1)
        ctx.arc(mx, my, 4, 0, 2 * math.pi); ctx.fill()

    # Twin Brass Ringer Bells on Top
    for bell_x in [-75, 75]:
        b_grad = cairo.LinearGradient(bell_x - 45, -280, bell_x + 45, -235)
        b_grad.add_color_stop_rgb(0.0, *hex_rgb("#E5A65D"))
        b_grad.add_color_stop_rgb(0.6, *hex_rgb("#CD7F32"))
        b_grad.add_color_stop_rgb(1.0, *hex_rgb("#7A4515"))
        ctx.set_source(b_grad); ctx.arc(bell_x, -245, 48, math.pi, 2 * math.pi); ctx.fill()
        ctx.set_source_rgb(0.1, 0.1, 0.1)
        ctx.arc(bell_x, -245, 12, 0, 2 * math.pi); ctx.fill()
        
    # Clapper striker between bells
    striker_x = math.sin(vibe * 12) * 14
    ctx.set_source_rgb(*hex_rgb("#B8860B"))
    ctx.arc(striker_x, -260, 9, 0, 2 * math.pi); ctx.fill()

    # Engraved Brass Navy Instruction Plate
    ctx.set_source_rgb(*hex_rgb("#B8860B"))
    rounded_rect(ctx, -110, -140, 220, 80, 8); ctx.fill_preserve()
    ctx.set_source_rgb(*hex_rgb("#664903")); ctx.set_line_width(3.0); ctx.stroke()
    ctx.set_source_rgb(0.1, 0.1, 0.1)
    ctx.select_font_face("Segoe UI", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(15); ctx.move_to(-85, -112); ctx.show_text("U.S. NAVY SOUND-POWERED")
    ctx.set_font_size(14); ctx.move_to(-75, -88); ctx.show_text("TELEPHONE  •  TYPE A")

    # Rotary Station Selector Switch (Brass dial)
    ctx.set_source_rgb(*hex_rgb("#CD7F32"))
    ctx.arc(0, 45, 60, 0, 2 * math.pi); ctx.fill()
    ctx.set_source_rgb(*hex_rgb("#182228"))
    ctx.arc(0, 45, 48, 0, 2 * math.pi); ctx.fill()
    # Pointer knob
    ctx.set_source_rgb(*hex_rgb("#B8860B"))
    ctx.rectangle(-8, 5, 16, 50); ctx.fill()

    # Hand Generator Crank on Right Side
    ctx.set_source_rgb(*hex_rgb("#556772"))
    ctx.rectangle(150, -20, 25, 20); ctx.fill()
    ctx.set_source_rgb(*hex_rgb("#8D9FA8"))
    ctx.rectangle(175, -20, 15, 90); ctx.fill()
    ctx.set_source_rgb(*hex_rgb("#23180D"))
    rounded_rect(ctx, 168, 65, 30, 40, 8); ctx.fill()

    # Empty Cradle Fork on Left
    ctx.set_source_rgb(*hex_rgb("#3A4750"))
    rounded_rect(ctx, -180, -60, 30, 80, 10); ctx.fill()

    ctx.restore()

# =============================================================
# HIGH-END ARTISTIC ASSET: Flooded Engine Room & Machinist (Scene 9)
# =============================================================
def draw_engine_room_flood(ctx, t):
    st = t - 57.5
    shake_x = math.sin(st * 90) * 16.0
    shake_y = math.cos(st * 110) * 14.0
    
    ctx.save()
    ctx.translate(shake_x, shake_y)
    
    # 1. Base Compartment
    ctx.set_source_rgb(*hex_rgb("#061016")); ctx.rectangle(0, 0, W, H); ctx.fill()
    
    # Massive Fairbanks-Morse Opposed-Piston Diesel Engines (Left & Right)
    for eng_x, flip in [(220, False), (1700, True)]:
        ctx.save()
        ctx.translate(eng_x, 620)
        if flip: ctx.scale(-1, 1)
        
        rounded_rect(ctx, -190, -320, 380, 640, 24)
        eng_grad = cairo.LinearGradient(-190, 0, 190, 0)
        eng_grad.add_color_stop_rgb(0.0, *hex_rgb("#1C2730"))
        eng_grad.add_color_stop_rgb(0.5, *hex_rgb("#2E3E4C"))
        eng_grad.add_color_stop_rgb(1.0, *hex_rgb("#121A20"))
        ctx.set_source(eng_grad); ctx.fill()
        
        for cy in range(-280, 240, 95):
            rounded_rect(ctx, -160, cy, 320, 68, 14)
            ctx.set_source_rgb(*hex_rgb("#425563")); ctx.fill_preserve()
            ctx.set_source_rgb(*hex_rgb("#0D1317")); ctx.set_line_width(2.5); ctx.stroke()
            ctx.set_source_rgb(*hex_rgb("#D4AF37"))
            ctx.arc(80, cy + 34, 10, 0, 2 * math.pi); ctx.fill()
            
        ctx.restore()

    # 2. Catwalk Steel Grating with diamond mesh & Stanchions
    ctx.set_source_rgb(*hex_rgb("#41535F")); ctx.set_line_width(14.0)
    ctx.move_to(360, 780); ctx.line_to(1560, 780); ctx.stroke()
    for rx in range(420, 1520, 160):
        ctx.move_to(rx, 780); ctx.line_to(rx, H); ctx.stroke()

    # 3. Blinding Electrical Arc Flash
    is_arc = (int(st * 18) % 3 == 0)
    if is_arc:
        ctx.set_source_rgba(0.8, 0.92, 1.0, 0.5)
        ctx.rectangle(0, 0, W, H); ctx.fill()

    # 4. Immense Solid Column of Freezing Atlantic Water
    col_x = 960
    col_w = 540 + st * 180
    water_grad = cairo.LinearGradient(col_x, 0, col_x, H)
    water_grad.add_color_stop_rgba(0.0, 0.35, 0.78, 0.98, 0.95)
    water_grad.add_color_stop_rgba(0.4, 0.15, 0.48, 0.68, 0.98)
    water_grad.add_color_stop_rgba(1.0, 0.04, 0.18, 0.32, 1.0)
    
    ctx.new_path()
    ctx.move_to(col_x - col_w * 0.4, 0); ctx.line_to(col_x + col_w * 0.4, 0)
    ctx.line_to(col_x + col_w * 0.88, H); ctx.line_to(col_x - col_w * 0.88, H)
    ctx.close_path(); ctx.set_source(water_grad); ctx.fill()
    
    # Spray particles
    ctx.set_source_rgba(0.92, 0.98, 1.0, 0.88)
    for _ in range(110):
        px = np.random.uniform(col_x - col_w * 0.88, col_x + col_w * 0.88)
        py = np.random.uniform(0, H)
        ctx.arc(px, py, np.random.uniform(5, 26), 0, 2 * math.pi); ctx.fill()

    # 5. Anatomically Detailed Machinist in Navy Dungarees
    ctx.save()
    ctx.translate(1420, 750)
    ctx.rotate(math.radians(-26.0))
    
    # Left Leg (Bracing on catwalk)
    ctx.set_source_rgb(*hex_rgb("#142230"))
    ctx.new_path()
    ctx.move_to(-25, 95); ctx.line_to(-55, 180); ctx.line_to(-35, 260); ctx.line_to(-5, 260); ctx.line_to(-10, 180); ctx.line_to(5, 95); ctx.close_path(); ctx.fill()
    # Left Naval Boot
    ctx.set_source_rgb(*hex_rgb("#0A0D10"))
    rounded_rect(ctx, -45, 255, 55, 30, 8); ctx.fill()
    
    # Right Leg (Knee bent forward into surging water)
    ctx.set_source_rgb(*hex_rgb("#1A2B3D"))
    ctx.new_path()
    ctx.move_to(5, 95); ctx.line_to(45, 170); ctx.line_to(30, 250); ctx.line_to(65, 250); ctx.line_to(75, 170); ctx.line_to(35, 95); ctx.close_path(); ctx.fill()
    # Right Naval Boot submerged
    ctx.set_source_rgb(*hex_rgb("#0A0D10"))
    rounded_rect(ctx, 30, 245, 60, 32, 10); ctx.fill()

    # Churning water splashing over boots
    ctx.set_source_rgba(0.7, 0.9, 1.0, 0.75)
    for bx in range(-60, 100, 18):
        ctx.arc(bx, 265 + math.sin(bx * 0.15 + st * 15) * 8, 10, 0, 2 * math.pi); ctx.fill()
    
    # Chambray Work Shirt Torso with anatomical muscular back
    chambray = cairo.LinearGradient(-60, 0, 60, 0)
    chambray.add_color_stop_rgb(0.0, *hex_rgb("#293E50"))
    chambray.add_color_stop_rgb(0.5, *hex_rgb("#3D5870"))
    chambray.add_color_stop_rgb(1.0, *hex_rgb("#1C2C3A"))
    ctx.new_path()
    ctx.move_to(-48, 100)
    ctx.curve_to(-58, 40, -55, -20, -42, -60)
    ctx.line_to(42, -60)
    ctx.curve_to(55, -20, 58, 40, 48, 100)
    ctx.close_path()
    ctx.set_source(chambray); ctx.fill_preserve()
    ctx.set_source_rgb(*hex_rgb("#0D161E")); ctx.set_line_width(2.5); ctx.stroke()
    
    # Left Arm: Muscular forearm reaching to grip rail
    ctx.set_source_rgb(*hex_rgb("#D6A784"))
    ctx.new_path()
    ctx.move_to(-38, -30); ctx.line_to(-135, -115); ctx.line_to(-115, -145); ctx.line_to(-20, -55); ctx.close_path()
    ctx.fill_preserve()
    ctx.set_source_rgb(*hex_rgb("#A87455")); ctx.set_line_width(2.2); ctx.stroke()
    
    # Hand wrapped tightly around the vertical rail
    rounded_rect(ctx, -148, -142, 44, 38, 12)
    ctx.set_source_rgb(*hex_rgb("#D6A784")); ctx.fill()
    ctx.set_source_rgb(*hex_rgb("#965C3D")); ctx.set_line_width(3.0)
    for fy in [-135, -123, -111]:
        ctx.move_to(-142, fy); ctx.line_to(-112, fy); ctx.stroke()
        
    # Right Arm: Shielding face from high-pressure water spray
    ctx.set_source_rgb(*hex_rgb("#D6A784"))
    ctx.new_path()
    ctx.move_to(20, -45); ctx.line_to(65, -95); ctx.line_to(45, -120); ctx.line_to(5, -65); ctx.close_path(); ctx.fill()
    rounded_rect(ctx, 45, -135, 35, 32, 10); ctx.fill()
    
    # Neck & Head shouting in terror
    ctx.set_source_rgb(*hex_rgb("#C69371"))
    rounded_rect(ctx, -16, -75, 32, 35, 8); ctx.fill()
    
    # Head & Profile
    ctx.set_source_rgb(*hex_rgb("#D6A784"))
    ctx.new_path()
    ctx.move_to(-32, -65); ctx.curve_to(-42, -95, -35, -125, -5, -132)
    ctx.curve_to(25, -130, 35, -100, 28, -65); ctx.close_path()
    ctx.fill()
    
    # Shouting open mouth with teeth & tongue
    ctx.set_source_rgb(*hex_rgb("#2A0A0A"))
    rounded_rect(ctx, -28, -92, 26, 18, 6); ctx.fill()
    ctx.set_source_rgb(*hex_rgb("#F5EFE6"))
    ctx.rectangle(-24, -92, 18, 5); ctx.fill() # Upper teeth
    
    # Strained Eye squinting against spray
    ctx.set_source_rgb(*hex_rgb("#1F2D38")); ctx.set_line_width(3.0)
    ctx.move_to(-25, -106); ctx.line_to(-12, -102); ctx.stroke()
    ctx.move_to(-25, -102); ctx.line_to(-12, -106); ctx.stroke()
    
    # White Dixie Cup Sailor Cap
    ctx.new_path()
    ctx.move_to(-42, -120); ctx.curve_to(-38, -155, 32, -155, 36, -120); ctx.close_path()
    ctx.set_source_rgb(*hex_rgb("#F2F5F8")); ctx.fill_preserve()
    ctx.set_source_rgb(*hex_rgb("#BAC6D0")); ctx.set_line_width(2.2); ctx.stroke()
    # Rolled brim
    rounded_rect(ctx, -46, -125, 86, 14, 6)
    ctx.set_source_rgb(*hex_rgb("#E2E8EE")); ctx.fill()
    ctx.restore()

    # 6. Electrical Switchboard Sparks Shower
    for _ in range(45):
        sx = 380 + np.random.uniform(-90, 90)
        sy = 450 + np.random.uniform(-160, 160)
        ctx.set_source_rgb(1.0, 0.95, 0.45)
        ctx.arc(sx, sy, np.random.uniform(3, 8), 0, 2 * math.pi); ctx.fill()
        
    ctx.restore()

    # Vietnamese Subtitle for Scene 9
    ctx.save()
    ctx.set_source_rgba(1.0, 0.35, 0.35, 0.98)
    ctx.select_font_face("Segoe UI", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(32); ctx.move_to(180, 960)
    ctx.show_text("CỘT NƯỚC LẠNH NHƯ BĂNG SẦM SẬP ĐỔ THẲNG VÀO HAI KHOANG ĐỘNG CƠ")
    ctx.restore()

print("art_assets.py upgraded with high-fidelity assets")
