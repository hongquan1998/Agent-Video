import os
import sys
import math
import subprocess
import numpy as np
import cairo

# Ensure local imports work cleanly
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from components import (
    W, H, hex_rgb, rounded_rect, draw_vignette,
    draw_squalus_detailed, draw_watertight_door_detailed
)
from art_assets import (
    draw_naquin_cinematic, draw_control_room_background, draw_engine_room_flood, draw_telephone_station
)
from localization import T, get_font_for_lang

FPS = 30
DURATION = 81.9
TOTAL_FRAMES = int(DURATION * FPS)

# -------------------------------------------------------------
# SCENE 1: The Frigid Horizon (0.0s – 7.5s)
# -------------------------------------------------------------
def scene_1(ctx, t, lang="vi"):
    font = get_font_for_lang(lang)
    dolly = t * 14.0
    cam_y = math.sin(t * 0.45) * 8.0
    
    # Rich North Atlantic Dawn Sky
    sky = cairo.LinearGradient(0, 0, 0, 680)
    sky.add_color_stop_rgb(0.0, *hex_rgb("#182A36"))
    sky.add_color_stop_rgb(0.4, *hex_rgb("#3A5666"))
    sky.add_color_stop_rgb(0.75, *hex_rgb("#7D95A3"))
    sky.add_color_stop_rgb(1.0, *hex_rgb("#C0D0D9"))
    ctx.rectangle(0, 0, W, 680); ctx.set_source(sky); ctx.fill()
    
    # Morning Sun Glow piercing through overcast mist
    sun_pat = cairo.RadialGradient(1420, 280, 15, 1420, 280, 320)
    sun_pat.add_color_stop_rgba(0.0, 1.0, 0.98, 0.88, 0.55)
    sun_pat.add_color_stop_rgba(0.5, 1.0, 0.95, 0.80, 0.22)
    sun_pat.add_color_stop_rgba(1.0, 1.0, 0.95, 0.80, 0.0)
    ctx.rectangle(0, 0, W, 680); ctx.set_source(sun_pat); ctx.fill()
    
    # 4 Layers of Oceanic Swells (2°C North Atlantic Deep Water)
    swells = [
        (540 + cam_y * 0.2, 9.0, 0.9, "#254857", 0.004),
        (610 + cam_y * 0.5, 15.0, 1.3, "#1A3A47", 0.005),
        (700 + cam_y * 0.8, 22.0, 1.8, "#122A34", 0.006),
        (810 + cam_y * 1.1, 28.0, 2.3, "#081820", 0.007),
    ]
    for layer, (base_y, amp, speed, col, freq) in enumerate(swells):
        ctx.new_path()
        ctx.move_to(0, H); ctx.line_to(0, base_y)
        for x in range(0, W + 30, 30):
            sw = amp * math.sin((x + dolly * (layer + 1) * 2.5) * freq + t * speed)
            ctx.line_to(x, base_y + sw)
        ctx.line_to(W, H); ctx.close_path()
        ctx.set_source_rgb(*hex_rgb(col)); ctx.fill()
        
        # Crest highlights & sea foam lines
        ctx.set_line_width(2.2)
        ctx.set_source_rgba(0.88, 0.96, 1.0, 0.32 + layer * 0.05)
        for x in range(20, W, 120):
            fx = (x + dolly * (layer + 1) * 4) % W
            fy = base_y + amp * math.sin((fx + dolly * (layer + 1) * 2.5) * freq + t * speed)
            ctx.arc(fx, fy - 1, 15, 0.2, math.pi - 0.2); ctx.stroke()

    # Volumetric Sea Fog
    for i, (fy, speed, op) in enumerate([(500, 35, 0.25), (610, 65, 0.30), (740, 95, 0.22)]):
        offset = (t * speed) % (W + 600) - 300
        pat_fog = cairo.LinearGradient(offset, fy, offset + 600, fy + 160)
        pat_fog.add_color_stop_rgba(0.0, 0.88, 0.94, 0.98, 0.0)
        pat_fog.add_color_stop_rgba(0.5, 0.88, 0.94, 0.98, op)
        pat_fog.add_color_stop_rgba(1.0, 0.88, 0.94, 0.98, 0.0)
        ctx.rectangle(0, fy - 70, W, 240); ctx.set_source(pat_fog); ctx.fill()

    # Title Card
    if t >= 0.8:
        alpha = min(1.0, (t - 0.8) / 1.2)
        if t > 6.2: alpha = max(0.0, 1.0 - (t - 6.2) / 1.0)
        ctx.save()
        ctx.set_source_rgba(0.96, 0.98, 1.0, alpha * 0.95)
        ctx.select_font_face(font, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(34); ctx.move_to(160, 410)
        ctx.show_text(T("s1_date", lang))
        
        ctx.set_source_rgba(0.82, 0.92, 0.98, alpha * 0.85)
        ctx.set_font_size(22); ctx.move_to(160, 455)
        ctx.show_text(T("s1_loc", lang))
        ctx.restore()

# -------------------------------------------------------------
# SCENE 2: The Emergence of Squalus (7.5s – 15.5s)
# -------------------------------------------------------------
def scene_2(ctx, t, lang="vi"):
    font = get_font_for_lang(lang)
    st = t - 7.5
    cam_x = -140 + st * 60.0
    sub_y = 560 + math.sin(st * 0.9) * 7.5
    
    sky = cairo.LinearGradient(0, 0, 0, 600)
    sky.add_color_stop_rgb(0.0, *hex_rgb("#233644"))
    sky.add_color_stop_rgb(1.0, *hex_rgb("#6E8896"))
    ctx.rectangle(0, 0, W, 600); ctx.set_source(sky); ctx.fill()
    
    sea = cairo.LinearGradient(0, 520, 0, H)
    sea.add_color_stop_rgb(0.0, *hex_rgb("#16323D"))
    sea.add_color_stop_rgb(1.0, *hex_rgb("#08151D"))
    ctx.rectangle(0, 520, W, H - 520); ctx.set_source(sea); ctx.fill()
    
    draw_squalus_detailed(ctx, 960 + cam_x * 0.35, sub_y, scale=1.35)
    
    # Bow Wave with foam spray
    bow_x = 960 + cam_x * 0.35 + 480 * 1.35
    ctx.set_source_rgba(0.92, 0.96, 1.0, 0.85)
    for bx in range(int(bow_x - 40), int(bow_x + 130), 10):
        by = sub_y + math.sin(bx * 0.12 + st * 9.0) * 9.0
        ctx.arc(bx, by, 7.5, 0, 2 * math.pi); ctx.fill()
        
    # Diesel exhaust puffs
    exhaust_x = 960 + cam_x * 0.35 - 340 * 1.35
    for p in range(5):
        pt = (st * 3.2 + p * 0.3) % 1.5
        px = exhaust_x - pt * 140
        py = sub_y - 85 - pt * 65 + math.sin(pt * 6) * 10
        ctx.set_source_rgba(0.35, 0.38, 0.40, max(0.0, (1.0 - pt / 1.5) * 0.45))
        ctx.arc(px, py, 14 + pt * 38, 0, 2 * math.pi); ctx.fill()
        
    # Foreground Waves
    for w_i in range(3):
        ctx.new_path(); ctx.move_to(0, H)
        fy = 590 + w_i * 80
        ctx.line_to(0, fy)
        for x in range(0, W + 40, 40):
            wy = fy + 16.0 * math.sin(x * 0.007 + st * (1.8 + w_i * 0.4))
            ctx.line_to(x, wy)
        ctx.line_to(W, H); ctx.close_path()
        ctx.set_source_rgba(0.06, 0.18, 0.24, 0.65 + w_i * 0.15); ctx.fill()

    alpha = min(1.0, st / 1.0)
    if st > 6.5: alpha = max(0.0, 1.0 - (st - 6.5) / 1.0)
    ctx.save()
    ctx.set_source_rgba(1.0, 1.0, 1.0, alpha * 0.95)
    ctx.select_font_face(font, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(38); ctx.move_to(180, 240); ctx.show_text(T("s2_title", lang))
    ctx.set_source_rgba(0.85, 0.92, 0.98, alpha * 0.85)
    ctx.set_font_size(22); ctx.move_to(180, 285)
    ctx.show_text(T("s2_sub", lang))
    ctx.restore()

# -------------------------------------------------------------
# SCENE 3: 59 Souls & Commander Naquin (15.5s – 25.5s)
# -------------------------------------------------------------
def scene_3(ctx, t, lang="vi"):
    font = get_font_for_lang(lang)
    st = t - 15.5
    zoom = 1.0 + st * 0.012
    ctx.save()
    ctx.translate(W / 2, H / 2)
    ctx.scale(zoom, zoom)
    ctx.translate(-W / 2, -H / 2)
    
    # 1. Dark Atmospheric Control Room Background
    draw_control_room_background(ctx, t, emergency_red=False)
    
    # 2. Authentic Brass Circular Pressure & Depth Gauges
    gauges = [
        (640, 310, 68, T("s3_gauge_1", lang)),
        (820, 270, 85, T("s3_gauge_2", lang)),
        (1010, 310, 68, T("s3_gauge_3", lang)),
    ]
    for gi, (gx, gy, gr, gtitle) in enumerate(gauges):
        # Outer heavy brass bezel
        ctx.set_source_rgb(*hex_rgb("#A67C1E"))
        ctx.arc(gx, gy, gr, 0, 2 * math.pi); ctx.fill()
        ctx.set_source_rgb(*hex_rgb("#D4AF37"))
        ctx.arc(gx, gy, gr - 5, 0, 2 * math.pi); ctx.fill()
        
        # Ivory dial face
        ctx.set_source_rgb(*hex_rgb("#F4EEDD"))
        ctx.arc(gx, gy, gr - 12, 0, 2 * math.pi); ctx.fill()
        
        # Tick marks
        ctx.set_source_rgb(0.15, 0.15, 0.15); ctx.set_line_width(2.0)
        for ang_i in range(12):
            rad = math.radians(ang_i * 30)
            ctx.move_to(gx + (gr - 25) * math.cos(rad), gy + (gr - 25) * math.sin(rad))
            ctx.line_to(gx + (gr - 15) * math.cos(rad), gy + (gr - 15) * math.sin(rad)); ctx.stroke()
        
        ctx.select_font_face(font, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(15); ctx.move_to(gx - 45, gy - 35); ctx.show_text(gtitle)
        
        needle_ang = math.radians(205 + math.sin(st * 2.0 + gi) * 18)
        ctx.set_source_rgb(0.85, 0.1, 0.1); ctx.set_line_width(3.5)
        ctx.move_to(gx, gy)
        ctx.line_to(gx + (gr - 28) * math.cos(needle_ang), gy + (gr - 28) * math.sin(needle_ang)); ctx.stroke()
        ctx.arc(gx, gy, 8, 0, 2 * math.pi); ctx.fill()
        
        # Glass reflection glint
        pat_glint = cairo.LinearGradient(gx - gr, gy - gr, gx + gr, gy + gr)
        pat_glint.add_color_stop_rgba(0.0, 1, 1, 1, 0.35)
        pat_glint.add_color_stop_rgba(0.4, 1, 1, 1, 0.0)
        ctx.set_source(pat_glint); ctx.arc(gx, gy, gr - 12, 0, 2 * math.pi); ctx.fill()

    # 3. Helmsman Silhouette at the Big Wheel
    ctx.save()
    ctx.translate(340, 720)
    ctx.set_source_rgb(0.06, 0.09, 0.12)
    ctx.arc(0, -120, 85, 0, 2 * math.pi); ctx.set_line_width(16); ctx.stroke()
    ctx.arc(-20, -180, 45, 0, 2 * math.pi); ctx.fill()
    ctx.rectangle(-70, -135, 140, 320); ctx.fill()
    ctx.restore()

    # 4. Cinematic Portrait of Lieutenant Oliver Naquin
    draw_naquin_cinematic(ctx, 1080, 480, scale=1.18, expression="determined", t=st)
    
    # Cold breath vapor
    bv_alpha = (0.5 + 0.5 * math.sin(st * 2.5)) * 0.35
    ctx.set_source_rgba(0.9, 0.95, 1.0, bv_alpha)
    ctx.arc(1140 + (st * 18) % 60, 540 - (st * 10) % 35, 24, 0, 2 * math.pi); ctx.fill()

    ctx.restore()
    
    # Caption Banner
    alpha = min(1.0, st / 1.0)
    if st > 8.5: alpha = max(0.0, 1.0 - (st - 8.5) / 1.0)
    ctx.save()
    ctx.set_source_rgba(0.95, 0.95, 0.95, alpha * 0.95)
    ctx.select_font_face(font, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(32); ctx.move_to(160, 960); ctx.show_text(T("s3_title", lang))
    ctx.set_font_size(22); ctx.set_source_rgba(0.8, 0.85, 0.9, alpha * 0.85)
    ctx.move_to(160, 1000); ctx.show_text(T("s3_sub", lang))
    ctx.restore()

# -------------------------------------------------------------
# SCENE 4: The Dive Klaxon & Engine Silence (25.5s – 32.5s)
# -------------------------------------------------------------
def scene_4(ctx, t, lang="vi"):
    font = get_font_for_lang(lang)
    st = t - 25.5
    shake_x = math.sin(st * 45) * 5.0 if (0.5 < st < 3.2) else 0.0
    shake_y = math.cos(st * 50) * 5.0 if (0.5 < st < 3.2) else 0.0
    
    ctx.save()
    ctx.translate(shake_x, shake_y)
    
    if st < 3.5:
        # Giant Brass Klaxon Horn Close-up
        ctx.set_source_rgb(*hex_rgb("#090E12")); ctx.rectangle(0, 0, W, H); ctx.fill()
        
        # Klaxon Flare
        flare = cairo.RadialGradient(680, 500, 40, 680, 500, 480)
        flare.add_color_stop_rgb(0.0, *hex_rgb("#D4AF37"))
        flare.add_color_stop_rgb(0.7, *hex_rgb("#856214"))
        flare.add_color_stop_rgb(1.0, *hex_rgb("#241A04"))
        ctx.arc(680, 500, 420, 0, 2 * math.pi); ctx.set_source(flare); ctx.fill()
        
        # Sound Shockwaves
        for i in range(4):
            sw_r = ((st * 4.2 + i * 0.5) % 2.0) * 220 + 80
            ctx.set_source_rgba(1.0, 0.85, 0.3, max(0.0, 0.8 - sw_r / 500))
            ctx.set_line_width(6.0)
            ctx.arc(680, 500, sw_r, -0.6, 0.6); ctx.stroke()
        
        # Engine Order Telegraph
        ctx.set_source_rgb(*hex_rgb("#CD7F32"))
        ctx.arc(1360, 450, 230, 0, 2 * math.pi); ctx.fill()
        ctx.set_source_rgb(*hex_rgb("#F7F1E1"))
        ctx.arc(1360, 450, 205, 0, 2 * math.pi); ctx.fill()
        
        ctx.set_source_rgb(0.1, 0.1, 0.1)
        ctx.select_font_face(font, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(24); ctx.move_to(1320, 290); ctx.show_text(T("s4_telegraph_stop", lang))
        ctx.move_to(1440, 360); ctx.show_text(T("s4_telegraph_ahead", lang))
        ctx.move_to(1220, 360); ctx.show_text(T("s4_telegraph_back", lang))
        ctx.set_source_rgb(0.85, 0.1, 0.1)
        ctx.set_font_size(32); ctx.move_to(1325, 590); ctx.show_text(T("s4_telegraph_dive", lang))
        
        # Telegraph Handle Pulled Down
        handle_ang = math.radians(20 + min(130.0, st * 75.0))
        ctx.set_source_rgb(0.85, 0.12, 0.1)
        ctx.set_line_width(20.0)
        ctx.move_to(1360, 450)
        ctx.line_to(1360 + 245 * math.cos(handle_ang), 450 + 245 * math.sin(handle_ang)); ctx.stroke()
        ctx.arc(1360, 450, 28, 0, 2 * math.pi); ctx.fill()
        
        ctx.set_source_rgba(1, 1, 1, 0.95)
        ctx.select_font_face(font, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(42); ctx.move_to(450, 820); ctx.show_text(T("s4_caption", lang))
    else:
        sink_pct = (st - 3.5) / 3.5
        sub_y = 480 + sink_pct * 190
        
        ctx.set_source_rgb(*hex_rgb("#14323E"))
        ctx.rectangle(0, 0, W, H); ctx.fill()
        draw_squalus_detailed(ctx, 960, sub_y, scale=1.35)
        
        ctx.set_source_rgba(0.85, 0.95, 1.0, 0.75)
        for fx in range(180, 1740, 28):
            fy = 520 + math.sin(fx * 0.02 + st * 12) * 22
            ctx.arc(fx, fy, 15, 0, 2 * math.pi); ctx.fill()
            
    ctx.restore()

# -------------------------------------------------------------
# SCENE 5: The "Christmas Tree" Board (32.5s – 42.5s)
# -------------------------------------------------------------
def scene_5(ctx, t, lang="vi"):
    font = get_font_for_lang(lang)
    st = t - 32.5
    zoom = 1.0 + st * 0.025
    ctx.save()
    ctx.translate(W / 2, H / 2)
    ctx.scale(zoom, zoom)
    ctx.translate(-W / 2, -H / 2)
    
    ctx.set_source_rgb(*hex_rgb("#0C1318")); ctx.rectangle(0, 0, W, H); ctx.fill()
    
    # Board Console Housing
    rounded_rect(ctx, 320, 150, 1280, 780, 30)
    ctx.set_source_rgb(*hex_rgb("#182228")); ctx.fill_preserve()
    ctx.set_source_rgb(*hex_rgb("#2A3740")); ctx.set_line_width(8.0); ctx.stroke()
    
    ctx.set_source_rgba(0.9, 0.9, 0.9, 0.9)
    ctx.select_font_face(font, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(32); ctx.move_to(680, 220); ctx.show_text(T("s5_title", lang))
    
    turn_green = st >= 5.5
    
    for row in range(2):
        for col in range(8):
            lx = 480 + col * 135
            ly = 380 + row * 220
            
            # Brass bezel
            ctx.set_source_rgb(*hex_rgb("#CD7F32"))
            ctx.arc(lx, ly, 46, 0, 2 * math.pi); ctx.fill()
            
            col_hex = "#2ED573" if turn_green else "#FF4757"
            ctx.set_source_rgb(*hex_rgb(col_hex))
            ctx.arc(lx, ly, 38, 0, 2 * math.pi); ctx.fill()
            
            pat = cairo.RadialGradient(lx, ly, 20, lx, ly, 105)
            r, g, b = hex_rgb(col_hex)
            pat.add_color_stop_rgba(0.0, r, g, b, 0.65)
            pat.add_color_stop_rgba(1.0, r, g, b, 0.0)
            ctx.arc(lx, ly, 105, 0, 2 * math.pi)
            ctx.set_source(pat); ctx.fill()
            
            lbl = f"V-{row*8 + col + 1}"
            if row == 1 and col == 4:
                lbl = T("s5_valve_1", lang)
            ctx.set_source_rgba(0.85, 0.85, 0.85, 0.8)
            ctx.select_font_face(font, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            ctx.set_font_size(15); ctx.move_to(lx - 28, ly + 68); ctx.show_text(lbl)

    ctx.restore()
    
    if turn_green:
        ctx.save()
        ctx.set_source_rgba(0.3, 1.0, 0.5, 0.95)
        ctx.select_font_face(font, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(34); ctx.move_to(540, 990); ctx.show_text(T("s5_confirm", lang))
        ctx.restore()

# -------------------------------------------------------------
# SCENE 6: 15-Meter Descent (42.5s – 48.0s)
# -------------------------------------------------------------
def scene_6(ctx, t, lang="vi"):
    font = get_font_for_lang(lang)
    st = t - 42.5
    ctx.set_source_rgb(*hex_rgb("#08202B")); ctx.rectangle(0, 0, W, H); ctx.fill()
    
    for bi in range(6):
        bx = 200 + bi * 280 + math.sin(st * 0.8 + bi) * 50
        pat = cairo.LinearGradient(bx, 0, bx + 160, H)
        pat.add_color_stop_rgba(0.0, 0.3, 0.7, 0.9, 0.12)
        pat.add_color_stop_rgba(1.0, 0.1, 0.3, 0.5, 0.0)
        ctx.rectangle(bx, 0, 160, H); ctx.set_source(pat); ctx.fill()
        
    ctx.save()
    ctx.translate(960 + st * 22, 540 + math.sin(st * 0.6) * 14)
    ctx.rotate(math.radians(8.5))
    draw_squalus_detailed(ctx, 0, 0, scale=1.25)
    ctx.restore()
    
    # Depth Gauge
    ctx.save()
    ctx.translate(1620, 240)
    ctx.set_source_rgb(*hex_rgb("#CD7F32")); ctx.arc(0, 0, 125, 0, 2 * math.pi); ctx.fill()
    ctx.set_source_rgb(*hex_rgb("#EDE8D5")); ctx.arc(0, 0, 110, 0, 2 * math.pi); ctx.fill()
    ctx.set_source_rgb(0.1, 0.1, 0.1)
    ctx.select_font_face(font, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(20); ctx.move_to(-52, -45); ctx.show_text(T("s6_depth_unit", lang))
    deg = 180 + min(120.0, st * 25.0)
    rad = math.radians(deg)
    ctx.set_source_rgb(0.85, 0.1, 0.1); ctx.set_line_width(4.5)
    ctx.move_to(0, 0); ctx.line_to(90 * math.cos(rad), 90 * math.sin(rad)); ctx.stroke()
    ctx.arc(0, 0, 10, 0, 2 * math.pi); ctx.fill()
    ctx.restore()

    ctx.save()
    ctx.set_source_rgba(0.9, 0.95, 1.0, 0.85)
    ctx.select_font_face(font, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(30); ctx.move_to(180, 960)
    ctx.show_text(T("s6_caption", lang))
    ctx.restore()

# -------------------------------------------------------------
# SCENE 7: The Lie (48.0s – 50.0s)
# -------------------------------------------------------------
def scene_7(ctx, t, lang="vi"):
    font = get_font_for_lang(lang)
    st = t - 48.0
    ctx.set_source_rgb(*hex_rgb("#060A0D")); ctx.rectangle(0, 0, W, H); ctx.fill()
    
    flicker = (math.sin(st * 40) > 0.25)
    shake_y = math.sin(st * 60) * 3.5
    
    ctx.save()
    ctx.translate(W / 2, H / 2 + shake_y)
    
    ctx.set_source_rgb(*hex_rgb("#A56728")); ctx.arc(0, 0, 230, 0, 2 * math.pi); ctx.fill()
    col = hex_rgb("#2ED573") if not flicker else hex_rgb("#E74C3C")
    ctx.set_source_rgb(*col); ctx.arc(0, 0, 190, 0, 2 * math.pi); ctx.fill()
    
    pat = cairo.RadialGradient(0, 0, 60, 0, 0, 520)
    pat.add_color_stop_rgba(0.0, col[0], col[1], col[2], 0.75)
    pat.add_color_stop_rgba(1.0, col[0], col[1], col[2], 0.0)
    ctx.set_source(pat); ctx.arc(0, 0, 520, 0, 2 * math.pi); ctx.fill()
    ctx.restore()
    
    ctx.save()
    ctx.set_source_rgba(1.0, 0.25, 0.25, min(1.0, st * 1.5))
    ctx.select_font_face(font, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(46); ctx.move_to(520, 920); ctx.show_text(T("s7_warning", lang))
    ctx.restore()

# -------------------------------------------------------------
# SCENE 8: The 80cm Valve Rupture (50.0s – 57.5s)
# -------------------------------------------------------------
def scene_8(ctx, t, lang="vi"):
    font = get_font_for_lang(lang)
    st = t - 50.0
    vibe = min(24.0, st * 3.6)
    shake_x = np.random.uniform(-vibe, vibe)
    shake_y = np.random.uniform(-vibe, vibe)
    
    ctx.set_source_rgb(*hex_rgb("#0A1218")); ctx.rectangle(0, 0, W, H); ctx.fill()
    
    ctx.save()
    ctx.translate(W / 2 + shake_x, H / 2 + shake_y)
    
    # 80cm Massive Main Induction Pipe
    ctx.set_source_rgb(*hex_rgb("#1D2830"))
    ctx.arc(0, 0, 340, 0, 2 * math.pi); ctx.fill()
    ctx.set_source_rgb(*hex_rgb("#34434E"))
    ctx.arc(0, 0, 310, 0, 2 * math.pi); ctx.set_line_width(28); ctx.stroke()
    
    # Hydraulic Piston Arm
    ctx.set_source_rgb(*hex_rgb("#63727E"))
    ctx.rectangle(-45, -280, 90, 220); ctx.fill()
    
    # Valve Flap
    valve_rot = 0.0 if st < 3.8 else min(78.0, (st - 3.8) * 110.0)
    ctx.save()
    ctx.translate(0, -180)
    ctx.rotate(math.radians(valve_rot))
    
    ctx.set_source_rgb(*hex_rgb("#12191E"))
    ctx.rectangle(-260, -25, 520, 50); ctx.fill()
    ctx.set_source_rgb(*hex_rgb("#8A9BA8"))
    ctx.rectangle(-260, -25, 520, 50); ctx.set_line_width(6); ctx.stroke()
    
    if st >= 3.8:
        # High Pressure Water Jet bursting past open seal
        ctx.set_source_rgba(0.7, 0.9, 1.0, 0.85)
        for sp in range(35):
            sx = np.random.uniform(-190, 190)
            sy = np.random.uniform(-190, 190)
            ctx.arc(sx, sy, np.random.uniform(15, 65), 0, 2 * math.pi); ctx.fill()
            
        ctx.set_source_rgb(1.0, 0.82, 0.2)
        for rx, ry in [(260, 110), (-250, -130), (130, -270)]:
            ctx.arc(rx + (st - 4.0) * 450, ry + (st - 4.0) * 380, 9, 0, 2 * math.pi); ctx.fill()
            
    ctx.restore()
    ctx.restore()
    
    ctx.save()
    ctx.set_source_rgba(1.0, 0.3, 0.2, 0.95)
    ctx.select_font_face(font, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(32); ctx.move_to(160, 960)
    ctx.show_text(T("s8_catastrophe", lang))
    ctx.restore()

# -------------------------------------------------------------
# SCENE 9: The Ice Deluge (57.5s – 62.0s)
# -------------------------------------------------------------
def scene_9(ctx, t, lang="vi"):
    draw_engine_room_flood(ctx, t)

# -------------------------------------------------------------
# SCENE 10: The Screaming Telephone (62.0s – 69.5s)
# -------------------------------------------------------------
def scene_10(ctx, t, lang="vi"):
    font = get_font_for_lang(lang)
    st = t - 62.0
    strobe_red = (math.sin(st * 8.5) > 0.0)
    
    draw_control_room_background(ctx, t, emergency_red=strobe_red)
    phone_vibe = math.sin(st * 45) * 6.0 if st < 4.5 else 0.0
    draw_telephone_station(ctx, 520, 470, vibe=phone_vibe)
    draw_naquin_cinematic(ctx, 1260, 480, scale=1.28, expression="horror", t=st)
    
    ctx.save()
    ctx.set_source_rgba(1.0, 0.25, 0.25, 0.98)
    ctx.select_font_face(font, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(44); ctx.move_to(180, 890)
    ctx.show_text(T("s10_shout", lang))
    ctx.restore()

# -------------------------------------------------------------
# SCENE 11: Dragged into the Abyss (69.5s – 74.0s)
# -------------------------------------------------------------
def scene_11(ctx, t, lang="vi"):
    font = get_font_for_lang(lang)
    st = t - 69.5
    ctx.set_source_rgb(*hex_rgb("#02060A")); ctx.rectangle(0, 0, W, H); ctx.fill()
    
    sink_angle = 16.0 + st * 7.5
    sub_x = 960 - st * 40
    sub_y = 480 + st * 55
    
    ctx.save()
    ctx.translate(sub_x, sub_y)
    ctx.rotate(math.radians(-sink_angle))
    draw_squalus_detailed(ctx, 0, 0, scale=1.12)
    ctx.restore()
    
    bubble_x = sub_x - 390
    bubble_y = sub_y + 120
    ctx.set_source_rgba(0.5, 0.8, 0.95, 0.65)
    for bi in range(70):
        bx = bubble_x + np.random.uniform(-150, 150)
        by = bubble_y - np.random.uniform(0, 650)
        ctx.arc(bx, by, np.random.uniform(8, 30), 0, 2 * math.pi); ctx.fill()

    draw_vignette(ctx, intensity=0.7)

    ctx.save()
    ctx.set_source_rgba(0.9, 0.95, 1.0, 0.85)
    ctx.select_font_face(font, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(32); ctx.move_to(200, 960)
    ctx.show_text(T("s11_abyss", lang))
    ctx.restore()

# -------------------------------------------------------------
# SCENE 12: The 45-Degree Tilt (74.0s – 77.0s)
# -------------------------------------------------------------
def scene_12(ctx, t, lang="vi"):
    font = get_font_for_lang(lang)
    st = t - 74.0
    ctx.save()
    ctx.translate(W / 2, H / 2)
    ctx.rotate(math.radians(-45.0))
    ctx.translate(-W / 2, -H / 2)
    
    ctx.set_source_rgb(*hex_rgb("#161212")); ctx.rectangle(-400, -400, W + 800, H + 800); ctx.fill()
    ctx.set_source_rgba(0.85, 0.1, 0.1, 0.28); ctx.rectangle(-400, -400, W + 800, H + 800); ctx.fill()
    ctx.set_source_rgb(*hex_rgb("#262D34")); ctx.rectangle(-400, 720, W + 800, 400); ctx.fill()
    
    for ti, (tx, ty, tr) in enumerate([(450, 680, 26), (820, 650, 42), (1200, 690, 20)]):
        slide = (st * 480 + ti * 180)
        ctx.set_source_rgb(*hex_rgb("#7D93A0"))
        ctx.rectangle(tx - slide, ty, tr * 2, tr); ctx.fill()

    # Sailor Clinging to Pipes
    ctx.save()
    ctx.translate(850 - st * 80, 620)
    ctx.set_source_rgb(0.08, 0.08, 0.08)
    ctx.arc(0, -60, 36, 0, 2 * math.pi); ctx.fill()
    ctx.rectangle(-36, -20, 72, 160); ctx.fill()
    ctx.set_line_width(24); ctx.move_to(0, 0); ctx.line_to(95, -115); ctx.stroke()
    ctx.restore()
    ctx.restore()
    
    ctx.save()
    ctx.set_source_rgba(1.0, 0.4, 0.4, 0.95)
    ctx.select_font_face(font, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(44); ctx.move_to(180, 220)
    ctx.show_text(T("s12_tilt", lang))
    ctx.restore()

# -------------------------------------------------------------
# SCENE 13: The Final Open Bulkhead Door (77.0s – 81.9s)
# -------------------------------------------------------------
def scene_13(ctx, t, lang="vi"):
    font = get_font_for_lang(lang)
    st = t - 77.0
    water_pct = min(1.0, st / 4.9)
    draw_watertight_door_detailed(ctx, t, water_pct=water_pct)
    
    ctx.save()
    ctx.set_source_rgba(1.0, 0.85, 0.85, min(1.0, st * 1.2))
    ctx.select_font_face(font, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(32); ctx.move_to(220, 990)
    ctx.show_text(T("s13_door", lang))
    ctx.restore()

    if st >= 3.2:
        fade = min(1.0, (st - 3.2) / 1.7)
        ctx.set_source_rgba(0, 0, 0, fade)
        ctx.rectangle(0, 0, W, H); ctx.fill()

# -------------------------------------------------------------
# Master Frame Dispatcher
# -------------------------------------------------------------
def render_frame(ctx, frame_idx, total_duration=81.9, fps=FPS, lang="vi"):
    t = frame_idx / fps
    scale_factor = 81.9 / total_duration if total_duration > 0 else 1.0
    norm_t = t * scale_factor
    
    if norm_t < 7.5:
        scene_1(ctx, norm_t, lang=lang)
    elif norm_t < 15.5:
        scene_2(ctx, norm_t, lang=lang)
    elif norm_t < 25.5:
        scene_3(ctx, norm_t, lang=lang)
    elif norm_t < 32.5:
        scene_4(ctx, norm_t, lang=lang)
    elif norm_t < 42.5:
        scene_5(ctx, norm_t, lang=lang)
    elif norm_t < 48.0:
        scene_6(ctx, norm_t, lang=lang)
    elif norm_t < 50.0:
        scene_7(ctx, norm_t, lang=lang)
    elif norm_t < 57.5:
        scene_8(ctx, norm_t, lang=lang)
    elif norm_t < 62.0:
        scene_9(ctx, norm_t, lang=lang)
    elif norm_t < 69.5:
        scene_10(ctx, norm_t, lang=lang)
    elif norm_t < 74.0:
        scene_11(ctx, norm_t, lang=lang)
    elif norm_t < 77.0:
        scene_12(ctx, norm_t, lang=lang)
    else:
        scene_13(ctx, norm_t, lang=lang)
        
    draw_vignette(ctx, intensity=0.35)

# -------------------------------------------------------------
# Preview Generation
# -------------------------------------------------------------
def generate_previews(output_dir=r"d:\Data\Agent Video\output", total_duration=81.9, fps=FPS, lang="vi"):
    os.makedirs(output_dir, exist_ok=True)
    sample_norm_times = [3.5, 11.5, 20.5, 29.0, 39.0, 45.0, 49.0, 55.0, 60.0, 66.0, 72.0, 75.5, 79.5]
    scale = total_duration / 81.9
    
    for idx, st in enumerate(sample_norm_times):
        actual_t = st * scale
        f_num = int(actual_t * fps)
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        ctx = cairo.Context(surf)
        render_frame(ctx, f_num, total_duration=total_duration, fps=fps, lang=lang)
        out_png = os.path.join(output_dir, f"cinematic_{lang}_preview_{idx+1}.png")
        surf.write_to_png(out_png)
        print(f"[Preview ({lang})] Saved: {out_png}")
    print(f"[Preview] All 13 preview plates ({lang}) generated successfully.")

# -------------------------------------------------------------
# Master Video Render Pipeline
# -------------------------------------------------------------
def render_cinematic_video(voiceover_file, sfx_file, output_mp4, duration=81.9, fps=FPS, lang="vi"):
    extra_paths = [
        r"C:\Users\Admin\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.2-full_build\bin",
        r"C:\Users\Admin\AppData\Local\Programs\Python\Python312"
    ]
    for p in extra_paths:
        if os.path.exists(p) and p not in os.environ.get("PATH", ""):
            os.environ["PATH"] = p + ";" + os.environ.get("PATH", "")

    total_frames = int(duration * fps)
    os.makedirs(os.path.dirname(output_mp4), exist_ok=True)

    has_voice = bool(voiceover_file and os.path.exists(voiceover_file))
    has_sfx = bool(sfx_file and os.path.exists(sfx_file))

    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{W}x{H}",
        "-pix_fmt", "bgr24",
        "-r", str(fps),
        "-i", "-", # Stdin video stream
    ]

    if has_voice and has_sfx:
        ffmpeg_cmd += [
            "-i", voiceover_file,
            "-i", sfx_file,
            "-filter_complex",
            "[1:a]volume=1.0[vocal]; [2:a]volume=0.62[sfx]; [vocal][sfx]amix=inputs=2:duration=longest[aout]",
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
        ffmpeg_cmd += [
            "-map", "0:v",
        ]

    ffmpeg_cmd += [
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "fast",
        "-crf", "18",
        "-shortest",
        output_mp4
    ]

    print(f"[Renderer] Launching FFmpeg pipeline: {output_mp4}")
    print(f"[Renderer] Language: {lang.upper()} | Target Duration: {duration:.2f}s | Total Frames: {total_frames} @ {fps} FPS")
    proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)

    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)

    for f in range(total_frames):
        render_frame(ctx, f, total_duration=duration, fps=fps, lang=lang)
        buf = np.frombuffer(surf.get_data(), dtype=np.uint8).reshape((H, W, 4))
        bgr = buf[:, :, :3]
        proc.stdin.write(bgr.tobytes())

        if f % 250 == 0 or f == total_frames - 1:
            pct = (f + 1) / total_frames * 100.0
            print(f"[Renderer] Progress: {f+1}/{total_frames} frames ({pct:.1f}%)")

    proc.stdin.close()
    proc.wait()
    print(f"[Renderer] Rendering Complete! Output saved to: {output_mp4}")
    return output_mp4

# -------------------------------------------------------------
# CLI Entrypoint
# -------------------------------------------------------------
if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "video"
    lang = sys.argv[2] if len(sys.argv) > 2 else "vi"
    output_dir = r"d:\Data\Agent Video\output"
    os.makedirs(output_dir, exist_ok=True)
    
    if mode == "preview":
        generate_previews(output_dir, lang=lang)
    elif mode == "video":
        voiceover_file = r"d:\Data\Agent Video\audio\uss_squalus_voiceover.mp3"
        sfx_file = r"d:\Data\Agent Video\audio\sfx_track.wav"
        output_mp4 = rf"d:\Data\Agent Video\output\uss_squalus_cinematic_{lang}.mp4"
        render_cinematic_video(voiceover_file, sfx_file, output_mp4, duration=81.9, fps=FPS, lang=lang)
