import os
import sys
import math
import subprocess
import numpy as np
import cairo

W, H = 1920, 1080
FPS = 30
DURATION = 81.9
TOTAL_FRAMES = int(DURATION * FPS)

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

def draw_vignette(ctx, intensity=0.5):
    ctx.save()
    rad = math.hypot(W, H) / 1.7
    pat = cairo.RadialGradient(W / 2, H / 2, rad * 0.45, W / 2, H / 2, rad)
    pat.add_color_stop_rgba(0.0, 0, 0, 0, 0.0)
    pat.add_color_stop_rgba(1.0, 0, 0, 0, intensity)
    ctx.rectangle(0, 0, W, H)
    ctx.set_source(pat)
    ctx.fill()
    ctx.restore()

# -------------------------------------------------------------
# SCENE 1: The Frigid Horizon (0.0s – 7.5s)
# -------------------------------------------------------------
def render_scene_1(ctx, t):
    # Camera slow forward dolly + subtle sea roll
    dolly = t * 15.0
    cam_y = math.sin(t * 0.6) * 12.0
    
    # Sky / Horizon Gradient (Morning Arctic Dawn)
    sky = cairo.LinearGradient(0, 0, 0, 680)
    sky.add_color_stop_rgb(0.0, *hex_rgb("#243B4A"))
    sky.add_color_stop_rgb(0.65, *hex_rgb("#637E8E"))
    sky.add_color_stop_rgb(1.0, *hex_rgb("#A6BBC5"))
    ctx.rectangle(0, 0, W, 680)
    ctx.set_source(sky)
    ctx.fill()
    
    # Distant Pale Sun through heavy cloud
    sun_pat = cairo.RadialGradient(1450, 320, 20, 1450, 320, 240)
    sun_pat.add_color_stop_rgba(0.0, 1.0, 0.98, 0.90, 0.45)
    sun_pat.add_color_stop_rgba(1.0, 1.0, 0.98, 0.90, 0.0)
    ctx.rectangle(0, 0, W, 680)
    ctx.set_source(sun_pat)
    ctx.fill()
    
    # Deep North Atlantic Water (2°C)
    sea = cairo.LinearGradient(0, 560, 0, H)
    sea.add_color_stop_rgb(0.0, *hex_rgb("#1B3B48"))
    sea.add_color_stop_rgb(0.4, *hex_rgb("#0F2530"))
    sea.add_color_stop_rgb(1.0, *hex_rgb("#06131A"))
    
    # Animated Parallax Ocean Swells (3 Layers)
    for layer, (base_y, amp, speed, col) in enumerate([
        (560 + cam_y * 0.3, 10.0, 1.2, "#234958"),
        (660 + cam_y * 0.6, 18.0, 1.7, "#173642"),
        (780 + cam_y * 1.0, 26.0, 2.2, "#0D222B"),
    ]):
        ctx.new_path()
        ctx.move_to(0, H)
        ctx.line_to(0, base_y)
        for x in range(0, W + 40, 40):
            sw = amp * math.sin((x + dolly * (layer + 1) * 3) * 0.005 + t * speed)
            ctx.line_to(x, base_y + sw)
        ctx.line_to(W, H)
        ctx.close_path()
        ctx.set_source_rgb(*hex_rgb(col))
        ctx.fill()
        
        # Crest foam highlights
        ctx.set_line_width(2.0)
        ctx.set_source_rgba(0.85, 0.94, 0.98, 0.35)
        for x in range(20, W, 120):
            fx = (x + dolly * (layer + 1) * 5) % W
            fy = base_y + amp * math.sin((fx + dolly * (layer + 1) * 3) * 0.005 + t * speed)
            ctx.arc(fx, fy - 1, 14, 0.2, math.pi - 0.2)
            ctx.stroke()

    # Drifting Cold Fog / Sea Mist
    for i, (fy, speed, op) in enumerate([(520, 45, 0.18), (620, 75, 0.25), (750, 110, 0.20)]):
        offset = (t * speed) % (W + 600) - 300
        pat_fog = cairo.LinearGradient(offset, fy, offset + 600, fy + 140)
        pat_fog.add_color_stop_rgba(0.0, 0.85, 0.92, 0.96, 0.0)
        pat_fog.add_color_stop_rgba(0.5, 0.85, 0.92, 0.96, op)
        pat_fog.add_color_stop_rgba(1.0, 0.85, 0.92, 0.96, 0.0)
        ctx.rectangle(0, fy - 60, W, 200)
        ctx.set_source(pat_fog)
        ctx.fill()

    # Cinematic Title Card
    if t >= 0.8:
        alpha = min(1.0, (t - 0.8) / 1.2)
        if t > 6.0:
            alpha = max(0.0, 1.0 - (t - 6.0) / 1.2)
        ctx.save()
        ctx.set_source_rgba(0.92, 0.96, 1.0, alpha * 0.95)
        ctx.select_font_face("Georgia", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(32)
        ctx.move_to(160, 420)
        ctx.show_text("MAY 23, 1939  •  08:00 AM")
        
        ctx.set_source_rgba(0.75, 0.88, 0.95, alpha * 0.85)
        ctx.select_font_face("Arial", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(22)
        ctx.move_to(160, 465)
        ctx.show_text("OFF THE COAST OF NEW HAMPSHIRE  |  NORTH ATLANTIC (2°C)")
        ctx.restore()

# -------------------------------------------------------------
# Helper: Detailed Procedural USS Squalus Exterior Rig
# -------------------------------------------------------------
def draw_squalus_hull(ctx, x, y, scale=1.0, submerged=0.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(scale, scale)
    
    # 1. Main Hull Silhouette (94-meter fleet submarine profile)
    ctx.new_path()
    # Sharp knife-bow to long sleek hull
    ctx.move_to(450, 0)
    ctx.curve_to(430, -35, 360, -42, 280, -42)
    ctx.line_to(-380, -42)
    ctx.curve_to(-460, -42, -520, -25, -550, -5) # Stern taper
    ctx.line_to(-550, 15)
    ctx.curve_to(-520, 35, -440, 45, -340, 45)
    ctx.line_to(260, 45)
    ctx.curve_to(380, 45, 435, 25, 450, 0)
    ctx.close_path()
    
    # Steel hull gradient
    hull_grad = cairo.LinearGradient(0, -45, 0, 45)
    hull_grad.add_color_stop_rgb(0.0, *hex_rgb("#3A474D"))
    hull_grad.add_color_stop_rgb(0.5, *hex_rgb("#273238"))
    hull_grad.add_color_stop_rgb(1.0, *hex_rgb("#171F24"))
    ctx.set_source(hull_grad)
    ctx.fill_preserve()
    ctx.set_source_rgb(*hex_rgb("#101518"))
    ctx.set_line_width(3.0)
    ctx.stroke()
    
    # Hull plating seams & rivets
    ctx.set_source_rgba(0.05, 0.08, 0.10, 0.45)
    ctx.set_line_width(1.5)
    for px in range(-480, 420, 65):
        ctx.move_to(px, -42)
        ctx.line_to(px, 45)
        ctx.stroke()

    # 2. Conning Tower & Periscope Shears
    ctx.new_path()
    ctx.move_to(80, -42)
    ctx.line_to(90, -130)
    ctx.curve_to(85, -145, 45, -145, -30, -145)
    ctx.line_to(-75, -145)
    ctx.curve_to(-95, -145, -105, -130, -115, -42)
    ctx.close_path()
    tower_grad = cairo.LinearGradient(0, -145, 0, -42)
    tower_grad.add_color_stop_rgb(0.0, *hex_rgb("#44545D"))
    tower_grad.add_color_stop_rgb(1.0, *hex_rgb("#232D33"))
    ctx.set_source(tower_grad)
    ctx.fill_preserve()
    ctx.set_source_rgb(*hex_rgb("#101518"))
    ctx.set_line_width(2.5)
    ctx.stroke()

    # Periscopes & Radio Mast
    ctx.set_source_rgb(*hex_rgb("#5C6E78"))
    ctx.set_line_width(4.0)
    ctx.move_to(15, -145); ctx.line_to(15, -210); ctx.stroke() # Attack periscope
    ctx.move_to(-25, -145); ctx.line_to(-25, -235); ctx.stroke() # Search periscope
    ctx.move_to(-55, -145); ctx.line_to(-55, -195); ctx.stroke() # Radio mast
    
    # Submarine Hull Number "192"
    ctx.save()
    ctx.set_source_rgba(0.85, 0.90, 0.95, 0.85)
    ctx.select_font_face("Impact", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(24)
    ctx.move_to(-20, -75)
    ctx.show_text("192")
    ctx.restore()
    
    # Deck Gun (3-inch / 50 caliber) forward of conning tower
    ctx.set_source_rgb(*hex_rgb("#1E272B"))
    ctx.set_line_width(4.5)
    ctx.move_to(180, -42); ctx.line_to(195, -60); ctx.line_to(255, -72); ctx.stroke()
    ctx.arc(195, -55, 9, 0, 2 * math.pi); ctx.fill()

    # Bronze Propeller (Aft)
    ctx.save()
    ctx.translate(-545, 10)
    ctx.set_source_rgb(*hex_rgb("#B8860B")) # Dark bronze
    for ang in [0, math.pi * 2 / 3, math.pi * 4 / 3]:
        ctx.save()
        ctx.rotate(ang)
        ctx.scale(1.2, 0.4)
        ctx.arc(0, 0, 18, 0, 2 * math.pi)
        ctx.fill()
        ctx.restore()
    ctx.restore()
    
    ctx.restore()

# -------------------------------------------------------------
# SCENE 2: The Emergence of USS Squalus (7.5s – 15.5s)
# -------------------------------------------------------------
def render_scene_2(ctx, t):
    st = t - 7.5
    # Cinematic tracking camera moving alongside the submarine
    cam_x = -200 + st * 75.0
    cam_roll = math.sin(st * 0.8) * 0.015
    
    # Cold Atlantic Sky
    sky = cairo.LinearGradient(0, 0, 0, 600)
    sky.add_color_stop_rgb(0.0, *hex_rgb("#2B3D4A"))
    sky.add_color_stop_rgb(1.0, *hex_rgb("#7E97A6"))
    ctx.rectangle(0, 0, W, 600)
    ctx.set_source(sky)
    ctx.fill()
    
    # Ocean Swell
    sea = cairo.LinearGradient(0, 520, 0, H)
    sea.add_color_stop_rgb(0.0, *hex_rgb("#1A3A46"))
    sea.add_color_stop_rgb(1.0, *hex_rgb("#09161E"))
    ctx.rectangle(0, 520, W, H - 520)
    ctx.set_source(sea)
    ctx.fill()
    
    # Submarine Hull in transit
    sub_y = 560 + math.sin(st * 1.1) * 8.0
    draw_squalus_hull(ctx, 960 + cam_x * 0.4, sub_y, scale=1.45)
    
    # Bow Wave & Foam Splash
    bow_x = 960 + cam_x * 0.4 + 450 * 1.45
    ctx.set_source_rgba(0.92, 0.96, 1.0, 0.75)
    for bx in range(int(bow_x - 30), int(bow_x + 90), 12):
        by = sub_y + math.sin(bx * 0.1 + st * 8.0) * 8.0
        ctx.arc(bx, by, 7, 0, 2 * math.pi)
        ctx.fill()
        
    # Diesel exhaust puffs from aft manifold
    exhaust_x = 960 + cam_x * 0.4 - 280 * 1.45
    for p in range(4):
        pt = (st * 3.5 + p * 0.35) % 1.4
        px = exhaust_x - pt * 120
        py = sub_y - 80 - pt * 60 + math.sin(pt * 5) * 8
        ctx.set_source_rgba(0.35, 0.38, 0.40, max(0.0, (1.0 - pt / 1.4) * 0.4))
        ctx.arc(px, py, 12 + pt * 35, 0, 2 * math.pi)
        ctx.fill()
        
    # Foreground Waves & Drifting Fog Mist
    for w_i in range(3):
        ctx.new_path()
        ctx.move_to(0, H)
        fy = 590 + w_i * 80
        ctx.line_to(0, fy)
        for x in range(0, W + 40, 40):
            wy = fy + 16.0 * math.sin(x * 0.007 + st * (2.0 + w_i * 0.4))
            ctx.line_to(x, wy)
        ctx.line_to(W, H)
        ctx.close_path()
        ctx.set_source_rgba(0.08, 0.20, 0.26, 0.65 + w_i * 0.15)
        ctx.fill()
        
    # Submarine Info Label
    alpha = min(1.0, st / 1.0)
    if st > 6.5: alpha = max(0.0, 1.0 - (st - 6.5) / 1.0)
    ctx.save()
    ctx.set_source_rgba(1.0, 1.0, 1.0, alpha * 0.9)
    ctx.select_font_face("Impact", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(42)
    ctx.move_to(180, 240)
    ctx.show_text("USS SQUALUS (SS-192)")
    
    ctx.set_source_rgba(0.85, 0.92, 0.98, alpha * 0.8)
    ctx.select_font_face("Arial", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(24)
    ctx.move_to(180, 285)
    ctx.show_text("SARGO-CLASS FLEET SUBMARINE  •  LENGTH: 94.7 METERS  •  DISPLACEMENT: 2,350 TONS")
    ctx.restore()

# -------------------------------------------------------------
# SCENE 3: 59 Souls & Commander Naquin (15.5s – 25.5s)
# -------------------------------------------------------------
def render_scene_3(ctx, t):
    st = t - 15.5
    # Camera slow creeping dolly inside the control room
    zoom = 1.0 + st * 0.015
    ctx.save()
    ctx.translate(W / 2, H / 2)
    ctx.scale(zoom, zoom)
    ctx.translate(-W / 2, -H / 2)
    
    # Dark Cramped Submarine Interior Bulkhead
    bg = cairo.LinearGradient(0, 0, W, H)
    bg.add_color_stop_rgb(0.0, *hex_rgb("#141D22"))
    bg.add_color_stop_rgb(0.5, *hex_rgb("#1E2A31"))
    bg.add_color_stop_rgb(1.0, *hex_rgb("#0F171B"))
    ctx.rectangle(0, 0, W, H)
    ctx.set_source(bg)
    ctx.fill()
    
    # Overhead Industrial Copper & Steel Pipes
    for py, r_col in [(120, "#B87333"), (165, "#8A9EA7"), (210, "#A0522D")]:
        ctx.set_source_rgb(*hex_rgb(r_col))
        ctx.set_line_width(28.0)
        ctx.move_to(0, py); ctx.line_to(W, py); ctx.stroke()
        # Pipe joints / valves
        for vx in range(250, W, 380):
            ctx.set_source_rgb(0.15, 0.15, 0.15)
            ctx.rectangle(vx - 20, py - 22, 40, 44); ctx.fill()
            ctx.set_source_rgb(0.75, 0.25, 0.2)
            ctx.arc(vx, py, 32, 0, 2 * math.pi); ctx.stroke()

    # Brass Depth & Pressure Gauges
    for gi, (gx, gy, gr, gtitle) in enumerate([
        (480, 360, 95, "DEPTH - FEET"),
        (720, 340, 115, "MAIN BALLAST"),
        (1380, 350, 105, "HYDRAULIC PSI")
    ]):
        # Outer Brass Ring
        ctx.set_source_rgb(*hex_rgb("#CD7F32"))
        ctx.arc(gx, gy, gr, 0, 2 * math.pi)
        ctx.fill()
        # Cream face
        ctx.set_source_rgb(*hex_rgb("#EAE3D2"))
        ctx.arc(gx, gy, gr - 12, 0, 2 * math.pi)
        ctx.fill()
        # Tick marks
        ctx.set_source_rgb(0.15, 0.15, 0.15)
        ctx.set_line_width(2.0)
        for ang_i in range(12):
            rad = math.radians(ang_i * 30)
            ctx.move_to(gx + (gr - 25) * math.cos(rad), gy + (gr - 25) * math.sin(rad))
            ctx.line_to(gx + (gr - 15) * math.cos(rad), gy + (gr - 15) * math.sin(rad))
            ctx.stroke()
        # Needle
        needle_ang = math.radians(210 + math.sin(st * 2.0 + gi) * 20)
        ctx.set_source_rgb(0.8, 0.1, 0.1)
        ctx.set_line_width(3.5)
        ctx.move_to(gx, gy)
        ctx.line_to(gx + (gr - 30) * math.cos(needle_ang), gy + (gr - 30) * math.sin(needle_ang))
        ctx.stroke()
        ctx.arc(gx, gy, 8, 0, 2 * math.pi); ctx.fill()

    # Incandescent Warm Bulkhead Lanterns (Glow effect)
    for lx in [320, 1050, 1620]:
        pat = cairo.RadialGradient(lx, 150, 15, lx, 150, 350)
        pat.add_color_stop_rgba(0.0, 1.0, 0.85, 0.50, 0.55)
        pat.add_color_stop_rgba(1.0, 0.2, 0.15, 0.05, 0.0)
        ctx.rectangle(0, 0, W, H)
        ctx.set_source(pat)
        ctx.fill()

    # CHARACTER: Lieutenant Oliver Naquin (Profile / 3/4 Silhouette)
    # Head, naval officer's cap, gold visor trim, uniform coat
    ctx.save()
    ctx.translate(1050, 480)
    
    # Body Coat
    ctx.set_source_rgb(*hex_rgb("#17242C"))
    ctx.move_to(-120, 450); ctx.line_to(-80, 160); ctx.curve_to(-70, 90, 70, 90, 80, 160); ctx.line_to(120, 450); ctx.close_path()
    ctx.fill()
    # Gold officer collar anchors
    ctx.set_source_rgb(*hex_rgb("#D4AF37"))
    ctx.rectangle(-45, 150, 18, 28); ctx.fill()
    ctx.rectangle(27, 150, 18, 28); ctx.fill()
    
    # Head & Neck
    ctx.set_source_rgb(*hex_rgb("#D4A373"))
    ctx.arc(0, 60, 52, 0, 2 * math.pi); ctx.fill()
    
    # Naval Officer Visor Cap
    ctx.set_source_rgb(*hex_rgb("#111A20"))
    rounded_rect(ctx, -75, -5, 150, 50, 12); ctx.fill()
    # Gold braided chin strap
    ctx.set_source_rgb(*hex_rgb("#D4AF37"))
    ctx.rectangle(-70, 32, 140, 10); ctx.fill()
    # Black polished peak / visor
    ctx.set_source_rgb(0.05, 0.05, 0.05)
    ctx.move_to(-75, 42); ctx.curve_to(-30, 68, 50, 68, 85, 42); ctx.line_to(70, 38); ctx.close_path(); ctx.fill()
    
    # Hand holding silver pocket watch
    watch_swing = math.sin(st * 1.5) * 4.0
    ctx.set_source_rgb(*hex_rgb("#D4A373"))
    ctx.arc(-90, 280 + watch_swing, 24, 0, 2 * math.pi); ctx.fill()
    ctx.set_source_rgb(*hex_rgb("#C0C0C0"))
    ctx.arc(-90, 280 + watch_swing, 18, 0, 2 * math.pi); ctx.fill()
    
    # Cold breath vapor
    bv_alpha = (0.5 + 0.5 * math.sin(st * 2.5)) * 0.35
    ctx.set_source_rgba(0.9, 0.95, 1.0, bv_alpha)
    ctx.arc(45 + st * 15 % 50, 65 - st * 8 % 30, 22, 0, 2 * math.pi); ctx.fill()
    ctx.restore()

    # Crew Silhouettes in Background (Helmsman, Chief of the Boat)
    for cx, cy in [(350, 620), (1500, 640)]:
        ctx.set_source_rgb(0.08, 0.12, 0.15)
        ctx.arc(cx, cy - 120, 42, 0, 2 * math.pi); ctx.fill() # Head
        ctx.rectangle(cx - 70, cy - 70, 140, 320); ctx.fill() # Torso

    # Historical Banner
    ctx.restore()
    alpha = min(1.0, st / 1.0)
    if st > 8.5: alpha = max(0.0, 1.0 - (st - 8.5) / 1.0)
    ctx.save()
    ctx.set_source_rgba(0.95, 0.95, 0.95, alpha * 0.9)
    ctx.select_font_face("Impact", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(36)
    ctx.move_to(160, 960)
    ctx.show_text("59 CREW & CIVILIAN ENGINEERS ON BOARD")
    ctx.set_font_size(24)
    ctx.select_font_face("Arial", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_source_rgba(0.8, 0.85, 0.9, alpha * 0.8)
    ctx.move_to(160, 1000)
    ctx.show_text("LIEUTENANT OLIVER F. NAQUIN COMMANDING  •  HIGH-SPEED TEST DIVE #19")
    ctx.restore()

# -------------------------------------------------------------
# SCENE 4: The Dive Klaxon & Engine Silence (25.5s – 32.5s)
# -------------------------------------------------------------
def render_scene_4(ctx, t):
    st = t - 25.5
    # Klaxon vibration camera shake
    shake_x = math.sin(st * 45) * 5.0 if (0.5 < st < 3.2) else 0.0
    shake_y = math.cos(st * 50) * 5.0 if (0.5 < st < 3.2) else 0.0
    
    ctx.save()
    ctx.translate(shake_x, shake_y)
    
    if st < 3.5:
        # Split action: Close-up on the diving alarm horn & telegraph
        ctx.set_source_rgb(*hex_rgb("#12191D"))
        ctx.rectangle(0, 0, W, H); ctx.fill()
        
        # Klaxon Warning Horn Housing
        ctx.set_source_rgb(*hex_rgb("#A83232"))
        rounded_rect(ctx, 420, 240, 320, 420, 25); ctx.fill()
        ctx.set_source_rgb(*hex_rgb("#D4AF37"))
        ctx.arc(580, 450, 130, 0, 2 * math.pi); ctx.fill()
        ctx.set_source_rgb(0.1, 0.1, 0.1)
        ctx.arc(580, 450, 100, 0, 2 * math.pi); ctx.fill()
        
        # Flashing Strobe Flare during AHOOGA
        flash_alpha = (0.5 + 0.5 * math.sin(st * 28)) * 0.6 if st < 3.0 else 0.0
        pat = cairo.RadialGradient(580, 450, 50, 580, 450, 600)
        pat.add_color_stop_rgba(0.0, 1.0, 0.2, 0.1, flash_alpha)
        pat.add_color_stop_rgba(1.0, 0.0, 0.0, 0.0, 0.0)
        ctx.set_source(pat); ctx.rectangle(0, 0, W, H); ctx.fill()
        
        # Engine Order Telegraph (Full Ahead to Submerge)
        ctx.set_source_rgb(*hex_rgb("#CD7F32"))
        ctx.arc(1350, 460, 220, 0, 2 * math.pi); ctx.fill()
        ctx.set_source_rgb(*hex_rgb("#F7F1E1"))
        ctx.arc(1350, 460, 195, 0, 2 * math.pi); ctx.fill()
        
        # Telegraph Handle Pulled Down
        handle_ang = math.radians(45 + min(90.0, st * 60.0))
        ctx.set_source_rgb(0.8, 0.15, 0.1)
        ctx.set_line_width(18.0)
        ctx.move_to(1350, 460)
        ctx.line_to(1350 + 230 * math.cos(handle_ang), 460 + 230 * math.sin(handle_ang))
        ctx.stroke()
        
        # Text Prompt
        ctx.set_source_rgba(1, 1, 1, 0.95)
        ctx.select_font_face("Impact", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(48)
        ctx.move_to(510, 820)
        ctx.show_text("DIVE ALARM SOUNDED")
    else:
        # Submerging: Hull cutting underwater
        sink_pct = (st - 3.5) / 3.5
        sub_y = 480 + sink_pct * 180
        
        # Water line rising
        ctx.set_source_rgb(*hex_rgb("#183845"))
        ctx.rectangle(0, 0, W, H); ctx.fill()
        
        draw_squalus_hull(ctx, 960, sub_y, scale=1.35)
        
        # Foaming water covering deck
        ctx.set_source_rgba(0.85, 0.95, 1.0, 0.7)
        for fx in range(200, 1720, 30):
            fy = 520 + math.sin(fx * 0.02 + st * 12) * 22
            ctx.arc(fx, fy, 14, 0, 2 * math.pi); ctx.fill()
            
    ctx.restore()

# -------------------------------------------------------------
# SCENE 5: The "Christmas Tree" Board (32.5s – 42.5s)
# -------------------------------------------------------------
def render_scene_5(ctx, t):
    st = t - 32.5
    # Macro zoom into the Christmas tree panel
    zoom = 1.0 + st * 0.03
    ctx.save()
    ctx.translate(W / 2, H / 2)
    ctx.scale(zoom, zoom)
    ctx.translate(-W / 2, -H / 2)
    
    # Dark Control Room Background
    ctx.set_source_rgb(*hex_rgb("#0E161B"))
    ctx.rectangle(0, 0, W, H); ctx.fill()
    
    # The Submarine Indicator Board ("Christmas Tree")
    rounded_rect(ctx, 360, 160, 1200, 760, 30)
    ctx.set_source_rgb(*hex_rgb("#1C262C")); ctx.fill_preserve()
    ctx.set_source_rgb(*hex_rgb("#2E3D46")); ctx.set_line_width(8.0); ctx.stroke()
    
    # Board Title
    ctx.set_source_rgba(0.9, 0.9, 0.9, 0.9)
    ctx.select_font_face("Impact", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(32)
    ctx.move_to(760, 230)
    ctx.show_text("HULL OPENINGS INDICATOR")
    
    # Grid of Indicator Lights (Red turning to Emerald Green at ~5.5s)
    # 2 rows of 8 lights
    turn_green = st >= 5.5
    
    for row in range(2):
        for col in range(8):
            lx = 520 + col * 125
            ly = 380 + row * 220
            
            # Brass bezel
            ctx.set_source_rgb(*hex_rgb("#CD7F32"))
            ctx.arc(lx, ly, 44, 0, 2 * math.pi); ctx.fill()
            
            # Light state: Green if turn_green else Red
            is_green = turn_green
            col_hex = "#2ED573" if is_green else "#FF4757"
            
            # Lens core
            ctx.set_source_rgb(*hex_rgb(col_hex))
            ctx.arc(lx, ly, 36, 0, 2 * math.pi); ctx.fill()
            
            # Glowing Bloom
            pat = cairo.RadialGradient(lx, ly, 20, lx, ly, 95)
            r, g, b = hex_rgb(col_hex)
            pat.add_color_stop_rgba(0.0, r, g, b, 0.6)
            pat.add_color_stop_rgba(1.0, r, g, b, 0.0)
            ctx.arc(lx, ly, 95, 0, 2 * math.pi)
            ctx.set_source(pat); ctx.fill()
            
            # Label under each indicator
            lbl = f"V-{row*8 + col + 1}"
            if row == 1 and col == 4:
                lbl = "MAIN IND." # The fatal main induction valve!
            ctx.set_source_rgba(0.85, 0.85, 0.85, 0.75)
            ctx.select_font_face("Arial", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            ctx.set_font_size(15)
            ctx.move_to(lx - 25, ly + 65)
            ctx.show_text(lbl)

    ctx.restore()
    
    # Overlay Subtitle
    if turn_green:
        ctx.save()
        ctx.set_source_rgba(0.3, 1.0, 0.5, 0.95)
        ctx.select_font_face("Impact", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(38)
        ctx.move_to(680, 990)
        ctx.show_text("ALL VENTS CONFIRMED SHUT (ALL GREEN)")
        ctx.restore()

# -------------------------------------------------------------
# SCENE 6: 15-Meter Descent (42.5s – 48.0s)
# -------------------------------------------------------------
def render_scene_6(ctx, t):
    st = t - 42.5
    # Smooth underwater glide at an 8-degree down angle
    ctx.set_source_rgb(*hex_rgb("#09222E"))
    ctx.rectangle(0, 0, W, H); ctx.fill()
    
    # Volumetric dancing sunbeams from surface
    for bi in range(6):
        bx = 200 + bi * 280 + math.sin(st * 0.8 + bi) * 50
        pat = cairo.LinearGradient(bx, 0, bx + 160, H)
        pat.add_color_stop_rgba(0.0, 0.6, 0.9, 1.0, 0.16)
        pat.add_color_stop_rgba(1.0, 0.1, 0.4, 0.6, 0.0)
        ctx.move_to(bx - 40, 0); ctx.line_to(bx + 40, 0); ctx.line_to(bx + 260, H); ctx.line_to(bx + 140, H); ctx.close_path()
        ctx.set_source(pat); ctx.fill()
        
    # Submarine descending diagonally
    glide_x = 750 + st * 45
    glide_y = 420 + st * 35
    ctx.save()
    ctx.translate(glide_x, glide_y)
    ctx.rotate(math.radians(8.5))
    draw_squalus_hull(ctx, 0, 0, scale=1.2)
    ctx.restore()
    
    # Depth Gauge Inset (50 feet / 15 meters)
    ctx.save()
    ctx.translate(1600, 240)
    ctx.set_source_rgb(*hex_rgb("#CD7F32")); ctx.arc(0, 0, 120, 0, 2 * math.pi); ctx.fill()
    ctx.set_source_rgb(*hex_rgb("#EDE8D5")); ctx.arc(0, 0, 105, 0, 2 * math.pi); ctx.fill()
    ctx.set_source_rgb(0.1, 0.1, 0.1); ctx.select_font_face("Impact", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(20); ctx.move_to(-40, -40); ctx.show_text("DEPTH - FT")
    # Needle rotating to 50
    deg = 180 + min(120.0, st * 25.0)
    rad = math.radians(deg)
    ctx.set_source_rgb(0.85, 0.1, 0.1); ctx.set_line_width(4.5)
    ctx.move_to(0, 0); ctx.line_to(85 * math.cos(rad), 85 * math.sin(rad)); ctx.stroke()
    ctx.arc(0, 0, 10, 0, 2 * math.pi); ctx.fill()
    ctx.restore()

# -------------------------------------------------------------
# SCENE 7: The Lie (48.0s – 50.0s)
# -------------------------------------------------------------
def render_scene_7(ctx, t):
    st = t - 48.0
    # Macro close-up on the single fatal green indicator light
    ctx.set_source_rgb(*hex_rgb("#080D10"))
    ctx.rectangle(0, 0, W, H); ctx.fill()
    
    # Camera glitch / shudder
    flicker = (math.sin(st * 40) > 0.3)
    shake_y = math.sin(st * 60) * 3.0
    
    ctx.save()
    ctx.translate(W / 2, H / 2 + shake_y)
    
    # Heavy Brass Industrial Bezel
    ctx.set_source_rgb(*hex_rgb("#A56728"))
    ctx.arc(0, 0, 220, 0, 2 * math.pi); ctx.fill()
    
    # Glowing Green Lamp (flickering between bright green and warning glitch)
    col = hex_rgb("#2ED573") if not flicker else hex_rgb("#E74C3C")
    ctx.set_source_rgb(*col)
    ctx.arc(0, 0, 180, 0, 2 * math.pi); ctx.fill()
    
    # Flare Bloom
    pat = cairo.RadialGradient(0, 0, 60, 0, 0, 480)
    pat.add_color_stop_rgba(0.0, col[0], col[1], col[2], 0.7)
    pat.add_color_stop_rgba(1.0, col[0], col[1], col[2], 0.0)
    ctx.set_source(pat); ctx.arc(0, 0, 480, 0, 2 * math.pi); ctx.fill()
    
    ctx.restore()
    
    # Dramatic Narrative Text
    ctx.save()
    ctx.set_source_rgba(1.0, 0.25, 0.25, min(1.0, st * 1.5))
    ctx.select_font_face("Georgia", cairo.FONT_SLANT_ITALIC, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(48)
    ctx.move_to(580, 920)
    ctx.show_text("BUT THE GREEN LIGHTS LIED.")
    ctx.restore()

# -------------------------------------------------------------
# SCENE 8: The 80cm Valve Rupture (50.0s – 57.5s)
# -------------------------------------------------------------
def render_scene_8(ctx, t):
    st = t - 50.0
    # Mounting vibration then catastrophic blowout
    vibe = min(22.0, st * 3.5)
    vx = math.sin(st * 70) * vibe
    vy = math.cos(st * 80) * vibe
    
    ctx.save()
    ctx.translate(vx, vy)
    
    # Aft Compartment Overhead Steel Trunk
    ctx.set_source_rgb(*hex_rgb("#11161A"))
    ctx.rectangle(0, 0, W, H); ctx.fill()
    
    # Massive 31-inch (80cm) Valve Flange
    ctx.save()
    ctx.translate(960, 500)
    ctx.rotate(math.radians(-15.0))
    
    # Steel Pipe Housing
    ctx.set_source_rgb(*hex_rgb("#2F3B42"))
    ctx.rectangle(-280, -320, 560, 640); ctx.fill()
    
    # Flange Ring with Heavy Bolts
    ctx.set_source_rgb(*hex_rgb("#1F272C"))
    ctx.arc(0, 0, 260, 0, 2 * math.pi); ctx.fill_preserve()
    ctx.set_source_rgb(*hex_rgb("#4A5C66")); ctx.set_line_width(12.0); ctx.stroke()
    
    for b_ang in range(0, 360, 30):
        rad = math.radians(b_ang)
        ctx.set_source_rgb(*hex_rgb("#859BA8"))
        ctx.arc(220 * math.cos(rad), 220 * math.sin(rad), 14, 0, 2 * math.pi); ctx.fill()

    # The 80cm Valve Disc slamming open at st >= 4.0
    is_blown = st >= 4.0
    open_pct = min(1.0, (st - 4.0) / 0.4) if is_blown else 0.0
    
    # Hinged Valve Disc opening to exterior ocean pressure
    ctx.save()
    ctx.translate(0, -180)
    ctx.rotate(math.radians(open_pct * 85.0))
    ctx.translate(0, 180)
    
    ctx.set_source_rgb(*hex_rgb("#3D4D57"))
    ctx.arc(0, 0, 180, 0, 2 * math.pi); ctx.fill_preserve()
    ctx.set_source_rgb(*hex_rgb("#1A2226")); ctx.set_line_width(8.0); ctx.stroke()
    ctx.restore()
    
    # Rivet Shear Sparks & Hydraulic Blowout
    if is_blown:
        # Water rushing in through the gap
        ctx.set_source_rgba(0.2, 0.7, 0.9, 0.85)
        for sp in range(25):
            sx = np.random.uniform(-180, 180)
            sy = np.random.uniform(-180, 180)
            ctx.arc(sx, sy, np.random.uniform(15, 60), 0, 2 * math.pi); ctx.fill()
            
        # Exploding Rivets flying off
        ctx.set_source_rgb(1.0, 0.8, 0.2)
        for rx, ry in [(250, 100), (-240, -120), (120, -260)]:
            ctx.arc(rx + (st - 4.0) * 400, ry + (st - 4.0) * 350, 8, 0, 2 * math.pi); ctx.fill()
            
    ctx.restore()
    ctx.restore()
    
    # Technical Overlay
    ctx.save()
    ctx.set_source_rgba(1.0, 0.3, 0.2, 0.9)
    ctx.select_font_face("Impact", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(36)
    ctx.move_to(180, 960)
    ctx.show_text("MAIN INDUCTION VALVE (31 INCH / 78.7 CM) BREACHED UNDER WATER PRESSURE")
    ctx.restore()

# -------------------------------------------------------------
# SCENE 9: The Ice Deluge (57.5s – 62.0s)
# -------------------------------------------------------------
def render_scene_9(ctx, t):
    st = t - 57.5
    # Violent camera shake (intensity 10/10)
    shake_x = math.sin(st * 90) * 16.0
    shake_y = math.cos(st * 110) * 14.0
    
    ctx.save()
    ctx.translate(shake_x, shake_y)
    
    # Flooding Engine Room Compartment
    ctx.set_source_rgb(*hex_rgb("#081218"))
    ctx.rectangle(0, 0, W, H); ctx.fill()
    
    # Electrical Arc Flash
    is_arc = (int(st * 15) % 3 == 0)
    if is_arc:
        ctx.set_source_rgba(0.7, 0.85, 1.0, 0.45)
        ctx.rectangle(0, 0, W, H); ctx.fill()
        
    # Massive Solid Column of Freezing Atlantic Water Blasting In
    col_x = 960
    col_w = 480 + st * 150
    water_grad = cairo.LinearGradient(col_x, 0, col_x, H)
    water_grad.add_color_stop_rgba(0.0, 0.35, 0.75, 0.95, 0.95)
    water_grad.add_color_stop_rgba(0.5, 0.15, 0.45, 0.65, 0.98)
    water_grad.add_color_stop_rgba(1.0, 0.05, 0.20, 0.35, 1.0)
    
    ctx.new_path()
    ctx.move_to(col_x - col_w * 0.4, 0)
    ctx.line_to(col_x + col_w * 0.4, 0)
    ctx.line_to(col_x + col_w * 0.8, H)
    ctx.line_to(col_x - col_w * 0.8, H)
    ctx.close_path()
    ctx.set_source(water_grad); ctx.fill()
    
    # High-pressure spray particles & turbulent foam
    ctx.set_source_rgba(0.9, 0.98, 1.0, 0.85)
    for _ in range(80):
        px = np.random.uniform(col_x - col_w * 0.8, col_x + col_w * 0.8)
        py = np.random.uniform(0, H)
        ctx.arc(px, py, np.random.uniform(5, 22), 0, 2 * math.pi); ctx.fill()
        
    # Overwhelmed Sailor Silhouette Knocked by the Torrent
    ctx.save()
    ctx.translate(1420, 720)
    ctx.rotate(math.radians(-35.0))
    ctx.set_source_rgb(0.05, 0.08, 0.1)
    ctx.arc(0, -90, 36, 0, 2 * math.pi); ctx.fill() # Head
    ctx.rectangle(-45, -55, 90, 220); ctx.fill() # Body
    ctx.move_to(-40, -40); ctx.line_to(-120, -120); ctx.set_line_width(28); ctx.stroke() # Desperate reaching arm
    ctx.restore()

    # Electrical Switchboard Sparks Shower
    for _ in range(35):
        sx = 380 + np.random.uniform(-80, 80)
        sy = 450 + np.random.uniform(-150, 150)
        ctx.set_source_rgb(1.0, 0.95, 0.4)
        ctx.arc(sx, sy, np.random.uniform(3, 7), 0, 2 * math.pi); ctx.fill()
        
    ctx.restore()

# -------------------------------------------------------------
# SCENE 10: The Screaming Telephone (62.0s – 69.5s)
# -------------------------------------------------------------
def render_scene_10(ctx, t):
    st = t - 62.0
    # Red Emergency Battle Strobe
    strobe_red = (math.sin(st * 8.0) > 0.0)
    
    bg_col = "#260808" if strobe_red else "#120B0B"
    ctx.set_source_rgb(*hex_rgb(bg_col))
    ctx.rectangle(0, 0, W, H); ctx.fill()
    
    # Sound-Powered Bulkhead Telephone
    phone_vibe = math.sin(st * 40) * 6.0 if st < 4.0 else 0.0
    ctx.save()
    ctx.translate(620 + phone_vibe, 480)
    
    # Cast Iron Box
    ctx.set_source_rgb(*hex_rgb("#2B3338"))
    rounded_rect(ctx, -140, -220, 280, 440, 20); ctx.fill()
    ctx.set_source_rgb(*hex_rgb("#161C20")); ctx.set_line_width(6.0); ctx.stroke()
    
    # Dual Brass Bells on top
    for bell_x in [-75, 75]:
        ctx.set_source_rgb(*hex_rgb("#CD7F32"))
        ctx.arc(bell_x, -235, 45, math.pi, 2 * math.pi); ctx.fill()
        # Clapper ringing
        ctx.set_source_rgb(0.1, 0.1, 0.1)
        ctx.arc(bell_x, -235, 12, 0, 2 * math.pi); ctx.fill()

    # Handset off hook / hanging
    ctx.set_source_rgb(*hex_rgb("#101416"))
    rounded_rect(ctx, 160, -120, 70, 260, 25); ctx.fill()
    # Spiral cord
    ctx.set_line_width(4.0)
    ctx.move_to(0, 180); ctx.curve_to(80, 260, 120, 240, 195, 120); ctx.stroke()
    ctx.restore()
    
    # Lieutenant Naquin in Horror (Foreground Silhouette in Red Light)
    ctx.save()
    ctx.translate(1380, 520)
    ctx.set_source_rgb(0.08, 0.02, 0.02)
    # Head & Cap
    ctx.arc(0, -120, 65, 0, 2 * math.pi); ctx.fill()
    rounded_rect(ctx, -90, -195, 180, 55, 15); ctx.fill()
    # Torso
    ctx.rectangle(-110, -50, 220, 550); ctx.fill()
    ctx.restore()
    
    # Frantic Voice Distress Text
    ctx.save()
    ctx.set_source_rgba(1.0, 0.25, 0.25, 0.95)
    ctx.select_font_face("Impact", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(44)
    ctx.move_to(220, 880)
    ctx.show_text('"TAKE HER UP! ENGINE ROOMS ARE FLOODING!"')
    ctx.restore()

# -------------------------------------------------------------
# SCENE 11: Dragged into the Abyss (69.5s – 74.0s)
# -------------------------------------------------------------
def render_scene_11(ctx, t):
    st = t - 69.5
    # Wide exterior abyss plunge
    ctx.set_source_rgb(*hex_rgb("#03080D"))
    ctx.rectangle(0, 0, W, H); ctx.fill()
    
    # Submarine sinking backwards / stern first
    sink_angle = 15.0 + st * 7.0
    sub_x = 960 - st * 40
    sub_y = 480 + st * 55
    
    ctx.save()
    ctx.translate(sub_x, sub_y)
    ctx.rotate(math.radians(-sink_angle)) # Stern dragged down
    draw_squalus_hull(ctx, 0, 0, scale=1.1)
    ctx.restore()
    
    # Boiling plumes of air bubbles rushing up from flooded stern
    bubble_x = sub_x - 380
    bubble_y = sub_y + 120
    ctx.set_source_rgba(0.5, 0.8, 0.95, 0.6)
    for bi in range(60):
        bx = bubble_x + np.random.uniform(-140, 140)
        by = bubble_y - np.random.uniform(0, 600)
        ctx.arc(bx, by, np.random.uniform(8, 28), 0, 2 * math.pi); ctx.fill()

    # Dark Abyssal Vignette
    draw_vignette(ctx, intensity=0.7)

# -------------------------------------------------------------
# SCENE 12: The 45-Degree Tilt (74.0s – 77.0s)
# -------------------------------------------------------------
def render_scene_12(ctx, t):
    st = t - 74.0
    # The entire frame pitched at 45 degrees
    ctx.save()
    ctx.translate(W / 2, H / 2)
    ctx.rotate(math.radians(-45.0))
    ctx.translate(-W / 2, -H / 2)
    
    # Submarine Interior at Steep Angle
    ctx.set_source_rgb(*hex_rgb("#181414"))
    ctx.rectangle(-400, -400, W + 800, H + 800); ctx.fill()
    
    # Red Emergency Light
    ctx.set_source_rgba(0.8, 0.1, 0.1, 0.25)
    ctx.rectangle(-400, -400, W + 800, H + 800); ctx.fill()
    
    # Bulkhead Deck Plates
    ctx.set_source_rgb(*hex_rgb("#2A3138"))
    ctx.rectangle(-400, 720, W + 800, 400); ctx.fill()
    
    # Tumbling Equipment sliding down the steep deck
    for ti, (tx, ty, tr) in enumerate([(450, 680, 25), (820, 650, 40), (1200, 690, 18)]):
        slide = (st * 450 + ti * 180)
        ctx.set_source_rgb(*hex_rgb("#859BA8"))
        ctx.rectangle(tx - slide, ty, tr * 2, tr); ctx.fill()

    # Crew Men Sliding and Clinging to Brass Pipes
    ctx.save()
    ctx.translate(850 - st * 80, 620)
    ctx.set_source_rgb(0.08, 0.08, 0.08)
    ctx.arc(0, -60, 35, 0, 2 * math.pi); ctx.fill() # Head
    ctx.rectangle(-35, -20, 70, 160); ctx.fill() # Torso
    ctx.set_line_width(22); ctx.move_to(0, 0); ctx.line_to(90, -110); ctx.stroke() # Reaching arm to pipe
    ctx.restore()
    
    ctx.restore()
    
    # Angle readout overlay
    ctx.save()
    ctx.set_source_rgba(1.0, 0.4, 0.4, 0.95)
    ctx.select_font_face("Impact", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(48)
    ctx.move_to(180, 220)
    ctx.show_text("PITCH ANGLE: -45° BOW UP")
    ctx.restore()

# -------------------------------------------------------------
# SCENE 13: The Final Open Bulkhead Door (77.0s – 81.9s)
# -------------------------------------------------------------
def render_scene_13(ctx, t):
    st = t - 77.0
    # Slow reverse dolly through the heavy watertight bulkhead door frame
    zoom = 1.0 - st * 0.03
    fade_to_black = max(0.0, (st - 3.2) / 1.7) if st >= 3.2 else 0.0
    
    ctx.save()
    ctx.translate(W / 2, H / 2)
    ctx.scale(zoom, zoom)
    ctx.translate(-W / 2, -H / 2)
    
    # Oppressive Darkness Outside the Door
    ctx.set_source_rgb(*hex_rgb("#060B0E"))
    ctx.rectangle(0, 0, W, H); ctx.fill()
    
    # Flooding water level rising beyond the door
    water_y = 850 - st * 90
    ctx.set_source_rgb(*hex_rgb("#0C232E"))
    ctx.rectangle(480, water_y, 960, H - water_y); ctx.fill()
    
    # The Watertight Oval Bulkhead Door Frame
    door_w, door_h = 760, 920
    door_x = (W - door_w) / 2
    door_y = (H - door_h) / 2
    
    # Steel Bulkhead Wall
    ctx.set_source_rgb(*hex_rgb("#182025"))
    ctx.rectangle(0, 0, W, H); ctx.fill()
    
    # Cutout Door Aperture
    ctx.save()
    rounded_rect(ctx, door_x, door_y, door_w, door_h, 240)
    ctx.clip()
    
    # Background Flooded Compartment visible through open portal
    ctx.set_source_rgb(*hex_rgb("#0A141A"))
    ctx.rectangle(door_x, door_y, door_w, door_h); ctx.fill()
    
    # Torrents of water spilling across door lip
    ctx.set_source_rgba(0.4, 0.75, 0.9, 0.8)
    for _ in range(40):
        px = np.random.uniform(door_x, door_x + door_w)
        py = np.random.uniform(water_y, H)
        ctx.arc(px, py, np.random.uniform(4, 18), 0, 2 * math.pi); ctx.fill()
        
    ctx.restore()
    
    # Heavy Heavy Oval Steel Door Trim & Gaskets
    rounded_rect(ctx, door_x, door_y, door_w, door_h, 240)
    ctx.set_source_rgb(*hex_rgb("#303E47")); ctx.set_line_width(32.0); ctx.stroke()
    ctx.set_source_rgb(*hex_rgb("#12191D")); ctx.set_line_width(8.0); ctx.stroke()
    
    # Door Locking Dogs (Brass Clamps around circumference)
    for d_ang in range(0, 360, 45):
        rad = math.radians(d_ang)
        dx = W / 2 + (door_w / 2 - 12) * math.cos(rad)
        dy = H / 2 + (door_h / 2 - 12) * math.sin(rad)
        ctx.set_source_rgb(*hex_rgb("#CD7F32"))
        ctx.arc(dx, dy, 18, 0, 2 * math.pi); ctx.fill()

    # FOREGROUND: Sailor's Trembling Hand on the Door Locking Wheel
    ctx.save()
    ctx.translate(420, 680)
    # Door Wheel
    ctx.set_source_rgb(*hex_rgb("#5A6D78"))
    ctx.arc(0, 0, 110, 0, 2 * math.pi); ctx.set_line_width(18.0); ctx.stroke()
    ctx.move_to(-110, 0); ctx.line_to(110, 0); ctx.stroke()
    ctx.move_to(0, -110); ctx.line_to(0, 110); ctx.stroke()
    
    # Hand Gripping Wheel
    hand_tremor = math.sin(st * 35) * 3.0
    ctx.translate(hand_tremor, hand_tremor)
    ctx.set_source_rgb(*hex_rgb("#C29373"))
    rounded_rect(ctx, -60, -35, 120, 70, 25); ctx.fill()
    ctx.restore()

    ctx.restore()
    
    # Final Fade to Black
    if fade_to_black > 0.0:
        ctx.set_source_rgba(0, 0, 0, min(1.0, fade_to_black))
        ctx.rectangle(0, 0, W, H); ctx.fill()

# -------------------------------------------------------------
# Master Frame Dispatcher
# -------------------------------------------------------------
def render_frame(ctx, frame_idx):
    t = frame_idx / FPS
    
    if t < 7.5:
        render_scene_1(ctx, t)
    elif t < 15.5:
        render_scene_2(ctx, t)
    elif t < 25.5:
        render_scene_3(ctx, t)
    elif t < 32.5:
        render_scene_4(ctx, t)
    elif t < 42.5:
        render_scene_5(ctx, t)
    elif t < 48.0:
        render_scene_6(ctx, t)
    elif t < 50.0:
        render_scene_7(ctx, t)
    elif t < 57.5:
        render_scene_8(ctx, t)
    elif t < 62.0:
        render_scene_9(ctx, t)
    elif t < 69.5:
        render_scene_10(ctx, t)
    elif t < 74.0:
        render_scene_11(ctx, t)
    elif t < 77.0:
        render_scene_12(ctx, t)
    else:
        render_scene_13(ctx, t)
        
    # Apply cinematic vignette overlay on all frames
    draw_vignette(ctx, intensity=0.35)

# -------------------------------------------------------------
# Main CLI & Video Pipeline
# -------------------------------------------------------------
if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "video"
    
    if mode == "preview":
        # Save sample keyframes across the 13 scenes
        os.makedirs(r"d:\Data\Agent Video\output", exist_ok=True)
        sample_times = [3.5, 11.5, 20.5, 29.0, 39.0, 45.0, 49.0, 55.0, 60.0, 66.0, 72.0, 75.5, 79.5]
        for idx, st in enumerate(sample_times):
            f_num = int(st * FPS)
            surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
            ctx = cairo.Context(surf)
            render_frame(ctx, f_num)
            out_png = rf"d:\Data\Agent Video\output\preview_scene_{idx+1}.png"
            surf.write_to_png(out_png)
            print(f"Saved preview: {out_png} (t={st:.1f}s)")
        print("All preview keyframes generated successfully!")
        
    elif mode == "video":
        os.makedirs(r"d:\Data\Agent Video\output", exist_ok=True)
        voiceover_file = r"d:\Data\Agent Video\audio\uss_squalus_voiceover.mp3"
        sfx_file = r"d:\Data\Agent Video\audio\sfx_track.wav"
        output_mp4 = r"d:\Data\Agent Video\output\uss_squalus_documentary.mp4"
        
        has_voice = bool(voiceover_file and os.path.exists(voiceover_file))
        has_sfx = bool(sfx_file and os.path.exists(sfx_file))

        ffmpeg_cmd = [
            "ffmpeg", "-y",
            "-f", "rawvideo",
            "-vcodec", "rawvideo",
            "-s", f"{W}x{H}",
            "-pix_fmt", "bgr24",
            "-r", str(FPS),
            "-i", "-", # stdin
        ]

        if has_voice and has_sfx:
            ffmpeg_cmd += [
                "-i", voiceover_file,
                "-i", sfx_file,
                "-filter_complex",
                "[1:a]volume=1.0[vocal]; [2:a]volume=0.55[sfx]; [vocal][sfx]amix=inputs=2:duration=longest[aout]",
                "-map", "0:v",
                "-map", "[aout]",
            ]
        elif has_voice:
            ffmpeg_cmd += [
                "-i", voiceover_file,
                "-map", "0:v",
                "-map", "1:a",
                "-c:a", "aac",
                "-b:a", "192k",
            ]
        elif has_sfx:
            ffmpeg_cmd += [
                "-i", sfx_file,
                "-map", "0:v",
                "-map", "1:a",
                "-c:a", "aac",
                "-b:a", "192k",
            ]
        else:
            ffmpeg_cmd += ["-map", "0:v"]

        ffmpeg_cmd += [
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-preset", "fast",
            "-crf", "19",
            "-shortest",
            output_mp4
        ]
        
        print("Launching FFmpeg pipeline...")
        proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)
        
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        ctx = cairo.Context(surf)
        
        print(f"Rendering {TOTAL_FRAMES} frames ({DURATION}s @ {FPS} fps)...")
        for f in range(TOTAL_FRAMES):
            render_frame(ctx, f)
            # Cairo ARGB32 on little-endian Windows stores [B, G, R, A]
            buf = np.frombuffer(surf.get_data(), dtype=np.uint8).reshape((H, W, 4))
            # Slice BGR
            bgr = buf[:, :, :3]
            proc.stdin.write(bgr.tobytes())
            
            if f % 150 == 0 or f == TOTAL_FRAMES - 1:
                pct = (f + 1) / TOTAL_FRAMES * 100.0
                print(f"Progress: frame {f+1}/{TOTAL_FRAMES} ({pct:.1f}%)")
                
        proc.stdin.close()
        proc.wait()
        print(f"Video rendered successfully: {output_mp4}")

