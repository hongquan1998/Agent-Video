# -*- coding: utf-8 -*-
"""
components.py
Thư viện Thành Phần Vector 2D Đa Dụng (General-Purpose 2D Vector Component Library).
Cung cấp các hàm vẽ hình học cơ bản, bộ đổ màu, hiệu ứng ánh sáng điện ảnh, hạt bụi,
thẻ giao diện (HUD Card), thước đo và các cấu trúc đồ họa tham số hóa dùng chung cho mọi chủ đề.
"""

import math
import numpy as np
import cairo

W, H = 1920, 1080

# ==============================================================================
# 1. HÀM MÀU SẮC & HÌNH HỌC NGUYÊN THỦY (COLOR & PRIMITIVES)
# ==============================================================================
def hex_rgb(h):
    """Chuyển mã Hex (#RRGGBB hoặc #RRGGBBAA) sang tuple (R, G, B) chuẩn hóa [0.0 - 1.0]."""
    if not isinstance(h, str):
        return (1.0, 1.0, 1.0)
    h = h.lstrip("#")
    if len(h) == 6:
        return tuple(int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))
    elif len(h) == 8:
        return tuple(int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))
    return (1.0, 1.0, 1.0)

def hex_rgba(h, alpha=1.0):
    """Chuyển mã Hex sang tuple (R, G, B, A) chuẩn hóa [0.0 - 1.0]."""
    r, g, b = hex_rgb(h)
    return (r, g, b, alpha)

def stroke_and_fill(ctx, fill_hex=None, stroke_hex="#12171C", lw=2.4, alpha=1.0):
    """Tô màu phẳng và viền nét mềm mại cho đường path hiện tại."""
    if fill_hex is not None:
        r, g, b = hex_rgb(fill_hex) if isinstance(fill_hex, str) else fill_hex[:3]
        ctx.set_source_rgba(r, g, b, alpha)
        if stroke_hex is not None and lw > 0:
            ctx.fill_preserve()
        else:
            ctx.fill()
    if stroke_hex is not None and lw > 0:
        sr, sg, sb = hex_rgb(stroke_hex) if isinstance(stroke_hex, str) else stroke_hex[:3]
        ctx.set_source_rgba(sr, sg, sb, alpha)
        ctx.set_line_width(lw)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.stroke()

def rounded_rect(ctx, x, y, w, h, r):
    """Tạo đường path hình chữ nhật bo tròn 4 góc an toàn."""
    r = min(r, abs(w) / 2.0, abs(h) / 2.0)
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    ctx.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
    ctx.close_path()

def draw_circle(ctx, cx, cy, r, fill_hex=None, stroke_hex=None, lw=2.0, alpha=1.0):
    """Vẽ hình tròn tâm (cx, cy) với bán kính r."""
    ctx.new_sub_path()
    ctx.arc(cx, cy, max(0.5, r), 0, 2 * math.pi)
    stroke_and_fill(ctx, fill_hex, stroke_hex, lw=lw, alpha=alpha)

def draw_capsule(ctx, x, y, w, h, fill_hex=None, stroke_hex=None, lw=2.0, vertical=False):
    """Vẽ hình viên thuốc (capsule / pill) nằm ngang hoặc dọc."""
    r = (w / 2.0) if vertical else (h / 2.0)
    rounded_rect(ctx, x, y, w, h, r)
    stroke_and_fill(ctx, fill_hex, stroke_hex, lw=lw)

def draw_polygon(ctx, points, fill_hex=None, stroke_hex="#12171C", lw=2.0, alpha=1.0):
    """Vẽ đa giác từ danh sách các điểm [(x1, y1), (x2, y2), ...]."""
    if not points or len(points) < 3:
        return
    ctx.new_path()
    ctx.move_to(points[0][0], points[0][1])
    for px, py in points[1:]:
        ctx.line_to(px, py)
    ctx.close_path()
    stroke_and_fill(ctx, fill_hex, stroke_hex, lw=lw, alpha=alpha)

def draw_star(ctx, cx, cy, points=5, r_outer=24, r_inner=12, fill_hex="#F59E0B", stroke_hex=None, lw=1.5):
    """Vẽ ngôi sao đối xứng đa cánh (phù hợp cho xếp hạng, mốc thành tựu)."""
    ctx.new_path()
    step = math.pi / points
    for i in range(2 * points):
        r = r_outer if i % 2 == 0 else r_inner
        ang = i * step - math.pi / 2
        px = cx + r * math.cos(ang)
        py = cy + r * math.sin(ang)
        if i == 0:
            ctx.move_to(px, py)
        else:
            ctx.line_to(px, py)
    ctx.close_path()
    stroke_and_fill(ctx, fill_hex, stroke_hex, lw=lw)

def draw_dashed_line(ctx, x1, y1, x2, y2, dashes=[10.0, 8.0], col="#94A3B8", lw=2.0):
    """Vẽ đường nét đứt đo đạc hoặc phân cách."""
    ctx.save()
    ctx.set_source_rgba(*hex_rgba(col))
    ctx.set_line_width(lw)
    ctx.set_dash(dashes)
    ctx.move_to(x1, y1)
    ctx.line_to(x2, y2)
    ctx.stroke()
    ctx.restore()


# ==============================================================================
# 2. HIỆU ỨNG ÁNH SÁNG & KHÍ QUYỂN ĐIỆN ẢNH (ATMOSPHERE & CINEMATIC FX)
# ==============================================================================
def draw_vignette(ctx, intensity=0.42, width=W, height=H, color=(0, 0, 0)):
    """Vẽ hiệu ứng làm tối 4 góc màn hình (Vignette) tạo chiều sâu điện ảnh."""
    ctx.save()
    rad = math.hypot(width, height) / 1.6
    pat = cairo.RadialGradient(width / 2, height / 2, rad * 0.35, width / 2, height / 2, rad)
    r, g, b = color[:3]
    pat.add_color_stop_rgba(0.0, r, g, b, 0.0)
    pat.add_color_stop_rgba(1.0, r, g, b, intensity)
    ctx.rectangle(0, 0, width, height)
    ctx.set_source(pat)
    ctx.fill()
    ctx.restore()

def draw_cinematic_bars(ctx, bar_height=70, width=W, height=H, color=(0, 0, 0)):
    """Vẽ thanh đen trên và dưới chuẩn khung hình phim nhựa (Letterbox)."""
    ctx.save()
    ctx.set_source_rgb(*color[:3])
    ctx.rectangle(0, 0, width, bar_height)
    ctx.rectangle(0, height - bar_height, width, bar_height)
    ctx.fill()
    ctx.restore()

def draw_particles_floating(ctx, t, count=35, width=W, height=H, col="#FFFFFF", speed_x=8.0, speed_y=-16.0):
    """Vẽ các hạt bụi / đốm sáng lơ lửng chuyển động chậm trong không khí."""
    ctx.save()
    r, g, b = hex_rgb(col)
    for i in range(count):
        seed_x = (i * 137.5) % width
        seed_y = (i * 91.3) % height
        cur_x = (seed_x + t * speed_x + 15 * math.sin(t * 0.8 + i)) % width
        cur_y = (seed_y + t * speed_y) % height
        rad = 1.6 + (i % 3) * 0.9
        alpha = 0.15 + 0.18 * math.sin(t * 1.5 + i * 2.0)
        ctx.arc(cur_x, cur_y, rad, 0, 2 * math.pi)
        ctx.set_source_rgba(r, g, b, alpha)
        ctx.fill()
    ctx.restore()

def draw_volumetric_light_cone(ctx, x1, y1, x2, y2, spread=160, col=(1.0, 0.95, 0.8), max_alpha=0.32):
    """Vẽ luồng sáng hình nón rọi xuống mặt sàn / bàn làm việc (Volumetric Light Cone)."""
    ctx.save()
    cone_g = cairo.LinearGradient(x1, y1, x2, y2)
    r, g, b = col[:3]
    cone_g.add_color_stop_rgba(0.0, r, g, b, max_alpha)
    cone_g.add_color_stop_rgba(1.0, r, g, b, 0.0)

    ctx.move_to(x1 - spread * 0.15, y1)
    ctx.line_to(x1 + spread * 0.15, y1)
    ctx.line_to(x2 + spread, y2)
    ctx.line_to(x2 - spread, y2)
    ctx.close_path()
    ctx.set_source(cone_g)
    ctx.fill()
    ctx.restore()

def draw_radial_glow(ctx, cx, cy, radius, col=(1.0, 1.0, 1.0), alpha=0.45):
    """Vẽ vầng hào quang phát sáng lan tỏa xung quanh một điểm hoặc bóng đèn."""
    ctx.save()
    pat = cairo.RadialGradient(cx, cy, radius * 0.05, cx, cy, radius)
    r, g, b = col[:3]
    pat.add_color_stop_rgba(0.0, r, g, b, alpha)
    pat.add_color_stop_rgba(1.0, r, g, b, 0.0)
    ctx.arc(cx, cy, radius, 0, 2 * math.pi)
    ctx.set_source(pat)
    ctx.fill()
    ctx.restore()


# ==============================================================================
# 3. THÀNH PHẦN GIAO DIỆN & INFOGRAPHIC DÙNG CHUNG (UI & HUD CARDS)
# ==============================================================================
def draw_card_panel(ctx, x, y, w, h, bg_hex="#0F172A", border_hex="#38BDF8", alpha=0.92, r=12, lw=2.4):
    """Vẽ khung bảng thông tin kính mờ bo tròn (Glassmorphism card)."""
    rounded_rect(ctx, x, y, w, h, r)
    stroke_and_fill(ctx, bg_hex, border_hex, lw=lw, alpha=alpha)

def draw_badge(ctx, x, y, text, bg_hex="#F59E0B", text_hex="#0F172A", r=6, font_size=15):
    """Vẽ nhãn huy hiệu nhỏ gọn (Badge / Tag) nổi bật."""
    ctx.save()
    ctx.select_font_face("Segoe UI", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(font_size)
    _, _, width, height, _, _ = ctx.text_extents(text)

    pad_x, pad_y = 14, 6
    bw = width + pad_x * 2
    bh = height + pad_y * 2
    rounded_rect(ctx, x, y, bw, bh, r)
    stroke_and_fill(ctx, bg_hex, None)

    ctx.set_source_rgb(*hex_rgb(text_hex))
    ctx.move_to(x + pad_x, y + pad_y + height)
    ctx.show_text(text)
    ctx.restore()
    return bw, bh

def draw_progress_bar(ctx, x, y, w, h, progress=0.5, bg_hex="#1E293B", fill_hex="#10B981", r=6):
    """Vẽ thanh tiến trình nằm ngang chuẩn xác theo tỉ lệ [0.0 - 1.0]."""
    p = max(0.0, min(1.0, progress))
    # Nền
    rounded_rect(ctx, x, y, w, h, r)
    stroke_and_fill(ctx, bg_hex, None)
    # Phần trăm hoàn thành
    if p > 0.01:
        rounded_rect(ctx, x, y, max(r * 2, w * p), h, r)
        stroke_and_fill(ctx, fill_hex, None)

def draw_gauge_arc(ctx, cx, cy, r=60, pct=0.75, lw=10, col_hex="#38BDF8", bg_col_hex="#1E293B", label=""):
    """Vẽ đồng hồ đo góc cung tròn (Gauge Arc)."""
    ctx.save()
    p = max(0.0, min(1.0, pct))
    start_ang = math.pi * 0.75
    total_ang = math.pi * 1.5

    # Cung nền xám
    ctx.arc(cx, cy, r, start_ang, start_ang + total_ang)
    ctx.set_source_rgb(*hex_rgb(bg_col_hex))
    ctx.set_line_width(lw)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.stroke()

    # Cung tiến trình phát sáng
    if p > 0.01:
        ctx.arc(cx, cy, r, start_ang, start_ang + total_ang * p)
        ctx.set_source_rgb(*hex_rgb(col_hex))
        ctx.set_line_width(lw)
        ctx.stroke()

    # Nhãn ở giữa
    ctx.select_font_face("Segoe UI", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(18)
    ctx.set_source_rgb(*hex_rgb(col_hex))
    pct_text = f"{int(p * 100)}%"
    _, _, tw, th, _, _ = ctx.text_extents(pct_text)
    ctx.move_to(cx - tw / 2, cy + th / 2)
    ctx.show_text(pct_text)

    if label:
        ctx.set_font_size(12)
        ctx.set_source_rgb(*hex_rgb("#94A3B8"))
        _, _, lw2, lh2, _, _ = ctx.text_extents(label)
        ctx.move_to(cx - lw2 / 2, cy + r + 24)
        ctx.show_text(label)

    ctx.restore()

def draw_crosshair_reticle(ctx, cx, cy, r=28, col_hex="#4CC9F0", lw=2.0, t=0.0):
    """Vẽ kính ngắm kỹ thuật HUD với hiệu ứng xoay góc nhẹ."""
    ctx.save()
    ctx.translate(cx, cy)
    ctx.rotate(t * 0.5)

    ctx.set_source_rgb(*hex_rgb(col_hex))
    ctx.set_line_width(lw)
    # Vòng tròn ngắm đứt quãng
    for i in range(4):
        ang_st = i * math.pi / 2 + 0.18
        ang_et = (i + 1) * math.pi / 2 - 0.18
        ctx.arc(0, 0, r, ang_st, ang_et)
        ctx.stroke()

    # Tâm ngắm chữ thập
    ctx.move_to(-r * 0.5, 0); ctx.line_to(r * 0.5, 0); ctx.stroke()
    ctx.move_to(0, -r * 0.5); ctx.line_to(0, r * 0.5); ctx.stroke()
    ctx.arc(0, 0, 3, 0, 2 * math.pi); ctx.fill()
    ctx.restore()


# ==============================================================================
# 4. CẤU TRÚC ĐỒ HỌA THAM SỐ HÓA (PARAMETRIC PROPS & STRUCTURES)
# ==============================================================================
def draw_submersible_or_vessel(ctx, x, y, scale=1.0, pitch_deg=0.0, vessel_type="submarine", hull_num="192"):
    """
    Vẽ phương tiện hải dương tham số hóa (tàu ngầm, tàu khảo sát biển).
    Tái sử dụng cho mọi chủ đề hàng hải, khoa học đại dương hoặc lịch sử.
    """
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(math.radians(pitch_deg))
    ctx.scale(scale, scale)

    # 1. Thân tàu chính
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

    # Đường ghép vỏ kim loại
    ctx.set_source_rgba(0.05, 0.08, 0.10, 0.45)
    ctx.set_line_width(1.5)
    for px in range(-480, 420, 65):
        ctx.move_to(px, -42); ctx.line_to(px, 45); ctx.stroke()

    # Lỗ thoát nước
    ctx.set_source_rgb(*hex_rgb("#101518"))
    for lx in range(-460, 360, 32):
        rounded_rect(ctx, lx, 18, 18, 7, 3); ctx.fill()

    # 2. Tháp chỉ huy
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

    # Số hiệu tàu
    if hull_num:
        ctx.save()
        ctx.set_source_rgba(0.92, 0.95, 0.98, 0.9)
        ctx.select_font_face("Segoe UI", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(26)
        ctx.move_to(-35, -82)
        ctx.show_text(str(hull_num))
        ctx.restore()

    # Chân vịt & bánh lái
    ctx.set_source_rgb(*hex_rgb("#C68A4C"))
    for blade_y in [-12, 12]:
        ctx.arc(-587, blade_y + 5, 11, 0, 2 * math.pi); ctx.fill()

    ctx.restore()

def draw_bulkhead_or_vault_door(ctx, t, water_pct=0.0, door_open_pct=0.3, emergency_red=False):
    """
    Vẽ cánh cửa thép ngăn áp lực / cửa kho tiền / cửa hầm an toàn công nghiệp.
    Tái sử dụng cho mọi bối cảnh thám hiểm, sự cố hoặc công trình kỹ thuật.
    """
    # 1. Bức tường thép chịu lực bên ngoài
    ctx.set_source_rgb(*hex_rgb("#141C21"))
    ctx.rectangle(0, 0, W, H); ctx.fill()

    # Hàng đinh tán công nghiệp
    ctx.set_source_rgb(*hex_rgb("#0D1317"))
    ctx.set_line_width(3.0)
    for rx in (320, 1600):
        ctx.move_to(rx, 0); ctx.line_to(rx, H); ctx.stroke()
        for ry in range(40, H, 60):
            ctx.arc(rx, ry, 5, 0, 2 * math.pi); ctx.fill()

    # 2. Cửa vòm oval
    dw, dh = 720, 880
    dx, dy = (W - dw) / 2 + 60, (H - dh) / 2

    # Lỗ mở cửa
    ctx.save()
    rounded_rect(ctx, dx, dy, dw, dh, 220)
    ctx.clip()

    # Khoang bên trong
    ctx.set_source_rgb(*hex_rgb("#050B0E"))
    ctx.rectangle(dx, dy, dw, dh); ctx.fill()

    # Nếu có chất lỏng dâng lên
    if water_pct > 0.01:
        water_h = dh * min(1.0, water_pct)
        wy = dy + dh - water_h
        water_pat = cairo.LinearGradient(W/2, wy, W/2, dy + dh)
        water_pat.add_color_stop_rgba(0.0, 0.12, 0.35, 0.48, 0.95)
        water_pat.add_color_stop_rgba(1.0, 0.02, 0.08, 0.14, 1.0)
        ctx.rectangle(dx, wy, dw, water_h)
        ctx.set_source(water_pat); ctx.fill()
    ctx.restore()

    # Khung cửa đúc dày
    rounded_rect(ctx, dx, dy, dw, dh, 220)
    stroke_and_fill(ctx, None, "#32404A", lw=36.0)
    rounded_rect(ctx, dx, dy, dw, dh, 220)
    stroke_and_fill(ctx, None, "#182126", lw=12.0)

    # 8 chốt khóa xoay quanh khung
    for d_i in range(8):
        ang = d_i * (math.pi / 4.0) + math.pi / 8.0
        cx = (dx + dw / 2) + (dw / 2) * math.cos(ang)
        cy = (dy + dh / 2) + (dh / 2) * math.sin(ang)
        ctx.save()
        ctx.translate(cx, cy)
        ctx.rotate(ang)
        rounded_rect(ctx, -15, -30, 30, 60, 8)
        stroke_and_fill(ctx, "#B8860B", "#4A3708", lw=2.0)
        ctx.restore()

    # Tay quay khóa cửa tròn lớn
    door_swing_x = dx - 140
    ctx.save()
    ctx.translate(door_swing_x - 20, H / 2 + 40)
    ctx.set_source_rgb(*hex_rgb("#4E5E68"))
    ctx.arc(0, 0, 125, 0, 2 * math.pi); ctx.set_line_width(20.0); ctx.stroke()
    ctx.move_to(-125, 0); ctx.line_to(125, 0); ctx.stroke()
    ctx.move_to(0, -125); ctx.line_to(0, 125); ctx.stroke()
    ctx.arc(0, 0, 30, 0, 2 * math.pi); ctx.fill()
    ctx.restore()

    # Cảnh báo khẩn cấp đỏ nếu có
    if emergency_red:
        pat = cairo.RadialGradient(W / 2, 120, 50, W / 2, 120, 850)
        pat.add_color_stop_rgba(0.0, 1.0, 0.15, 0.1, 0.35)
        pat.add_color_stop_rgba(1.0, 0.0, 0.0, 0.0, 0.0)
        ctx.rectangle(0, 0, W, H); ctx.set_source(pat); ctx.fill()


# ==============================================================================
# 5. HÀM TƯƠNG THÍCH NGƯỢC (BACKWARD COMPATIBILITY ALIASES)
# ==============================================================================
def draw_squalus_detailed(ctx, x, y, scale=1.0, pitch_deg=0.0):
    """Wrapper tương thích ngược cho các tập lệnh cũ gọi USS Squalus."""
    draw_submersible_or_vessel(ctx, x, y, scale=scale, pitch_deg=pitch_deg, vessel_type="submarine", hull_num="192")

def draw_watertight_door_detailed(ctx, t, water_pct=0.3):
    """Wrapper tương thích ngược cho các tập lệnh cũ gọi cửa ngăn nước."""
    draw_bulkhead_or_vault_door(ctx, t, water_pct=water_pct, emergency_red=True)

def draw_officer_naquin(ctx, x, y, scale=1.0, expression="determined", t=0.0):
    """Wrapper tương thích ngược cho nhân vật chỉ huy."""
    from art_assets import draw_character_portrait
    draw_character_portrait(ctx, x, y, scale=scale, outfit="uniform", expression=expression, t=t)
