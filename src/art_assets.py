# -*- coding: utf-8 -*-
"""
art_assets.py
Thư viện Đồ Họa Vector 2D Nghệ Thuật Đa Dụng (General-Purpose Artistic Vector Asset Engine).
Cung cấp các chân dung nhân vật phong cách đổ bóng Chiaroscuro cao cấp, các bối cảnh
phòng làm việc / trung tâm điều khiển / phân xưởng công nghiệp đa năng, và các trạm thiết bị phần cứng.
"""

import math
import numpy as np
import cairo

W, H = 1920, 1080

def hex_rgb(h):
    if not isinstance(h, str):
        return (1.0, 1.0, 1.0)
    h = h.lstrip("#")
    if len(h) == 6:
        return tuple(int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))
    elif len(h) == 8:
        return tuple(int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))
    return (1.0, 1.0, 1.0)

def rounded_rect(ctx, x, y, w, h, r):
    r = min(r, abs(w) / 2.0, abs(h) / 2.0)
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    ctx.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
    ctx.close_path()


# ==============================================================================
# 1. CHÂN DUNG NHÂN VẬT ĐA DỤNG (CHIAROSCURO CHARACTER PORTRAIT ENGINE)
# ==============================================================================
def draw_character_portrait(
    ctx, x, y, scale=1.0,
    gender="male",
    outfit="casual",
    expression="determined",
    headwear=None,
    rim_color=None,
    t=0.0
):
    """
    Vẽ chân dung nhân vật bán thân (Bust Portrait) chất lượng điện ảnh với ánh sáng Chiaroscuro.
    - outfit: 'suit' (vest doanh nhân), 'casual' (đời thường), 'uniform' (đồng phục sĩ quan), 'workwear' (kỹ sư/thợ máy)
    - expression: 'neutral', 'determined', 'thoughtful', 'shocked', 'smiling'
    - headwear: None, 'officer_cap', 'casual_cap'
    """
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(scale, scale)

    # 1. Ánh sáng ven Chiaroscuro (Rim Light) phía sau lưng
    if rim_color is None:
        if expression == "shocked":
            rim_color = (0.85, 0.20, 0.15, 0.35)
        elif outfit == "uniform":
            rim_color = (0.35, 0.65, 0.88, 0.25)
        else:
            rim_color = (0.95, 0.75, 0.25, 0.25)

    pat_rim = cairo.RadialGradient(0, 150, 80, 0, 150, 380)
    r_r, r_g, r_b = rim_color[:3]
    r_a = rim_color[3] if len(rim_color) > 3 else 0.3
    pat_rim.add_color_stop_rgba(0.0, r_r, r_g, r_b, r_a)
    pat_rim.add_color_stop_rgba(1.0, r_r, r_g, r_b, 0.0)
    ctx.arc(0, 150, 380, 0, 2 * math.pi)
    ctx.set_source(pat_rim)
    ctx.fill()

    # 2. Thân & Trang phục (Torso & Outfit)
    ctx.new_path()
    ctx.move_to(-125, 480)
    ctx.curve_to(-115, 320, -95, 160, -90, 135)
    ctx.curve_to(-80, 75, -45, 68, 0, 72)
    ctx.curve_to(45, 68, 80, 75, 90, 135)
    ctx.curve_to(95, 160, 115, 320, 125, 480)
    ctx.close_path()

    if outfit == "suit":
        top_col, bot_col = "#1E293B", "#0F172A"
    elif outfit == "casual":
        top_col, bot_col = "#334155", "#1E293B"
    elif outfit == "workwear":
        top_col, bot_col = "#2B4C5E", "#162D3B"
    else:  # uniform
        top_col, bot_col = "#1C2730", "#0A0F13"

    coat_grad = cairo.LinearGradient(0, 65, 0, 480)
    coat_grad.add_color_stop_rgb(0.0, *hex_rgb(top_col))
    coat_grad.add_color_stop_rgb(1.0, *hex_rgb(bot_col))
    ctx.set_source(coat_grad)
    ctx.fill_preserve()
    ctx.set_source_rgb(*hex_rgb("#060A0D"))
    ctx.set_line_width(2.8)
    ctx.stroke()

    # Cổ áo & ve áo (Lapels)
    if outfit in ("suit", "uniform"):
        # Ve áo vest
        ctx.new_path()
        ctx.move_to(-45, 78); ctx.line_to(-65, 180); ctx.line_to(-18, 260); ctx.line_to(0, 140); ctx.close_path()
        ctx.set_source_rgb(*hex_rgb("#162028")); ctx.fill()
        ctx.new_path()
        ctx.move_to(45, 78); ctx.line_to(65, 180); ctx.line_to(18, 260); ctx.line_to(0, 140); ctx.close_path()
        ctx.set_source_rgb(*hex_rgb("#121A21")); ctx.fill()

        # Áo sơ mi trắng & cà vạt
        ctx.new_path()
        ctx.move_to(-28, 92); ctx.line_to(0, 145); ctx.line_to(28, 92); ctx.close_path()
        ctx.set_source_rgb(*hex_rgb("#E8ECF0")); ctx.fill()

        ctx.set_source_rgb(*hex_rgb("#090D10"))
        ctx.rectangle(-8, 122, 16, 20); ctx.fill()
        ctx.new_path()
        ctx.move_to(-10, 142); ctx.line_to(10, 142); ctx.line_to(14, 250); ctx.line_to(-14, 250); ctx.close_path()
        ctx.fill()

        if outfit == "uniform":
            # Hàng khuy vàng đồng phục
            for by in (175, 235, 295):
                for bx in (-38, 38):
                    ctx.set_source_rgb(*hex_rgb("#D4AF37"))
                    ctx.arc(bx, by, 7.5, 0, 2 * math.pi); ctx.fill()
    elif outfit == "casual":
        # Áo thun / len cổ tròn hoặc chữ V đời thường
        ctx.new_path()
        ctx.move_to(-32, 85); ctx.curve_to(-15, 130, 15, 130, 32, 85); ctx.close_path()
        ctx.set_source_rgb(*hex_rgb("#E2E8F0")); ctx.fill()

    # 3. Cổ & Khuôn mặt
    ctx.new_path()
    ctx.move_to(-25, 48); ctx.line_to(-22, 110); ctx.line_to(22, 110); ctx.line_to(25, 48); ctx.close_path()
    neck_grad = cairo.LinearGradient(-25, 0, 25, 0)
    neck_grad.add_color_stop_rgb(0.0, *hex_rgb("#B88463"))
    neck_grad.add_color_stop_rgb(0.5, *hex_rgb("#D6A784"))
    neck_grad.add_color_stop_rgb(1.0, *hex_rgb("#A87455"))
    ctx.set_source(neck_grad); ctx.fill()

    # Đường viền xương hàm & gò má
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
    ctx.set_source(face_grad)
    ctx.fill_preserve()
    ctx.set_source_rgb(*hex_rgb("#966343"))
    ctx.set_line_width(1.8)
    ctx.stroke()

    # Mũi
    ctx.new_path()
    ctx.move_to(-2, -14); ctx.line_to(5, 8); ctx.line_to(-6, 14); ctx.close_path()
    ctx.set_source_rgb(*hex_rgb("#D69F7A")); ctx.fill_preserve()
    ctx.set_source_rgb(*hex_rgb("#A86E47")); ctx.set_line_width(1.8); ctx.stroke()

    # 4. Mắt & Biểu cảm (Eyes & Expression)
    if expression in ("shocked", "horror"):
        # Mắt trợn trừng kinh ngạc
        ctx.set_source_rgb(*hex_rgb("#241A12")); ctx.set_line_width(3.8)
        ctx.move_to(-30, -22); ctx.line_to(-6, -14); ctx.stroke()
        ctx.move_to(30, -22); ctx.line_to(6, -14); ctx.stroke()

        ctx.set_source_rgb(1, 1, 1)
        rounded_rect(ctx, -25, -12, 18, 14, 5); ctx.fill()
        rounded_rect(ctx, 7, -12, 18, 14, 5); ctx.fill()
        ctx.set_source_rgb(*hex_rgb("#1B2A36"))
        ctx.arc(-16, -5, 5, 0, 2 * math.pi); ctx.fill()
        ctx.arc(16, -5, 5, 0, 2 * math.pi); ctx.fill()

        # Miệng mở to thở dốc / hô lệnh
        ctx.set_source_rgb(*hex_rgb("#301010"))
        rounded_rect(ctx, -16, 20, 32, 22, 8); ctx.fill()
    elif expression == "smiling":
        # Mắt cười dịu dàng
        ctx.set_source_rgb(*hex_rgb("#241A12")); ctx.set_line_width(2.8)
        ctx.arc(-16, -8, 8, math.pi * 0.15, math.pi * 0.85); ctx.stroke()
        ctx.arc(16, -8, 8, math.pi * 0.15, math.pi * 0.85); ctx.stroke()
        # Nụ cười
        ctx.arc(0, 18, 14, math.pi * 0.1, math.pi * 0.9); ctx.stroke()
    else:  # determined / neutral
        ctx.set_source_rgb(*hex_rgb("#241A12")); ctx.set_line_width(3.2)
        ctx.move_to(-28, -16); ctx.line_to(-8, -13); ctx.stroke()
        ctx.move_to(8, -13); ctx.line_to(28, -16); ctx.stroke()

        ctx.set_source_rgb(1, 1, 1)
        rounded_rect(ctx, -24, -8, 16, 10, 3); ctx.fill()
        rounded_rect(ctx, 8, -8, 16, 10, 3); ctx.fill()
        ctx.set_source_rgb(*hex_rgb("#1B2A36"))
        ctx.arc(-16, -3, 4, 0, 2 * math.pi); ctx.fill()
        ctx.arc(16, -3, 4, 0, 2 * math.pi); ctx.fill()

        # Miệng kiên định
        ctx.set_source_rgb(*hex_rgb("#7A452B")); ctx.set_line_width(2.8)
        ctx.move_to(-14, 25); ctx.line_to(14, 25); ctx.stroke()

    # 5. Mũ hoặc Tóc (Headwear or Hair)
    if headwear == "officer_cap":
        # Mũ sĩ quan hải quân
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

        # Vành mũ da đen bóng
        ctx.new_path()
        ctx.move_to(-68, -32)
        ctx.curve_to(-25, -16, 25, -16, 68, -32)
        ctx.curve_to(50, -40, -50, -40, -68, -32)
        ctx.close_path()
        ctx.set_source_rgb(*hex_rgb("#0A0D10")); ctx.fill()
    else:
        # Mái tóc ngắn hiện đại vuốt tự nhiên
        ctx.new_path()
        ctx.move_to(-44, -40)
        ctx.curve_to(-48, -85, 42, -90, 44, -45)
        ctx.curve_to(30, -60, -20, -60, -44, -40)
        ctx.close_path()
        ctx.set_source_rgb(*hex_rgb("#1F2429"))
        ctx.fill()

    ctx.restore()


# ==============================================================================
# 2. KHÔNG GIAN BỐI CẢNH NỘI THẤT ĐA DỤNG (INTERIOR ROOM & FACILITY ARTIST)
# ==============================================================================
def draw_room_interior(ctx, t, theme="control_room", emergency=False):
    """
    Vẽ không gian nội thất phòng kỹ thuật / điều hành / phòng làm việc đa năng.
    - theme: 'control_room', 'modern_office', 'industrial_bay', 'vintage_study'
    - emergency: chế độ cảnh báo khẩn cấp (đèn đỏ strobe và bóng đổ kịch tính)
    """
    bg = cairo.LinearGradient(0, 0, W, H)
    if emergency:
        bg.add_color_stop_rgb(0.0, *hex_rgb("#230A0A"))
        bg.add_color_stop_rgb(0.5, *hex_rgb("#180707"))
        bg.add_color_stop_rgb(1.0, *hex_rgb("#0D0303"))
    elif theme == "modern_office":
        bg.add_color_stop_rgb(0.0, *hex_rgb("#0F172A"))
        bg.add_color_stop_rgb(0.5, *hex_rgb("#1E293B"))
        bg.add_color_stop_rgb(1.0, *hex_rgb("#090D16"))
    else:
        bg.add_color_stop_rgb(0.0, *hex_rgb("#18232B"))
        bg.add_color_stop_rgb(0.4, *hex_rgb("#111A20"))
        bg.add_color_stop_rgb(1.0, *hex_rgb("#090D10"))

    ctx.rectangle(0, 0, W, H)
    ctx.set_source(bg)
    ctx.fill()

    # Khung sườn dầm thép chịu lực
    rib_col = "#2A0D0D" if emergency else ("#1E293B" if theme == "modern_office" else "#22313B")
    ctx.set_source_rgb(*hex_rgb(rib_col))
    ctx.set_line_width(14.0)
    for rx in range(160, W + 100, 320):
        ctx.move_to(rx, 0); ctx.line_to(rx, H); ctx.stroke()
        for ry in range(40, H, 55):
            ctx.arc(rx, ry, 4.0, 0, 2 * math.pi); ctx.fill()

    # Các đường ống dẫn / máng cáp kỹ thuật trên trần
    conduits = [
        (110, 32, "#B87333", "#7A4315"),
        (165, 24, "#CD7F32", "#8A541E"),
        (215, 18, "#7E96A0", "#4B5F68"),
    ]
    for py, pw, c_light, c_dark in conduits:
        p_grad = cairo.LinearGradient(0, py - pw/2, 0, py + pw/2)
        p_grad.add_color_stop_rgb(0.0, *hex_rgb(c_light))
        p_grad.add_color_stop_rgb(1.0, *hex_rgb(c_dark))
        ctx.set_source(p_grad); ctx.set_line_width(pw)
        ctx.move_to(0, py); ctx.line_to(W, py); ctx.stroke()

    # Đèn tường công nghiệp chiếu rọi
    for lx in (360, 1100, 1660):
        ctx.arc(lx, 140, 24, 0, math.pi)
        ctx.set_source_rgb(*hex_rgb("#CD7F32")); ctx.fill()

        pat = cairo.RadialGradient(lx, 145, 15, lx, 145, 450)
        if emergency:
            pat.add_color_stop_rgba(0.0, 1.0, 0.2, 0.1, 0.55)
            pat.add_color_stop_rgba(1.0, 0.2, 0.0, 0.0, 0.0)
        else:
            pat.add_color_stop_rgba(0.0, 1.0, 0.90, 0.58, 0.40)
            pat.add_color_stop_rgba(1.0, 0.15, 0.12, 0.04, 0.0)
        ctx.rectangle(0, 0, W, H); ctx.set_source(pat); ctx.fill()


# ==============================================================================
# 3. TRẠM THIẾT BỊ PHẦN CỨNG & ĐIỀU KHIỂN (INTERACTIVE HARDWARE & TERMINALS)
# ==============================================================================
def draw_terminal_station(ctx, x, y, title="COMMAND & TELEMETRY", device_type="vintage_telecom", vibe=0.0):
    """
    Vẽ trạm thiết bị phần cứng gắn tường / bàn điều khiển đa năng.
    - device_type: 'vintage_telecom' (chuông đồng, quay số, tay quay), 'gauge_cluster' (cụm đồng hồ áp suất)
    """
    ctx.save()
    ctx.translate(x + vibe, y)

    # Thân hộp gang đúc
    rounded_rect(ctx, -150, -230, 300, 460, 22)
    box_grad = cairo.LinearGradient(-150, 0, 150, 0)
    box_grad.add_color_stop_rgb(0.0, *hex_rgb("#1C252B"))
    box_grad.add_color_stop_rgb(0.5, *hex_rgb("#2E3D46"))
    box_grad.add_color_stop_rgb(1.0, *hex_rgb("#141B20"))
    ctx.set_source(box_grad); ctx.fill_preserve()
    ctx.set_source_rgb(*hex_rgb("#0C1215")); ctx.set_line_width(6.0); ctx.stroke()

    # Ốc vít bắt tường 4 góc
    for mx, my in [(-130, -210), (130, -210), (-130, 210), (130, 210)]:
        ctx.set_source_rgb(*hex_rgb("#4C5C66"))
        ctx.arc(mx, my, 8, 0, 2 * math.pi); ctx.fill()

    if device_type == "vintage_telecom":
        # Chuông đồng kép phía trên
        for bell_x in [-75, 75]:
            b_grad = cairo.LinearGradient(bell_x - 45, -280, bell_x + 45, -235)
            b_grad.add_color_stop_rgb(0.0, *hex_rgb("#E5A65D"))
            b_grad.add_color_stop_rgb(1.0, *hex_rgb("#7A4515"))
            ctx.set_source(b_grad); ctx.arc(bell_x, -245, 48, math.pi, 2 * math.pi); ctx.fill()

        # Con lắc gõ chuông
        striker_x = math.sin(vibe * 12) * 14
        ctx.set_source_rgb(*hex_rgb("#B8860B"))
        ctx.arc(striker_x, -260, 9, 0, 2 * math.pi); ctx.fill()

    # Bảng đồng khắc hướng dẫn
    ctx.set_source_rgb(*hex_rgb("#B8860B"))
    rounded_rect(ctx, -110, -140, 220, 80, 8); ctx.fill_preserve()
    ctx.set_source_rgb(*hex_rgb("#664903")); ctx.set_line_width(3.0); ctx.stroke()

    ctx.select_font_face("Segoe UI", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(15); ctx.set_source_rgb(0.1, 0.1, 0.1)
    ctx.move_to(-85, -100); ctx.show_text(title[:24])

    # Núm xoay / công tắc chọn kênh
    ctx.set_source_rgb(*hex_rgb("#CD7F32"))
    ctx.arc(0, 45, 60, 0, 2 * math.pi); ctx.fill()
    ctx.set_source_rgb(*hex_rgb("#182228"))
    ctx.arc(0, 45, 48, 0, 2 * math.pi); ctx.fill()
    ctx.set_source_rgb(*hex_rgb("#B8860B"))
    ctx.rectangle(-8, 5, 16, 50); ctx.fill()

    ctx.restore()


# ==============================================================================
# 4. PHÂN XƯỞNG MÁY MÓC CÔNG NGHIỆP NẶNG (HEAVY MACHINERY BAY)
# ==============================================================================
def draw_machinery_bay(ctx, t, shake_intensity=0.0, fluid_pct=0.0, fluid_color="#184E60"):
    """
    Vẽ phân xưởng động cơ / máy móc công nghiệp nặng, hỗ trợ hiệu ứng rung lắc và ngập chất lỏng.
    """
    shake_x = math.sin(t * 85) * shake_intensity
    shake_y = math.cos(t * 105) * shake_intensity

    ctx.save()
    ctx.translate(shake_x, shake_y)

    ctx.set_source_rgb(*hex_rgb("#061016")); ctx.rectangle(0, 0, W, H); ctx.fill()

    # Hai khối động cơ / tua-bin khổng lồ 2 bên
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

        # Nắp xi-lanh động cơ
        for cy in range(-280, 240, 95):
            rounded_rect(ctx, -160, cy, 320, 68, 14)
            ctx.set_source_rgb(*hex_rgb("#425563")); ctx.fill_preserve()
            ctx.set_source_rgb(*hex_rgb("#0D1317")); ctx.set_line_width(2.5); ctx.stroke()
        ctx.restore()

    # Chất lỏng dâng lên từ sàn nếu có
    if fluid_pct > 0.01:
        fh = H * min(1.0, fluid_pct)
        fy = H - fh
        ctx.rectangle(0, fy, W, fh)
        ctx.set_source_rgba(*hex_rgb(fluid_color), 0.85)
        ctx.fill()

    ctx.restore()


# ==============================================================================
# 5. HÀM TƯƠNG THÍCH NGƯỢC (BACKWARD COMPATIBILITY ALIASES)
# ==============================================================================
def draw_naquin_cinematic(ctx, x, y, scale=1.0, expression="determined", t=0.0):
    """Wrapper tương thích ngược cho chân dung Đại úy Oliver Naquin."""
    draw_character_portrait(ctx, x, y, scale=scale, outfit="uniform", expression=expression, headwear="officer_cap", t=t)

def draw_control_room_background(ctx, t, emergency_red=False):
    """Wrapper tương thích ngược cho phòng điều khiển."""
    draw_room_interior(ctx, t, theme="control_room", emergency=emergency_red)

def draw_telephone_station(ctx, x, y, vibe=0.0):
    """Wrapper tương thích ngược cho trạm điện thoại xuyên vách ngăn."""
    draw_terminal_station(ctx, x, y, title="U.S. NAVY SOUND-POWERED", device_type="vintage_telecom", vibe=vibe)

def draw_engine_room_flood(ctx, t):
    """Wrapper tương thích ngược cho khoang động cơ ngập nước."""
    st = max(0.0, t - 57.5)
    draw_machinery_bay(ctx, t, shake_intensity=15.0 if st > 0 else 0.0, fluid_pct=min(0.85, st * 0.05))

