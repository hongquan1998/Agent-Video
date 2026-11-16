"""
assets_library.py
Thư viện Vector 2D Tối Giản & Chuyển Động Procedural (PyCairo)
Dành cho pipeline: AI phân tích cốt truyện (JSON) + Python dựng chuyển động 30/60 FPS.
Tích hợp trực tiếp vào quy trình tự động hóa auto_produce.py.
"""

import os
import sys
import math
import json
import shutil
import subprocess
import cairo
import numpy as np

# Ensure local imports work cleanly
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

try:
    from localization import get_font_for_lang, T
except ImportError:
    def get_font_for_lang(lang="vi"):
        return "Segoe UI" if str(lang).lower() in ("vi", "en") else "Sans"
    def T(key, lang="vi"):
        return key

# ==============================================================================
# 1. VISUAL DESIGN TOKENS & PRIMITIVE HELPERS
# ==============================================================================
W_DEFAULT, H_DEFAULT, FPS_DEFAULT = 1920, 1080, 30
DEBUG_PIVOTS = False  # Đặt True để hiển thị chấm tròn vàng tại mọi khớp xoay

PALETTE = {
    # Nền & Blueprint HUD
    "bg_navy": "#081B29",
    "grid_line": "#133147",
    "hud_amber": "#F5C242",
    "hud_cyan": "#4CC9F0",
    "hud_white": "#F4F7F9",
    "alert_coral": "#E05A47",
    "ink_crimson": "#C93B2B",
    "journal_cream": "#F2EAD3",
    "accent_gold": "#E8A838",
    "office_slate": "#1E293B",
    "desk_amber": "#FFB703",
    "soft_teal": "#00A896",
    # Nhân vật, Sinh vật & Đạo cụ
    "outline": "#12171C",
    "slate_dark": "#3A4750",
    "slate_mid": "#4D5D66",
    "slate_light": "#8FA1AB",
    "silver_belly": "#BCCAD1",
    "teal_deep": "#184E60",
    "teal_suit": "#2E7D91",
    "teal_light": "#63A3B5",
    "skin_warm": "#E2B897",
    "wood_brown": "#7A5236",
    "fur_brown": "#6B4F3B",
    "fur_dark": "#3D2B1F",
    "denim_blue": "#284B63",
    "casual_cream": "#E9ECEF",
    "hair_dark": "#1F1D1D",
}


def hex_rgb(hex_str):
    """Chuyển mã màu Hex sang tuple (R, G, B) chuẩn hóa [0.0 - 1.0]."""
    h = hex_str.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


def shade_color(hex_str, factor=0.85):
    """Làm tối hoặc sáng nhẹ màu hex/rgb để tạo phân lớp chiều sâu thị giác (z-depth)."""
    if isinstance(hex_str, (tuple, list)):
        r, g, b = hex_str[:3]
    else:
        r, g, b = hex_rgb(hex_str)
    return (max(0.0, min(1.0, r * factor)),
            max(0.0, min(1.0, g * factor)),
            max(0.0, min(1.0, b * factor)))


def safe_scale(ctx, sx, sy):
    """Kẹp giá trị scale >= 0.05 nhưng giữ nguyên dấu âm/dương (hỗ trợ flip_x/flip_y)."""
    safe_x = math.copysign(max(0.05, abs(sx)), sx)
    safe_y = math.copysign(max(0.05, abs(sy)), sy)
    ctx.scale(safe_x, safe_y)


def stroke_and_fill(ctx, fill_hex=None, stroke_hex="#12171C", lw=1.8, alpha=1.0):
    """Tô màu mảng phẳng (flat fill) và vẽ viền bo tròn chuẩn vector 2D."""
    if fill_hex is not None:
        if isinstance(fill_hex, str):
            r, g, b = hex_rgb(fill_hex)
        else:
            r, g, b = fill_hex[:3]
        ctx.set_source_rgba(r, g, b, alpha)
        if stroke_hex is not None and lw > 0:
            ctx.fill_preserve()
        else:
            ctx.fill()
    if stroke_hex is not None and lw > 0:
        if isinstance(stroke_hex, str):
            sr, sg, sb = hex_rgb(stroke_hex)
        else:
            sr, sg, sb = stroke_hex[:3]
        ctx.set_source_rgba(sr, sg, sb, alpha)
        ctx.set_line_width(lw)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.stroke()


def rounded_rect(ctx, x, y, w, h, r):
    """Tạo đường dẫn hình chữ nhật bo góc."""
    r = min(r, abs(w) / 2.0, abs(h) / 2.0)
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    ctx.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
    ctx.close_path()


def draw_pivot_marker(ctx, radius=3.2):
    """Vẽ tâm xoay màu vàng hổ phách tại gốc (0, 0) khi bật DEBUG_PIVOTS."""
    if not DEBUG_PIVOTS:
        return
    ctx.save()
    ctx.arc(0, 0, radius, 0, 2 * math.pi)
    ctx.set_source_rgb(*hex_rgb(PALETTE["hud_amber"]))
    ctx.fill_preserve()
    ctx.set_source_rgb(*hex_rgb(PALETTE["outline"]))
    ctx.set_line_width(1.2)
    ctx.stroke()
    ctx.restore()


def draw_capsule_limb(ctx, length, r_top, r_bot=None, fill_hex="#4D5D66", accent_hex=None, is_child=False, is_terminal=False, lw=1.8):
    """
    Vẽ một đốt xương hình viên nang phẳng hoàn toàn không vết nối (Seamless Limb):
    - Nếu là đốt cha (is_child=False): Vẽ capsule chuẩn với outline tinh tế lw=1.8.
    - Nếu là đốt con (is_child=True): Fill capsule + patch tròn che khớp tại (0, 0) xóa sạch vết cắt
      bên trong của đốt cha, chỉ viền 2 bên sườn nối tiếp mượt mà.
    - accent_hex: Đã loại bỏ việc vẽ khớp tròn thô kệch, giữ tính tương thích tham số.
    """
    if r_bot is None:
        r_bot = r_top

    outline_col = PALETTE.get("outline", "#12171C")

    if is_child:
        # 1. Fill thân đốt con
        ctx.new_sub_path()
        ctx.arc(0, 0, r_top, math.pi, 0)
        ctx.arc(0, length, r_bot, 0, math.pi)
        ctx.close_path()
        stroke_and_fill(ctx, fill_hex, None)

        # 2. Xóa sạch vết viền khớp của đốt cha tại tâm xoay (0, 0)
        ctx.new_sub_path()
        ctx.arc(0, 0, r_top - lw * 0.35, 0, 2 * math.pi)
        stroke_and_fill(ctx, fill_hex, None)

        # 3. Viền 2 cạnh sườn mượt mà
        ctx.new_sub_path()
        ctx.move_to(-r_top, 0)
        ctx.line_to(-r_bot, length)
        ctx.move_to(r_top, 0)
        ctx.line_to(r_bot, length)
        if is_terminal:
            ctx.arc(0, length, r_bot, 0, math.pi)
        stroke_and_fill(ctx, None, outline_col, lw=lw)
    else:
        ctx.new_sub_path()
        ctx.arc(0, 0, r_top, math.pi, 0)
        ctx.arc(0, length, r_bot, 0, math.pi)
        ctx.close_path()
        stroke_and_fill(ctx, fill_hex, outline_col, lw=lw)

    draw_pivot_marker(ctx)


# ==============================================================================
# 2. HỆ THỐNG XƯƠNG PHÂN CẤP 2D (SCENE GRAPH & BONE HIERARCHY)
# ==============================================================================
class BoneNode:
    """Nút xương 2D hỗ trợ phân cấp cha-con và thứ tự lớp vẽ z_index."""
    def __init__(self, name, pivot_x=0.0, pivot_y=0.0, base_angle=0.0, draw_fn=None, z_index=0):
        self.name = name
        self.pivot_x = pivot_x
        self.pivot_y = pivot_y
        self.base_angle = base_angle
        self.anim_angle = 0.0
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.scale_x = 1.0
        self.scale_y = 1.0
        self.draw_fn = draw_fn
        self.z_index = z_index
        self.children = []

    def add_child(self, child_node):
        self.children.append(child_node)
        return child_node

    def reset_pose(self):
        self.anim_angle = 0.0
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.scale_x = 1.0
        self.scale_y = 1.0
        for c in self.children:
            c.reset_pose()

    def render(self, ctx):
        ctx.save()
        ctx.translate(self.pivot_x + self.offset_x, self.pivot_y + self.offset_y)
        ctx.rotate(math.radians(self.base_angle + self.anim_angle))
        safe_scale(ctx, self.scale_x, self.scale_y)

        # Vẽ các xương con nằm phía sau (z_index < 0)
        for child in sorted((c for c in self.children if c.z_index < 0), key=lambda x: x.z_index):
            child.render(ctx)

        # Vẽ hình học của chính xương hiện tại
        if self.draw_fn is not None:
            self.draw_fn(ctx)

        # Vẽ các xương con nằm phía trước (z_index >= 0)
        for child in sorted((c for c in self.children if c.z_index >= 0), key=lambda x: x.z_index):
            child.render(ctx)

        ctx.restore()


class ActorRig:
    """Đối tượng hoàn chỉnh chứa gốc xương (root) và từ điển truy cập nhanh mọi khớp."""
    def __init__(self, rig_type, root_bone, bones_dict):
        self.rig_type = rig_type
        self.root = root_bone
        self.bones = bones_dict
        self.x = 0.0
        self.y = 0.0
        self.scale = 1.0
        self.angle_deg = 0.0
        self.flip_x = False

    def set_transform(self, x, y, scale=1.0, angle_deg=0.0, flip_x=False):
        self.x = x
        self.y = y
        self.scale = scale
        self.angle_deg = angle_deg
        self.flip_x = flip_x

    def reset_pose(self):
        self.root.reset_pose()

    def render(self, ctx):
        ctx.save()
        ctx.translate(self.x, self.y)
        ctx.rotate(math.radians(self.angle_deg))
        sx = -self.scale if self.flip_x else self.scale
        safe_scale(ctx, sx, self.scale)
        self.root.render(ctx)
        ctx.restore()


# ==============================================================================
# 3. THƯ VIỆN VECTOR TĨNH & BỘ LẮP RÁP NHÂN VẬT / SINH VẬT / ĐẠO CỤ
# ==============================================================================
class RigBuilder:
    """Bộ sưu tập hàm tạo Rig tách khớp tái sử dụng cho AI và Python."""

    # --------------------------------------------------------------------------
    # 3.1. NHÂN VẬT CON NGƯỜI (DIVER / EXPLORER / SWIMMER / CIVILIAN / OFFICER / CASUAL / FORMAL)
    # --------------------------------------------------------------------------
    @staticmethod
    def build_human_rig(variant="casual"):
        bones = {}
        outline_col = PALETTE.get("outline", "#15191E")
        skin = PALETTE.get("skin_warm", "#FADBC8")
        skin_shadow = shade_color(skin, 0.88)
        hair_dark = PALETTE.get("hair_dark", "#1E1B18")
        hair_hl = shade_color(hair_dark, 1.45)

        if variant in ("casual", "civilian"):
            # Phong cách đời thường hiện đại: Áo len camel/sand ấm áp hoặc xám khói, quần denim indigo thanh lịch
            top_col = "#D4A373" if variant == "casual" else "#E2E8F0"
            collar_inner = "#FFFFFF" if variant == "casual" else "#1E293B"
            pants_col = "#1E3A8A" if variant == "casual" else "#1E293B"
            shoe_main = "#334155"
            shoe_sole = "#FFFFFF"
            has_jacket = False
        elif variant in ("formal", "suit"):
            # Vest công sở cao cấp
            top_col = "#1A2536"
            collar_inner = "#F8FAFC"
            pants_col = "#1A2536"
            shoe_main = "#0B0F17"
            shoe_sole = "#334155"
            has_jacket = True
        elif variant == "officer":
            top_col = PALETTE.get("slate_dark", "#1E293B")
            collar_inner = "#F8FAFC"
            pants_col = PALETTE.get("slate_dark", "#1E293B")
            shoe_main = outline_col
            shoe_sole = "#334155"
            has_jacket = True
        elif variant == "machinist":
            top_col = PALETTE.get("denim_blue", "#284B63")
            collar_inner = "#F8FAFC"
            pants_col = PALETTE.get("denim_blue", "#284B63")
            shoe_main = PALETTE.get("wood_brown", "#7A5236")
            shoe_sole = "#334155"
            has_jacket = False
        elif variant == "explorer":
            top_col = PALETTE.get("slate_mid", "#475569")
            collar_inner = "#334155"
            pants_col = PALETTE.get("slate_dark", "#334155")
            shoe_main = PALETTE.get("wood_brown", "#78350F")
            shoe_sole = "#FFFFFF"
            has_jacket = True
        elif variant == "diver":
            top_col = PALETTE.get("teal_suit", "#164E63")
            collar_inner = "#083344"
            pants_col = top_col
            shoe_main = PALETTE.get("hud_amber", "#F59E0B")
            shoe_sole = "#D97706"
            has_jacket = False
        else: # swimmer
            top_col = PALETTE.get("teal_deep", "#184E60")
            collar_inner = skin
            pants_col = top_col
            shoe_main = skin
            shoe_sole = skin
            has_jacket = False

        # 1. Thân người (Torso & Pelvis)
        def draw_torso(ctx):
            # A. Vùng mông & hông quần (Pelvis / Seat) nối liền tự nhiên từ eo xuống đùi
            ctx.new_sub_path()
            ctx.move_to(-14, -14)
            ctx.curve_to(-17, -2, -16, 6, -12, 8)
            ctx.curve_to(-6, 8, -2, 6, 0, 4)
            ctx.curve_to(6, 4, 10, -4, 11, -14)
            ctx.close_path()
            stroke_and_fill(ctx, pants_col, outline_col, lw=1.6)

            # B. Thân áo (Torso / Top) với gấu áo phủ nhẹ qua thắt lưng
            ctx.new_sub_path()
            ctx.move_to(-15, -60) # Vai sau
            ctx.curve_to(-18, -42, -16, -22, -14, -2) # Sống lưng áo
            ctx.curve_to(-7, 2, 7, 2, 14, -2)        # Gấu áo phủ nhẹ
            ctx.curve_to(16, -22, 17, -42, 15, -60)    # Ngực trước
            ctx.line_to(6, -65)   # Vai trước dốc lên cổ
            ctx.curve_to(2, -67, -2, -67, -6, -65)     # Cổ áo
            ctx.line_to(-15, -60) # Vai sau
            ctx.close_path()
            stroke_and_fill(ctx, top_col, outline_col, lw=1.6)

            if variant in ("formal", "suit"):
                # Sơ mi + cà vạt + ve áo vest
                ctx.new_sub_path()
                ctx.move_to(-6, -65)
                ctx.line_to(1, -50)
                ctx.line_to(7, -65)
                ctx.close_path()
                stroke_and_fill(ctx, collar_inner, outline_col, lw=1.2)
                # Cà vạt đỏ
                ctx.new_sub_path()
                ctx.move_to(0, -50)
                ctx.line_to(3, -50)
                ctx.line_to(4, -20)
                ctx.line_to(1.5, -14)
                ctx.line_to(-1, -20)
                ctx.close_path()
                stroke_and_fill(ctx, "#991B1B", outline_col, lw=1.2)
                # Ve áo vest
                ctx.new_sub_path()
                ctx.move_to(-14, -60)
                ctx.line_to(-4, -40)
                ctx.line_to(-9, -36)
                ctx.line_to(-4, -18)
                stroke_and_fill(ctx, None, outline_col, lw=1.3)
                ctx.new_sub_path()
                ctx.move_to(14, -60)
                ctx.line_to(4, -40)
                ctx.line_to(9, -36)
                ctx.line_to(4, -18)
                stroke_and_fill(ctx, None, outline_col, lw=1.3)
            elif variant == "officer":
                # Nút vàng hải quân sang trọng
                for by in (-45, -30, -15):
                    ctx.new_sub_path()
                    ctx.arc(0, by, 2.8, 0, 2 * math.pi)
                    stroke_and_fill(ctx, PALETTE["hud_amber"], outline_col, lw=1.2)
            else:
                # Cổ áo thun trắng lót trong
                ctx.new_sub_path()
                ctx.move_to(-5, -65)
                ctx.curve_to(-3, -56, 3, -56, 5, -65)
                ctx.close_path()
                stroke_and_fill(ctx, collar_inner, outline_col, lw=1.3)
                if has_jacket:
                    ctx.new_sub_path()
                    ctx.move_to(-2.5, -56)
                    ctx.line_to(-3, -3)
                    stroke_and_fill(ctx, None, outline_col, lw=1.1)
                    ctx.new_sub_path()
                    ctx.move_to(2.5, -56)
                    ctx.line_to(3, -3)
                    stroke_and_fill(ctx, None, outline_col, lw=1.1)
            draw_pivot_marker(ctx)

        # 2. Đầu & Mặt & Tóc (Head & Neck & Hair)
        def draw_head(ctx):
            # Cổ chuẩn giải phẫu (nối từ xương quai hàm cắm sâu vào lồng ngực)
            ctx.new_sub_path()
            ctx.move_to(-5.5, -4)
            ctx.curve_to(-6.0, 4, -7.0, 10, -7.5, 16)
            ctx.line_to(7.5, 16)
            ctx.curve_to(6.5, 10, 5.5, 4, 5.0, -4)
            ctx.close_path()
            stroke_and_fill(ctx, skin, outline_col, lw=1.5)

            # Bóng đổ cổ dưới cằm
            ctx.new_sub_path()
            ctx.move_to(-5.5, -4)
            ctx.curve_to(0, 2, 2, 2, 5.0, -4)
            ctx.close_path()
            stroke_and_fill(ctx, skin_shadow, None)

            if variant == "diver":
                ctx.new_sub_path()
                ctx.arc(0, -20, 18.0, 0, 2 * math.pi)
                stroke_and_fill(ctx, "#083344", outline_col, lw=1.8)
                ctx.new_sub_path()
                ctx.arc(8, -20, 11, 0, 2 * math.pi)
                stroke_and_fill(ctx, "#0E7490", outline_col, lw=1.8)
                ctx.new_sub_path()
                ctx.arc(8, -20, 7.5, 0, 2 * math.pi)
                stroke_and_fill(ctx, "#22D3EE", outline_col, lw=1.2)
                ctx.new_sub_path()
                ctx.arc(10.5, -23, 2.8, 0, 2 * math.pi)
                stroke_and_fill(ctx, "#FFFFFF", None)
                draw_pivot_marker(ctx)
                return

            # Khuôn mặt
            ctx.new_sub_path()
            ctx.arc(0, -20, 17.5, 0, 2 * math.pi)
            stroke_and_fill(ctx, skin, outline_col, lw=1.6)

            # Tai
            ctx.new_sub_path()
            ctx.arc(-7, -19, 3.6, 0, 2 * math.pi)
            stroke_and_fill(ctx, skin, outline_col, lw=1.3)
            ctx.new_sub_path()
            ctx.arc(-7, -19, 1.8, -math.pi/2, math.pi/2)
            stroke_and_fill(ctx, None, outline_col, lw=1.0)

            # Mũi
            ctx.new_sub_path()
            ctx.move_to(15, -21)
            ctx.curve_to(18.0, -19, 18.0, -17.5, 15.5, -16.5)
            stroke_and_fill(ctx, None, outline_col, lw=1.4)

            # Mắt có catchlight
            ctx.new_sub_path()
            ctx.arc(8.0, -21, 2.2, 0, 2 * math.pi)
            stroke_and_fill(ctx, outline_col, None)
            ctx.new_sub_path()
            ctx.arc(8.8, -22, 0.7, 0, 2 * math.pi)
            stroke_and_fill(ctx, "#FFFFFF", None)

            # Lông mày
            ctx.new_sub_path()
            ctx.move_to(4, -26)
            ctx.curve_to(7.5, -28, 12, -27, 14, -25)
            stroke_and_fill(ctx, None, outline_col, lw=1.6)

            # Miệng
            ctx.new_sub_path()
            ctx.move_to(9.5, -12)
            ctx.curve_to(11.5, -11.5, 13, -12.5, 13.5, -13)
            stroke_and_fill(ctx, None, outline_col, lw=1.3)

            # Má hồng
            ctx.new_sub_path()
            ctx.arc(4.5, -15, 2.5, 0, 2 * math.pi)
            stroke_and_fill(ctx, "#FCA5A5", None, alpha=0.35)

            if variant == "officer":
                # Mũ sĩ quan chuẩn quân phục
                rounded_rect(ctx, -18, -42, 38, 11, 3)
                stroke_and_fill(ctx, PALETTE["hud_white"], outline_col, lw=1.6)
                rounded_rect(ctx, 4, -34, 18, 5, 2)
                stroke_and_fill(ctx, outline_col, None)
            elif variant == "explorer":
                # Mũ vành dã ngoại
                ctx.new_sub_path()
                ctx.move_to(-22, -34)
                ctx.line_to(22, -34)
                ctx.curve_to(16, -48, -16, -48, -22, -34)
                ctx.close_path()
                stroke_and_fill(ctx, PALETTE["hud_amber"], outline_col, lw=1.6)
            else:
                # Tóc nam hiện đại (side-part taper)
                ctx.new_sub_path()
                ctx.move_to(-13, -18)
                ctx.curve_to(-18, -29, -9, -40, 4, -40)
                ctx.curve_to(15, -40, 20, -34, 18, -24)
                ctx.curve_to(14, -28, 7, -30, 2, -28)
                ctx.curve_to(-4, -26, -7, -22, -8, -15)
                ctx.close_path()
                stroke_and_fill(ctx, hair_dark, outline_col, lw=1.6)

                # Highlight tóc
                ctx.new_sub_path()
                ctx.move_to(-3, -38)
                ctx.curve_to(3, -39, 9, -38, 13, -34)
                ctx.curve_to(7, -36, 0, -37, -3, -36)
                ctx.close_path()
                stroke_and_fill(ctx, hair_hl, None)

            draw_pivot_marker(ctx)

        # 3. Bàn tay (Hand)
        def draw_hand(ctx, fill_col):
            ctx.new_sub_path()
            ctx.move_to(-3.5, 0)
            ctx.curve_to(-5, 7, -5, 10, -3.5, 12)
            ctx.curve_to(-2, 12, -1, 10, -0.8, 8.5)
            ctx.line_to(1.8, 12.5)
            ctx.curve_to(3.8, 12.5, 4.2, 10, 3.5, 7.5)
            ctx.line_to(3.0, 0)
            ctx.close_path()
            stroke_and_fill(ctx, fill_col, outline_col, lw=1.3)
            draw_pivot_marker(ctx)

        # 4. Giày (Shoe / Sneaker)
        def draw_foot(ctx, is_far=False):
            f_main = shade_color(shoe_main, 0.8) if is_far else shoe_main
            f_sole = "#CBD5E1" if is_far else shoe_sole

            if variant == "diver":
                ctx.new_sub_path()
                ctx.move_to(-6, -3)
                ctx.line_to(44, 5)
                ctx.line_to(40, 16)
                ctx.line_to(-8, 10)
                ctx.close_path()
                stroke_and_fill(ctx, f_main, outline_col, lw=1.8)
            else:
                ctx.new_sub_path()
                ctx.move_to(-7, -2)
                ctx.curve_to(-9, 4, -8, 7, -7, 10)
                ctx.line_to(20, 10)
                ctx.curve_to(23, 7, 21, 3, 17, 2)
                ctx.line_to(7, 1)
                ctx.curve_to(1, -2, -1, -2, -7, -2)
                ctx.close_path()
                stroke_and_fill(ctx, f_main, outline_col, lw=1.5)
                rounded_rect(ctx, -8, 9, 30, 5.0, 2)
                stroke_and_fill(ctx, f_sole, outline_col, lw=1.3)
            draw_pivot_marker(ctx)

        root = BoneNode("torso", 0, 0, draw_fn=draw_torso, z_index=0)
        bones["torso"] = root
        bones["head"] = root.add_child(BoneNode("head", 2, -66, draw_fn=draw_head, z_index=-1))

        # Chỉ diver hoặc explorer mới đeo bình khí/balo, casual/formal KHÔNG CÓ balo
        if variant == "diver":
            def draw_backpack(ctx):
                rounded_rect(ctx, -24, -30, 16, 56, 7)
                stroke_and_fill(ctx, "#94A3B8", outline_col, lw=1.6)
                rounded_rect(ctx, -24, -20, 16, 10, 2)
                stroke_and_fill(ctx, "#F59E0B", outline_col, lw=1.4)
                draw_pivot_marker(ctx)
            bones["backpack"] = root.add_child(BoneNode("backpack", -14, -30, draw_fn=draw_backpack, z_index=-3))
        elif variant == "explorer":
            def draw_backpack(ctx):
                rounded_rect(ctx, -24, -28, 18, 52, 6)
                stroke_and_fill(ctx, PALETTE["wood_brown"], outline_col, lw=1.6)
                draw_pivot_marker(ctx)
            bones["backpack"] = root.add_child(BoneNode("backpack", -14, -30, draw_fn=draw_backpack, z_index=-3))

        # Lắp 2 tay & 2 chân theo tỷ lệ giải phẫu chuẩn
        # Cánh tay: khuỷu tay ngang eo (y=-18), cổ tay ngang hông (y=18), ngón tay ngang giữa đùi (y=30)
        # Chân: đùi dài 58px, cẳng chân dài 56px, bàn chân 12px
        # Chân đặt tại z=-2 (L) và z=-1 (R) để chỏm xoay khớp háng luôn ẩn mượt mà dưới gấu áo và hông quần
        for side, z_arm, z_leg, is_far in [("L", -2, -2, True), ("R", 2, -1, False)]:
            arm_col = shade_color(top_col, 0.82) if is_far else top_col
            leg_col = shade_color(pants_col, 0.82) if is_far else pants_col
            skin_c  = shade_color(skin, 0.85) if is_far else skin

            px_arm = -2 if is_far else 2
            px_leg = -2 if is_far else 2

            ua = root.add_child(BoneNode(
                f"arm_upper_{side}", px_arm, -60, z_index=z_arm,
                draw_fn=lambda c, col=arm_col: draw_capsule_limb(c, 42, 7.5, 6.2, col, is_child=False)
            ))
            la = ua.add_child(BoneNode(
                f"arm_lower_{side}", 0, 42,
                draw_fn=lambda c, col=arm_col: draw_capsule_limb(c, 36, 6.2, 5.0, col, is_child=True, is_terminal=False)
            ))
            hand = la.add_child(BoneNode(
                f"hand_{side}", 0, 36,
                draw_fn=lambda c, sc=skin_c: draw_hand(c, sc)
            ))

            ul = root.add_child(BoneNode(
                f"leg_upper_{side}", px_leg, 2, z_index=z_leg,
                draw_fn=lambda c, col=leg_col: draw_capsule_limb(c, 58, 9.5, 8.0, col, is_child=False)
            ))
            ll = ul.add_child(BoneNode(
                f"leg_lower_{side}", 0, 58,
                draw_fn=lambda c, col=leg_col: draw_capsule_limb(c, 56, 8.0, 6.2, col, is_child=True, is_terminal=False)
            ))
            foot = ll.add_child(BoneNode(
                f"foot_{side}", 0, 56,
                draw_fn=lambda c, far=is_far: draw_foot(c, far)
            ))

            bones[f"arm_upper_{side}"] = ua
            bones[f"arm_lower_{side}"] = la
            bones[f"hand_{side}"] = hand
            bones[f"leg_upper_{side}"] = ul
            bones[f"leg_lower_{side}"] = ll
            bones[f"foot_{side}"] = foot

        return ActorRig(f"human_{variant}", root, bones)

    # --------------------------------------------------------------------------
    # 3.2. CÁ MẬP / CÁ VOI SÁT THỦ CHIA ĐỐT (SEGMENTED MARINE PREDATOR)
    # --------------------------------------------------------------------------
    @staticmethod
    def build_shark_rig(variant="shark"):
        bones = {}
        dorsal_col = PALETTE["slate_dark"] if variant == "orca" else PALETTE["teal_Suit" if False else "slate_mid"]
        belly_col = PALETTE["hud_white"] if variant == "orca" else PALETTE["silver_belly"]

        def draw_body_ant(ctx):
            # Khoang ngực + Vây lưng lớn
            ctx.move_to(50, -32)
            ctx.curve_to(20, -42, -30, -42, -65, -34)
            ctx.line_to(-65, 32)
            ctx.curve_to(-30, 42, 20, 42, 50, 28)
            ctx.close_path()
            stroke_and_fill(ctx, dorsal_col, PALETTE["outline"])

            # Mảng bụng sáng màu
            ctx.move_to(50, 8)
            ctx.curve_to(10, 14, -30, 14, -65, 10)
            ctx.line_to(-65, 32)
            ctx.curve_to(-30, 42, 20, 42, 50, 28)
            ctx.close_path()
            stroke_and_fill(ctx, belly_col, PALETTE["outline"])

            # Vây lưng (Dorsal Fin)
            ctx.move_to(5, -38)
            ctx.curve_to(-5, -85, -25, -95, -45, -98)
            ctx.curve_to(-32, -70, -28, -50, -38, -36)
            ctx.close_path()
            stroke_and_fill(ctx, dorsal_col, PALETTE["outline"])

            # Khe mang (Gill slits)
            if variant == "shark":
                for gx in (18, 26, 34, 42):
                    ctx.move_to(gx, -10)
                    ctx.line_to(gx - 3, 12)
                    stroke_and_fill(ctx, None, PALETTE["outline"], lw=2.2)
            draw_pivot_marker(ctx)

        def draw_head(ctx):
            ctx.move_to(0, -30)
            ctx.curve_to(45, -26, 85, -12, 105, 2)
            ctx.curve_to(75, 10, 35, 10, 0, 8)
            ctx.close_path()
            stroke_and_fill(ctx, dorsal_col, PALETTE["outline"])
            # Mắt
            ctx.new_sub_path()
            ctx.arc(48, -8, 4.5, 0, 2 * math.pi)
            stroke_and_fill(ctx, PALETTE["outline"], None)
            if variant == "orca":
                ctx.new_sub_path()
                ctx.arc(32, -14, 12, 0, 2 * math.pi)
                stroke_and_fill(ctx, PALETTE["hud_white"], None)
            draw_pivot_marker(ctx)

        def draw_jaw(ctx):
            # Răng hàm dưới
            for tx in range(12, 62, 10):
                ctx.move_to(tx, 2)
                ctx.line_to(tx + 4, -7)
                ctx.line_to(tx + 8, 2)
                ctx.close_path()
                stroke_and_fill(ctx, PALETTE["hud_white"], PALETTE["outline"], lw=1.8)
            # Xương hàm dưới
            ctx.move_to(0, 0)
            ctx.line_to(72, 2)
            ctx.curve_to(55, 20, 20, 24, 0, 20)
            ctx.close_path()
            stroke_and_fill(ctx, belly_col, PALETTE["outline"])
            draw_pivot_marker(ctx)

        def draw_segment(ctx, length, h_front, h_back):
            ctx.move_to(0, -h_front)
            ctx.line_to(-length, -h_back)
            ctx.line_to(-length, h_back)
            ctx.line_to(0, h_front)
            ctx.close_path()
            stroke_and_fill(ctx, dorsal_col, PALETTE["outline"])
            # Phần bụng dưới
            ctx.move_to(0, h_front * 0.3)
            ctx.line_to(-length, h_back * 0.3)
            ctx.line_to(-length, h_back)
            ctx.line_to(0, h_front)
            ctx.close_path()
            stroke_and_fill(ctx, belly_col, PALETTE["outline"])
            draw_pivot_marker(ctx)

        def draw_caudal_fin(ctx):
            ctx.move_to(0, -8)
            ctx.curve_to(-28, -55, -52, -78, -75, -82)
            ctx.curve_to(-55, -42, -42, -15, -32, 0)
            ctx.curve_to(-42, 15, -50, 38, -65, 62)
            ctx.curve_to(-42, 55, -20, 32, 0, 8)
            ctx.close_path()
            stroke_and_fill(ctx, dorsal_col, PALETTE["outline"])
            draw_pivot_marker(ctx)

        def draw_flipper(ctx):
            ctx.move_to(-10, 0)
            ctx.curve_to(-5, 38, -28, 72, -52, 86)
            ctx.curve_to(-22, 82, 12, 52, 18, 6)
            ctx.close_path()
            stroke_and_fill(ctx, dorsal_col, PALETTE["outline"])
            draw_pivot_marker(ctx)

        root = BoneNode("body_ant", 0, 0, draw_fn=draw_body_ant, z_index=0)
        bones["body_ant"] = root
        bones["head"] = root.add_child(BoneNode("head", 46, -2, draw_fn=draw_head, z_index=1))
        bones["jaw"] = bones["head"].add_child(BoneNode("jaw", 4, 8, draw_fn=draw_jaw, z_index=-1))

        mid = root.add_child(BoneNode("body_mid", -62, 0, draw_fn=lambda c: draw_segment(c, 68, 32, 21), z_index=-1))
        ped = mid.add_child(BoneNode("tail_peduncle", -65, 0, draw_fn=lambda c: draw_segment(c, 56, 20, 10), z_index=-1))
        fin = ped.add_child(BoneNode("fin_caudal", -54, 0, draw_fn=draw_caudal_fin, z_index=-1))

        bones["body_mid"] = mid
        bones["tail_peduncle"] = ped
        bones["fin_caudal"] = fin
        bones["flipper_R"] = root.add_child(BoneNode("flipper_R", 18, 22, draw_fn=draw_flipper, z_index=2))
        bones["flipper_L"] = root.add_child(BoneNode("flipper_L", 26, 20, draw_fn=draw_flipper, z_index=-2))

        return ActorRig(variant, root, bones)

    # --------------------------------------------------------------------------
    # 3.3. CÁ VOI LƯNG GÙ / CÁ VOI XANH (WHALE RIG)
    # --------------------------------------------------------------------------
    @staticmethod
    def build_whale_rig():
        rig = RigBuilder.build_shark_rig(variant="shark")
        rig.rig_type = "whale"

        def draw_whale_head(ctx):
            ctx.move_to(0, -36)
            ctx.curve_to(65, -36, 110, -24, 115, 6)
            ctx.line_to(0, 6)
            ctx.close_path()
            stroke_and_fill(ctx, PALETTE["teal_deep"], PALETTE["outline"])
            ctx.arc(32, -4, 4.0, 0, 2 * math.pi)
            stroke_and_fill(ctx, PALETTE["outline"], None)
            draw_pivot_marker(ctx)

        def draw_whale_jaw(ctx):
            ctx.move_to(0, 0)
            ctx.line_to(108, 0)
            ctx.curve_to(100, 34, 45, 42, 0, 28)
            ctx.close_path()
            stroke_and_fill(ctx, PALETTE["silver_belly"], PALETTE["outline"])
            # Nếp gấp cổ họng (Ventral pleats)
            for py in (8, 15, 22):
                ctx.move_to(8, py)
                ctx.line_to(85 - py, py * 0.7)
                stroke_and_fill(ctx, None, PALETTE["slate_mid"], lw=1.8)
            draw_pivot_marker(ctx)

        rig.bones["head"].draw_fn = draw_whale_head
        rig.bones["jaw"].draw_fn = draw_whale_jaw
        return rig

    # --------------------------------------------------------------------------
    # 3.4. CHIM BIỂN / ĐẠI BÀNG TÁCH KHỚP CÁNH (AVIAN RIG)
    # --------------------------------------------------------------------------
    @staticmethod
    def build_bird_rig():
        bones = {}

        def draw_torso(ctx):
            ctx.move_to(35, -8)
            ctx.curve_to(15, -24, -20, -20, -42, -4)
            ctx.curve_to(-20, 18, 15, 20, 35, 6)
            ctx.close_path()
            stroke_and_fill(ctx, PALETTE["hud_white"], PALETTE["outline"])
            draw_pivot_marker(ctx)

        def draw_head(ctx):
            ctx.arc(12, -4, 13, 0, 2 * math.pi)
            stroke_and_fill(ctx, PALETTE["hud_white"], PALETTE["outline"])
            # Mỏ chim
            ctx.move_to(23, -8)
            ctx.line_to(46, -2)
            ctx.line_to(23, 3)
            ctx.close_path()
            stroke_and_fill(ctx, PALETTE["hud_amber"], PALETTE["outline"])
            ctx.arc(15, -6, 2.5, 0, 2 * math.pi)
            stroke_and_fill(ctx, PALETTE["outline"], None)
            draw_pivot_marker(ctx)

        def draw_tail(ctx):
            ctx.move_to(0, -4)
            ctx.line_to(-38, -14)
            ctx.line_to(-34, 12)
            ctx.line_to(0, 4)
            ctx.close_path()
            stroke_and_fill(ctx, PALETTE["slate_mid"], PALETTE["outline"])
            draw_pivot_marker(ctx)

        def draw_wing_inner(ctx):
            ctx.move_to(0, 0)
            ctx.line_to(-12, -48)
            ctx.line_to(-32, -42)
            ctx.line_to(-18, 8)
            ctx.close_path()
            stroke_and_fill(ctx, PALETTE["slate_light"], PALETTE["outline"])
            draw_pivot_marker(ctx)

        def draw_wing_outer(ctx):
            ctx.move_to(0, 0)
            ctx.line_to(-18, -56)
            ctx.line_to(-38, -12)
            ctx.line_to(-15, 6)
            ctx.close_path()
            stroke_and_fill(ctx, PALETTE["slate_dark"], PALETTE["outline"])
            draw_pivot_marker(ctx)

        root = BoneNode("torso", 0, 0, draw_fn=draw_torso)
        bones["torso"] = root
        bones["head"] = root.add_child(BoneNode("head", 32, -4, draw_fn=draw_head, z_index=1))
        bones["tail"] = root.add_child(BoneNode("tail", -38, 0, draw_fn=draw_tail, z_index=-1))

        for side, z in [("L", -1), ("R", 1)]:
            wi = root.add_child(BoneNode(f"wing_inner_{side}", 4, -8, draw_fn=draw_wing_inner, z_index=z))
            wo = wi.add_child(BoneNode(f"wing_outer_{side}", -14, -44, draw_fn=draw_wing_outer, z_index=z))
            bones[f"wing_inner_{side}"] = wi
            bones[f"wing_outer_{side}"] = wo

        return ActorRig("bird", root, bones)

    # --------------------------------------------------------------------------
    # 3.5. ĐỘNG VẬT 4 CHÂN (QUADRUPED: WOLF / BEAR)
    # --------------------------------------------------------------------------
    @staticmethod
    def build_quadruped_rig(variant="wolf"):
        bones = {}
        coat_col = PALETTE["fur_brown"] if variant == "bear" else PALETTE["slate_mid"]
        dark_col = PALETTE["fur_dark"] if variant == "bear" else PALETTE["slate_dark"]

        def draw_torso(ctx):
            rounded_rect(ctx, -52, -26, 104, 52, 22)
            stroke_and_fill(ctx, coat_col, PALETTE["outline"])
            draw_pivot_marker(ctx)

        def draw_head(ctx):
            rounded_rect(ctx, -10, -22, 42, 32, 12)
            stroke_and_fill(ctx, coat_col, PALETTE["outline"])
            # Mõm
            rounded_rect(ctx, 24, -12, 26, 18, 6)
            stroke_and_fill(ctx, dark_col, PALETTE["outline"])
            # Tai
            ctx.move_to(2, -20)
            ctx.line_to(10, -38)
            ctx.line_to(20, -20)
            ctx.close_path()
            stroke_and_fill(ctx, dark_col, PALETTE["outline"])
            ctx.arc(20, -10, 3.0, 0, 2 * math.pi)
            stroke_and_fill(ctx, PALETTE["hud_amber"], PALETTE["outline"], lw=1.5)
            draw_pivot_marker(ctx)

        root = BoneNode("torso", 0, 0, draw_fn=draw_torso)
        bones["torso"] = root
        bones["head"] = root.add_child(BoneNode("head", 46, -18, draw_fn=draw_head, z_index=1))
        bones["tail"] = root.add_child(BoneNode(
            "tail", -50, -12, base_angle=35, z_index=-1,
            draw_fn=lambda c: draw_capsule_limb(c, 36 if variant == "wolf" else 14, 7, 4, dark_col)
        ))

        leg_coords = [("FR", 34, 16, 1), ("FL", 38, 14, -1), ("BR", -36, 16, 1), ("BL", -32, 14, -1)]
        for tag, lx, ly, z in leg_coords:
            c_col = coat_col if z > 0 else dark_col
            ul = root.add_child(BoneNode(
                f"leg_upper_{tag}", lx, ly, z_index=z,
                draw_fn=lambda c, col=c_col: draw_capsule_limb(c, 34, 9.5, 7.5, col)
            ))
            ll = ul.add_child(BoneNode(
                f"leg_lower_{tag}", 0, 34,
                draw_fn=lambda c, col=c_col: draw_capsule_limb(c, 30, 7.0, 5.5, col)
            ))
            bones[f"leg_upper_{tag}"] = ul
            bones[f"leg_lower_{tag}"] = ll

        return ActorRig(f"quadruped_{variant}", root, bones)

    # --------------------------------------------------------------------------
    # 3.6. TÀU NGHIÊN CỨU & TÀU LẶN (VESSEL & SUBMERSIBLE RIGS)
    # --------------------------------------------------------------------------
    @staticmethod
    def build_vessel_rig(variant="submersible"):
        bones = {}
        if variant == "submersible":
            def draw_hull(ctx):
                # Thân tàu ngầm vàng hổ phách
                rounded_rect(ctx, -65, -42, 130, 84, 38)
                stroke_and_fill(ctx, PALETTE["hud_amber"], PALETTE["outline"])
                # Vòm kính quan sát phía trước
                ctx.arc(42, 0, 26, -math.pi / 2, math.pi / 2)
                ctx.close_path()
                stroke_and_fill(ctx, PALETTE["teal_light"], PALETTE["outline"])
                # Cửa sổ tròn bên hông
                ctx.arc(-10, -4, 16, 0, 2 * math.pi)
                stroke_and_fill(ctx, PALETTE["teal_deep"], PALETTE["outline"], lw=3.2)
                # Chân đế đáp đáy biển
                rounded_rect(ctx, -48, 46, 96, 8, 4)
                stroke_and_fill(ctx, PALETTE["slate_dark"], PALETTE["outline"])
                draw_pivot_marker(ctx)

            def draw_propeller(ctx):
                for sign in (-1, 1):
                    ctx.move_to(0, 0)
                    ctx.curve_to(-14, sign * 24, -4, sign * 30, 0, sign * 6)
                    stroke_and_fill(ctx, PALETTE["alert_coral"], PALETTE["outline"])
                draw_pivot_marker(ctx)

            def draw_spotlight(ctx):
                # Luồng sáng hình nón bán trong suốt
                grad = cairo.LinearGradient(0, 0, 240, 0)
                grad.add_color_stop_rgba(0.0, 0.96, 0.76, 0.26, 0.42)
                grad.add_color_stop_rgba(1.0, 0.96, 0.76, 0.26, 0.0)
                ctx.move_to(0, -6)
                ctx.line_to(240, -65)
                ctx.line_to(240, 65)
                ctx.line_to(0, 6)
                ctx.close_path()
                ctx.set_source(grad)
                ctx.fill()
                rounded_rect(ctx, -8, -8, 16, 16, 4)
                stroke_and_fill(ctx, PALETTE["slate_dark"], PALETTE["outline"])
                draw_pivot_marker(ctx)

            root = BoneNode("hull", 0, 0, draw_fn=draw_hull)
            bones["hull"] = root
            bones["propeller"] = root.add_child(BoneNode("propeller", -72, 0, draw_fn=draw_propeller, z_index=-1))
            bones["spotlight"] = root.add_child(BoneNode("spotlight", 62, -24, draw_fn=draw_spotlight, z_index=2))
            arm1 = root.add_child(BoneNode(
                "claw_arm", 48, 28, base_angle=-25, z_index=1,
                draw_fn=lambda c: draw_capsule_limb(c, 36, 5.5, 4.5, PALETTE["slate_mid"])
            ))
            bones["claw_arm"] = arm1
            return ActorRig("submersible", root, bones)

        # Mặc định: Tàu nghiên cứu mặt nước (research_boat)
        def draw_boat_hull(ctx):
            # Cabin trắng
            rounded_rect(ctx, -35, -62, 68, 42, 6)
            stroke_and_fill(ctx, PALETTE["hud_white"], PALETTE["outline"])
            # Thân tàu
            ctx.move_to(-110, -22)
            ctx.line_to(115, -28)
            ctx.line_to(92, 24)
            ctx.line_to(-98, 24)
            ctx.close_path()
            stroke_and_fill(ctx, PALETTE["slate_dark"], PALETTE["outline"])
            # Sọc cảnh báo màu cam
            ctx.move_to(-102, -4)
            ctx.line_to(102, -6)
            stroke_and_fill(ctx, None, PALETTE["hud_amber"], lw=6.0)
            draw_pivot_marker(ctx)

        def draw_radar(ctx):
            rounded_rect(ctx, -18, -4, 36, 8, 3)
            stroke_and_fill(ctx, PALETTE["hud_amber"], PALETTE["outline"])
            draw_pivot_marker(ctx)

        root = BoneNode("hull", 0, 0, draw_fn=draw_boat_hull)
        bones["hull"] = root
        bones["radar"] = root.add_child(BoneNode("radar", 0, -72, draw_fn=draw_radar, z_index=1))
        return ActorRig("research_boat", root, bones)


# ==============================================================================
# 4. BỘ GIẢI CHUYỂN ĐỘNG PROCEDURAL (PROCEDURAL MOTION SOLVERS)
# ==============================================================================
class ProceduralMotion:
    """Biến đổi các góc khớp (anim_angle) và vị trí theo hàm lượng giác thời gian t."""

    @staticmethod
    def apply_idle(rig, t, freq=1.8, amp=3.5, **_):
        w = t * freq
        if "torso" in rig.bones:
            rig.bones["torso"].offset_y = amp * math.sin(w)
        if "head" in rig.bones:
            rig.bones["head"].anim_angle = 2.5 * math.sin(w - 0.5)
        for side, sign in [("L", 1), ("R", -1)]:
            if f"arm_upper_{side}" in rig.bones:
                rig.bones[f"arm_upper_{side}"].anim_angle = sign * 4.0 * math.sin(w - 0.4)

    @staticmethod
    def apply_walk(rig, t, freq=4.5, stride_deg=32.0, **_):
        w = t * freq
        for side, phase in [("L", w), ("R", w + math.pi)]:
            if f"leg_upper_{side}" in rig.bones:
                rig.bones[f"leg_upper_{side}"].anim_angle = stride_deg * math.sin(phase)
            if f"leg_lower_{side}" in rig.bones:
                rig.bones[f"leg_lower_{side}"].anim_angle = max(0.0, stride_deg * 1.15 * math.sin(phase - 1.4))
            if f"foot_{side}" in rig.bones:
                rig.bones[f"foot_{side}"].anim_angle = 10.0 * math.cos(phase)

        for side, phase in [("L", w + math.pi), ("R", w)]:
            if f"arm_upper_{side}" in rig.bones:
                rig.bones[f"arm_upper_{side}"].anim_angle = (stride_deg * 0.65) * math.sin(phase)
            if f"arm_lower_{side}" in rig.bones:
                rig.bones[f"arm_lower_{side}"].anim_angle = -abs(stride_deg * 0.45) * (0.5 + 0.5 * math.sin(phase))

        if "torso" in rig.bones:
            rig.bones["torso"].offset_y = 4.5 * abs(math.sin(w))
            rig.bones["torso"].anim_angle = 3.5 * math.sin(w)

    @staticmethod
    def apply_swim_human(rig, t, freq=3.2, kick_deg=26.0, horizontal=True, **_):
        w = t * freq
        if "torso" in rig.bones:
            rig.bones["torso"].base_angle = 78.0 if horizontal else 8.0
            rig.bones["torso"].offset_y = 6.0 * math.sin(w * 0.6)
        if "head" in rig.bones:
            rig.bones["head"].base_angle = -52.0 if horizontal else 0.0
            rig.bones["head"].anim_angle = 5.0 * math.sin(w * 0.6 - 0.4)

        for side, phase in [("L", w), ("R", w + math.pi)]:
            if f"leg_upper_{side}" in rig.bones:
                rig.bones[f"leg_upper_{side}"].anim_angle = kick_deg * math.sin(phase)
            if f"leg_lower_{side}" in rig.bones:
                rig.bones[f"leg_lower_{side}"].anim_angle = max(0.0, kick_deg * 0.85 * math.sin(phase - 1.1))
            if f"foot_{side}" in rig.bones:
                rig.bones[f"foot_{side}"].anim_angle = 18.0 * math.sin(phase - 1.6)
            if f"arm_upper_{side}" in rig.bones:
                rig.bones[f"arm_upper_{side}"].base_angle = -25.0 if horizontal else 15.0
                rig.bones[f"arm_upper_{side}"].anim_angle = 16.0 * math.sin(phase * 0.5)

    @staticmethod
    def apply_spine_undulation(rig, t, freq=3.6, amp_deg=15.0, jaw_open=0.2, **_):
        w = t * freq
        chain = ["body_ant", "body_mid", "tail_peduncle", "fin_caudal"]
        for i, name in enumerate(chain):
            if name in rig.bones:
                factor = 0.25 + 0.42 * i
                rig.bones[name].anim_angle = (amp_deg * factor) * math.sin(w - i * 0.85)
        if "body_ant" in rig.bones:
            rig.bones["body_ant"].offset_y = 5.0 * math.sin(w)
        for side, offset in [("R", -0.5), ("L", -0.8)]:
            if f"flipper_{side}" in rig.bones:
                rig.bones[f"flipper_{side}"].anim_angle = 18.0 * math.sin(w + offset)
        if "jaw" in rig.bones:
            rig.bones["jaw"].anim_angle = jaw_open * 32.0 * (0.65 + 0.35 * math.sin(w * 0.7))

    @staticmethod
    def apply_wing_flap(rig, t, freq=5.2, flap_deg=38.0, **_):
        w = t * freq
        if "torso" in rig.bones:
            rig.bones["torso"].offset_y = -6.0 * math.sin(w)
        for side in ("L", "R"):
            if f"wing_inner_{side}" in rig.bones:
                rig.bones[f"wing_inner_{side}"].anim_angle = flap_deg * math.sin(w)
            if f"wing_outer_{side}" in rig.bones:
                rig.bones[f"wing_outer_{side}"].anim_angle = (flap_deg * 0.75) * math.sin(w - 0.65)
        if "tail" in rig.bones:
            rig.bones["tail"].anim_angle = 8.0 * math.sin(w - 1.0)

    @staticmethod
    def apply_quadruped_gait(rig, t, freq=5.5, stride_deg=34.0, **_):
        w = t * freq
        phases = {"FR": w, "FL": w + 0.5, "BR": w + math.pi, "BL": w + math.pi + 0.5}
        for tag, ph in phases.items():
            if f"leg_upper_{tag}" in rig.bones:
                rig.bones[f"leg_upper_{tag}"].anim_angle = stride_deg * math.sin(ph)
            if f"leg_lower_{tag}" in rig.bones:
                rig.bones[f"leg_lower_{tag}"].anim_angle = max(0.0, stride_deg * 0.9 * math.sin(ph - 1.3))
        if "torso" in rig.bones:
            rig.bones["torso"].offset_y = 5.0 * abs(math.sin(w))
            rig.bones["torso"].anim_angle = 4.0 * math.sin(w)
        if "tail" in rig.bones:
            rig.bones["tail"].anim_angle = 14.0 * math.sin(w * 1.2)

    @staticmethod
    def apply_vessel_cruise(rig, t, freq=2.0, bob_amp=6.0, **_):
        w = t * freq
        if "hull" in rig.bones:
            rig.bones["hull"].offset_y = bob_amp * math.sin(w)
            rig.bones["hull"].anim_angle = 2.8 * math.sin(w * 0.7)
        if "propeller" in rig.bones:
            rig.bones["propeller"].scale_y = math.sin(t * 18.0)
        if "radar" in rig.bones:
            rig.bones["radar"].scale_x = math.cos(t * 4.5)
        if "spotlight" in rig.bones:
            rig.bones["spotlight"].anim_angle = 10.0 * math.sin(t * 0.9)

    @staticmethod
    def apply_sitting(rig, t, freq=1.5, **_):
        """Tư thế ngồi thư thái hoặc làm việc tại bàn."""
        w = t * freq
        if "torso" in rig.bones:
            rig.bones["torso"].offset_y = 18.0 + 1.5 * math.sin(w)
            rig.bones["torso"].base_angle = 4.0
        if "head" in rig.bones:
            rig.bones["head"].anim_angle = 3.0 * math.sin(w * 0.8)
        for side in ("L", "R"):
            if f"leg_upper_{side}" in rig.bones:
                rig.bones[f"leg_upper_{side}"].base_angle = -75.0
            if f"leg_lower_{side}" in rig.bones:
                rig.bones[f"leg_lower_{side}"].base_angle = 80.0
            if f"arm_upper_{side}" in rig.bones:
                rig.bones[f"arm_upper_{side}"].base_angle = 32.0
            if f"arm_lower_{side}" in rig.bones:
                rig.bones[f"arm_lower_{side}"].base_angle = -48.0

    @staticmethod
    def apply_typing_desk(rig, t, freq=7.0, **_):
        """Đang gõ bàn phím laptop/máy tính với nhịp tay sống động."""
        ProceduralMotion.apply_sitting(rig, t, freq=1.2)
        w = t * freq
        for side, sign in [("L", 1), ("R", -1)]:
            if f"arm_lower_{side}" in rig.bones:
                rig.bones[f"arm_lower_{side}"].anim_angle = sign * 6.5 * math.sin(w + (0 if side == "L" else 1.8))
        if "head" in rig.bones:
            rig.bones["head"].base_angle = 12.0
            rig.bones["head"].anim_angle = 2.0 * math.sin(w * 0.3)

    @staticmethod
    def apply_talk(rig, t, freq=3.2, gesture_amp=14.0, **_):
        """Nhân vật đang nói chuyện, diễn giải (đầu cử động, tay nhấn nhá)."""
        w = t * freq
        ProceduralMotion.apply_idle(rig, t, freq=1.4)
        if "head" in rig.bones:
            rig.bones["head"].anim_angle = 4.5 * math.sin(w) + 2.0 * math.sin(w * 2.3)
        if "arm_upper_R" in rig.bones:
            rig.bones["arm_upper_R"].anim_angle = -gesture_amp * (0.6 + 0.4 * math.sin(w * 0.8))
        if "arm_lower_R" in rig.bones:
            rig.bones["arm_lower_R"].anim_angle = -18.0 * (0.5 + 0.5 * math.sin(w * 0.8 - 0.5))

    @staticmethod
    def apply_inspect(rig, t, freq=1.6, **_):
        """Cúi nhìn, kiểm tra tài liệu, bản vẽ hoặc dụng cụ."""
        w = t * freq
        if "torso" in rig.bones:
            rig.bones["torso"].base_angle = 14.0
            rig.bones["torso"].offset_y = 2.0 * math.sin(w)
        if "head" in rig.bones:
            rig.bones["head"].base_angle = 22.0
            rig.bones["head"].anim_angle = 3.0 * math.sin(w)
        if "arm_upper_R" in rig.bones:
            rig.bones["arm_upper_R"].base_angle = 35.0
        if "arm_lower_R" in rig.bones:
            rig.bones["arm_lower_R"].base_angle = -45.0

    @classmethod
    def apply_preset(cls, rig, preset_name, t, **params):
        rig.reset_pose()
        dispatch = {
            "idle": cls.apply_idle,
            "walk": cls.apply_walk,
            "swim_horizontal": lambda r, time, **kw: cls.apply_swim_human(r, time, horizontal=True, **kw),
            "swim_tread": lambda r, time, **kw: cls.apply_swim_human(r, time, horizontal=False, **kw),
            "spine_undulation": cls.apply_spine_undulation,
            "wing_flap": cls.apply_wing_flap,
            "quadruped_gait": cls.apply_quadruped_gait,
            "vessel_cruise": cls.apply_vessel_cruise,
            "sitting": cls.apply_sitting,
            "typing": cls.apply_typing_desk,
            "typing_desk": cls.apply_typing_desk,
            "talk": cls.apply_talk,
            "inspect": cls.apply_inspect,
        }
        fn = dispatch.get(preset_name, cls.apply_idle)
        fn(rig, t, **params)


# ==============================================================================
# 5. MÔI TRƯỜNG PARALLAX & BỐI CẢNH TÁI SỬ DỤNG (ENVIRONMENT RENDERER)
# ==============================================================================
class EnvironmentRenderer:
    """Vẽ các bối cảnh tiêu chuẩn có chiều sâu Parallax và hiệu ứng ánh sáng."""

    @staticmethod
    def draw_underwater_cross_section(ctx, W, H, t, surf_y=210, cam_x=0.0, deep_mode=False):
        # 1. Bầu trời phía trên mặt nước
        if surf_y > 0:
            sky_g = cairo.LinearGradient(0, 0, 0, surf_y + 20)
            sky_g.add_color_stop_rgb(0.0, *hex_rgb("#64869A"))
            sky_g.add_color_stop_rgb(1.0, *hex_rgb("#BBD0DC"))
            ctx.rectangle(0, 0, W, surf_y + 20)
            ctx.set_source(sky_g)
            ctx.fill()

        # 2. Khối nước đại dương & Sóng mặt nước
        wat_g = cairo.LinearGradient(0, max(0, surf_y), 0, H)
        wat_g.add_color_stop_rgb(0.0, *hex_rgb("#184E60" if deep_mode else "#2E7D91"))
        wat_g.add_color_stop_rgb(0.55, *hex_rgb("#0A2C3B" if deep_mode else "#134B5E"))
        wat_g.add_color_stop_rgb(1.0, *hex_rgb("#04131C" if deep_mode else "#061C29"))

        if surf_y > 0:
            ctx.move_to(0, H)
            ctx.line_to(0, surf_y)
            for x in range(0, W + 32, 32):
                wy = surf_y + 6.5 * math.sin(x * 0.008 + t * 2.2 + cam_x * 0.005)
                ctx.line_to(x, wy)
            ctx.line_to(W, H)
            ctx.close_path()
        else:
            ctx.rectangle(0, 0, W, H)
        ctx.set_source(wat_g)
        ctx.fill()

        # 3. Luồng tia nắng xuyên qua mặt nước (Volumetric Sunbeams)
        ray_top = max(0, surf_y)
        rays = [(260, 95, 250, 0.09), (620, 135, 320, 0.12), (1040, 90, 240, 0.08), (1460, 145, 340, 0.11)]
        for i, (rx_base, rw_top, rw_bot, op) in enumerate(rays):
            sway = 38.0 * math.sin(t * 0.7 + i * 1.4) - cam_x * 0.25
            x1 = (rx_base + sway) % (W + 300) - 150
            x2 = x1 + 210
            rg = cairo.LinearGradient(x1, ray_top, x2, H)
            rg.add_color_stop_rgba(0.0, 0.78, 0.95, 0.98, op)
            rg.add_color_stop_rgba(1.0, 0.50, 0.80, 0.90, 0.0)
            ctx.move_to(x1 - rw_top / 2, ray_top)
            ctx.line_to(x1 + rw_top / 2, ray_top)
            ctx.line_to(x2 + rw_bot / 2, H)
            ctx.line_to(x2 - rw_bot / 2, H)
            ctx.close_path()
            ctx.set_source(rg)
            ctx.fill()

        # 4. Đường gợn sóng khúc xạ dưới bề mặt
        if surf_y > 0:
            for li in range(1, 5):
                ctx.new_path()
                for x in range(0, W + 32, 32):
                    wy = surf_y + li * 12 + (5.5 - li * 0.8) * math.sin(x * 0.008 + t * 2.2 + li * 0.5)
                    ctx.move_to(x, wy) if x == 0 else ctx.line_to(x, wy)
                ctx.set_source_rgba(0.82, 0.96, 0.99, max(0.05, 0.30 - li * 0.06))
                ctx.set_line_width(2.8 if li == 1 else 1.5)
                ctx.stroke()

    @staticmethod
    def draw_mountain_forest_parallax(ctx, W, H, t, cam_x=0.0):
        # Bầu trời
        sky_g = cairo.LinearGradient(0, 0, 0, H * 0.75)
        sky_g.add_color_stop_rgb(0.0, *hex_rgb("#1B3B4B"))
        sky_g.add_color_stop_rgb(1.0, *hex_rgb("#64869A"))
        ctx.rectangle(0, 0, W, H)
        ctx.set_source(sky_g)
        ctx.fill()

        # Lớp 1: Núi xa (Parallax z = 0.15)
        ctx.move_to(0, H)
        for x in range(0, W + 80, 80):
            wx = x + cam_x * 0.15
            my = H * 0.55 - 110 * math.sin(wx * 0.0025) - 55 * math.cos(wx * 0.006)
            ctx.line_to(x, my)
        ctx.line_to(W, H)
        ctx.close_path()
        stroke_and_fill(ctx, "#2B4C5E", None)

        # Lớp 2: Rừng thông tầm trung (Parallax z = 0.45)
        base_y = H * 0.78
        ctx.rectangle(0, base_y, W, H - base_y)
        stroke_and_fill(ctx, "#163543", None)
        for i in range(-2, int(W / 65) + 3):
            tx = (i * 65 - (cam_x * 0.45) % 65)
            th = 75 + 25 * math.sin(i * 3.7)
            ctx.move_to(tx, base_y - th)
            ctx.line_to(tx - 22, base_y)
            ctx.line_to(tx + 22, base_y)
            ctx.close_path()
            stroke_and_fill(ctx, "#1F4454", PALETTE["outline"], lw=1.8)

        # Lớp 3: Mặt đất tiền cảnh (Parallax z = 1.0)
        fg_y = H * 0.84
        ctx.rectangle(0, fg_y, W, H - fg_y)
        stroke_and_fill(ctx, PALETTE["slate_dark"], PALETTE["outline"], lw=3.0)

    @staticmethod
    def draw_blueprint_grid(ctx, W, H, grid_size=48, cam_x=0.0, cam_y=0.0):
        ctx.rectangle(0, 0, W, H)
        stroke_and_fill(ctx, PALETTE["bg_navy"], None)

        ox = -(cam_x % grid_size)
        oy = -(cam_y % grid_size)
        ctx.set_source_rgba(*hex_rgb(PALETTE["grid_line"]), 0.75)
        ctx.set_line_width(1.2)
        for x in np.arange(ox, W, grid_size):
            ctx.move_to(x, 0)
            ctx.line_to(x, H)
        for y in np.arange(oy, H, grid_size):
            ctx.move_to(0, y)
            ctx.line_to(W, y)
        ctx.stroke()

        HUDRenderer.draw_viewfinder_brackets(ctx, 56, 48, W - 112, H - 96)

    @staticmethod
    def draw_historical_journal_card(ctx, W, H, title_text, body_lines, underline_progress=1.0):
        # Nền bàn tối
        ctx.rectangle(0, 0, W, H)
        stroke_and_fill(ctx, "#0B151C", None)

        # Trang giấy kem cổ điển (#F2EAD3)
        cw, ch = 1160, 660
        cx, cy = (W - cw) / 2, (H - ch) / 2
        rounded_rect(ctx, cx, cy, cw, ch, 14)
        stroke_and_fill(ctx, PALETTE["journal_cream"], PALETTE["outline"], lw=3.5)

        # Đường kẻ ngang sổ tay
        for ly in range(int(cy + 110), int(cy + ch - 40), 46):
            ctx.move_to(cx + 60, ly)
            ctx.line_to(cx + cw - 60, ly)
            stroke_and_fill(ctx, None, "#D5CBB4", lw=1.4)

        # Tiêu đề nhật ký
        ctx.select_font_face("Serif", cairo.FONT_SLANT_ITALIC, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(34)
        ctx.set_source_rgb(*hex_rgb(PALETTE["ink_crimson"]))
        ctx.move_to(cx + 80, cy + 88)
        ctx.show_text(title_text)

        # Nội dung các dòng nhật ký
        ctx.set_font_size(28)
        ctx.set_source_rgb(*hex_rgb(PALETTE["outline"]))
        for idx, line in enumerate(body_lines):
            ly = cy + 168 + idx * 68
            ctx.move_to(cx + 80, ly)
            ctx.show_text(line)
            if idx == len(body_lines) - 1 and underline_progress > 0:
                line_w = min(cw - 180, len(line) * 14.5) * min(1.0, underline_progress)
                ctx.move_to(cx + 80, ly + 10)
                ctx.line_to(cx + 80 + line_w, ly + 10)
                stroke_and_fill(ctx, None, PALETTE["ink_crimson"], lw=4.0)

    @staticmethod
    def draw_modern_workspace(ctx, W, H, t, cam_x=0.0):
        """Bối cảnh bàn làm việc đêm ấm cúng, cửa sổ mưa/ánh đèn thành phố và đèn bàn."""
        # 1. Nền phòng tối màu slate hiện đại
        bg = cairo.LinearGradient(0, 0, 0, H)
        bg.add_color_stop_rgb(0.0, *hex_rgb("#0F172A"))
        bg.add_color_stop_rgb(1.0, *hex_rgb("#1E293B"))
        ctx.rectangle(0, 0, W, H)
        ctx.set_source(bg)
        ctx.fill()

        # 2. Cửa sổ kính nhìn ra thành phố đêm
        win_x, win_y, win_w, win_h = 160, 140, 760, 520
        rounded_rect(ctx, win_x, win_y, win_w, win_h, 12)
        stroke_and_fill(ctx, "#0B1120", PALETTE["outline"], lw=3.0)

        # Ánh đèn bokeh mờ ảo ngoài cửa sổ
        bokeh_dots = [
            (win_x + 120, win_y + 180, 24, "#F59E0B", 0.35),
            (win_x + 280, win_y + 240, 32, "#38BDF8", 0.28),
            (win_x + 440, win_y + 160, 20, "#F43F5E", 0.30),
            (win_x + 600, win_y + 220, 28, "#10B981", 0.25),
            (win_x + 360, win_y + 340, 18, "#E0E7FF", 0.40),
        ]
        for bx, by, br, bcol, balpha in bokeh_dots:
            ctx.arc(bx + 4 * math.sin(t * 0.8 + bx), by, br, 0, 2 * math.pi)
            r, g, b = hex_rgb(bcol)
            ctx.set_source_rgba(r, g, b, balpha)
            ctx.fill()

        # Hạt mưa lăn trên kính
        ctx.set_line_width(1.2)
        ctx.set_source_rgba(0.7, 0.85, 1.0, 0.25)
        for rx in range(win_x + 30, win_x + win_w - 20, 48):
            ry = win_y + 20 + ((t * 80 + rx * 7) % (win_h - 40))
            ctx.move_to(rx, ry)
            ctx.line_to(rx - 4, ry + 16)
        ctx.stroke()

        # Khung chia ô cửa sổ
        ctx.set_source_rgb(*hex_rgb(PALETTE["outline"]))
        ctx.set_line_width(4.0)
        ctx.move_to(win_x + win_w / 2, win_y); ctx.line_to(win_x + win_w / 2, win_y + win_h); ctx.stroke()
        ctx.move_to(win_x, win_y + win_h / 2); ctx.line_to(win_x + win_w, win_y + win_h / 2); ctx.stroke()

        # 3. Sàn phòng
        floor_y = 780
        ctx.rectangle(0, floor_y, W, H - floor_y)
        stroke_and_fill(ctx, "#0B1220", None)
        ctx.move_to(0, floor_y); ctx.line_to(W, floor_y)
        stroke_and_fill(ctx, None, PALETTE["outline"], lw=3.0)

        # 4. Bàn làm việc gỗ sẫm
        desk_x, desk_y, desk_w, desk_h = 780, 680, 1020, 28
        rounded_rect(ctx, desk_x, desk_y, desk_w, desk_h, 6)
        stroke_and_fill(ctx, "#4A3525", PALETTE["outline"], lw=2.5)
        # Chân bàn kim loại
        for lx in (desk_x + 60, desk_x + desk_w - 80):
            rounded_rect(ctx, lx, desk_y + desk_h, 14, floor_y - (desk_y + desk_h), 2)
            stroke_and_fill(ctx, PALETTE["slate_dark"], PALETTE["outline"], lw=2.0)

        # 5. Laptop & Màn hình phát sáng nhẹ
        lap_x, lap_y = 1040, desk_y - 8
        rounded_rect(ctx, lap_x - 70, lap_y, 140, 8, 3)
        stroke_and_fill(ctx, PALETTE["slate_mid"], PALETTE["outline"], lw=2.0)
        # Màn hình mở nghiêng
        ctx.move_to(lap_x - 65, lap_y)
        ctx.line_to(lap_x - 55, lap_y - 85)
        ctx.line_to(lap_x + 55, lap_y - 85)
        ctx.line_to(lap_x + 65, lap_y)
        ctx.close_path()
        stroke_and_fill(ctx, "#0F172A", PALETTE["outline"], lw=2.0)
        # Vệt sáng cyan từ màn hình
        screen_glow = cairo.LinearGradient(lap_x, lap_y - 85, lap_x, lap_y)
        screen_glow.add_color_stop_rgba(0.0, 0.3, 0.78, 0.94, 0.45)
        screen_glow.add_color_stop_rgba(1.0, 0.3, 0.78, 0.94, 0.05)
        ctx.rectangle(lap_x - 50, lap_y - 80, 100, 75)
        ctx.set_source(screen_glow)
        ctx.fill()

        # 6. Đèn bàn ấm áp
        lamp_x, lamp_y = 1580, desk_y - 200
        # Nón đèn
        ctx.move_to(lamp_x, lamp_y)
        ctx.line_to(lamp_x - 45, lamp_y + 40)
        ctx.line_to(lamp_x + 45, lamp_y + 40)
        ctx.close_path()
        stroke_and_fill(ctx, PALETTE["hud_amber"], PALETTE["outline"], lw=2.4)
        # Thân đèn kim loại cong
        ctx.move_to(lamp_x, lamp_y)
        ctx.curve_to(lamp_x + 50, lamp_y + 80, lamp_x + 40, desk_y - 30, lamp_x + 20, desk_y)
        stroke_and_fill(ctx, None, PALETTE["slate_mid"], lw=4.5)
        # Luồng sáng vàng ấm rọi xuống mặt bàn
        cone = cairo.LinearGradient(lamp_x, lamp_y + 40, lamp_x - 40, desk_y + 10)
        cone.add_color_stop_rgba(0.0, 0.98, 0.76, 0.22, 0.38)
        cone.add_color_stop_rgba(1.0, 0.98, 0.76, 0.22, 0.0)
        ctx.move_to(lamp_x - 45, lamp_y + 40)
        ctx.line_to(lamp_x + 45, lamp_y + 40)
        ctx.line_to(lamp_x + 180, desk_y + desk_h)
        ctx.line_to(lamp_x - 240, desk_y + desk_h)
        ctx.close_path()
        ctx.set_source(cone)
        ctx.fill()

    @staticmethod
    def draw_cinematic_gradient(ctx, W, H, t, top_col="#081B29", bot_col="#133147"):
        """Nền Gradient điện ảnh sang trọng với hiệu ứng hạt sáng lơ lửng."""
        grad = cairo.LinearGradient(0, 0, 0, H)
        grad.add_color_stop_rgb(0.0, *hex_rgb(top_col))
        grad.add_color_stop_rgb(1.0, *hex_rgb(bot_col))
        ctx.rectangle(0, 0, W, H)
        ctx.set_source(grad)
        ctx.fill()

        # Hạt bụi ánh sáng lơ lửng tinh tế
        for i in range(25):
            px = ((i * 137.5 + t * 15.0) % W)
            py = ((i * 93.1 - t * 20.0) % H)
            op = 0.15 + 0.12 * math.sin(t * 1.5 + i)
            ctx.arc(px, py, 1.8 + (i % 3) * 0.8, 0, 2 * math.pi)
            ctx.set_source_rgba(0.95, 0.96, 1.0, op)
            ctx.fill()

    @staticmethod
    def draw_crossroad_horizon(ctx, W, H, t, cam_x=0.0):
        """Đường chân trời lúc bình minh/hoàng hôn tượng trưng cho bước ngoặt tuổi 32."""
        # Bầu trời hoàng hôn / rạng đông
        sky = cairo.LinearGradient(0, 0, 0, 620)
        sky.add_color_stop_rgb(0.0, *hex_rgb("#0F172A"))
        sky.add_color_stop_rgb(0.45, *hex_rgb("#312E81"))
        sky.add_color_stop_rgb(0.75, *hex_rgb("#9A3412"))
        sky.add_color_stop_rgb(1.0, *hex_rgb("#F59E0B"))
        ctx.rectangle(0, 0, W, 620)
        ctx.set_source(sky)
        ctx.fill()

        # Mặt trời rực rỡ nơi chân trời
        sun = cairo.RadialGradient(960, 600, 10, 960, 600, 220)
        sun.add_color_stop_rgba(0.0, 1.0, 0.95, 0.8, 0.85)
        sun.add_color_stop_rgba(0.4, 0.98, 0.65, 0.2, 0.45)
        sun.add_color_stop_rgba(1.0, 0.98, 0.65, 0.2, 0.0)
        ctx.arc(960, 600, 220, 0, 2 * math.pi)
        ctx.set_source(sun)
        ctx.fill()

        # Mặt đất & Con đường lớn hướng tới chân trời
        ground_y = 620
        ctx.rectangle(0, ground_y, W, H - ground_y)
        stroke_and_fill(ctx, "#111827", None)

        # Con đường phối cảnh thu nhỏ dần về tâm chân trời
        ctx.move_to(960, ground_y)
        ctx.line_to(960 - 20, ground_y)
        ctx.line_to(280, H)
        ctx.line_to(1640, H)
        ctx.line_to(960 + 20, ground_y)
        ctx.close_path()
        stroke_and_fill(ctx, "#1F2937", PALETTE["outline"], lw=2.0)

        # Vạch kẻ tim đường đứt quãng
        ctx.set_source_rgb(*hex_rgb(PALETTE["hud_amber"]))
        for i in range(8):
            p = (i + 1) / 9.0
            p_next = (i + 1.4) / 9.0
            y1 = ground_y + (H - ground_y) * (p ** 1.8)
            y2 = ground_y + (H - ground_y) * (p_next ** 1.8)
            lw = 2.0 + p * 12.0
            ctx.set_line_width(lw)
            ctx.move_to(960, y1); ctx.line_to(960, y2); ctx.stroke()


# ==============================================================================
# 6. BỘ HUD BLUEPRINT & INFOGRAPHIC ĐO LƯỜNG (HUD RENDERER)
# ==============================================================================
class HUDRenderer:
    """Các thành phần giao diện kỹ thuật, thước đo tỷ lệ và biểu đồ trực quan."""

    @staticmethod
    def spring_pop(t, trigger_t, duration=0.45):
        dt = t - trigger_t
        if dt <= 0:
            return 0.05
        if dt >= duration:
            return 1.0
        p = dt / duration
        return max(0.05, 1.0 - math.exp(-6.0 * p) * math.cos(12.0 * p))

    @staticmethod
    def draw_viewfinder_brackets(ctx, x, y, w, h, arm=36, color_hex="#F4F7F9"):
        ctx.save()
        ctx.set_source_rgba(*hex_rgb(color_hex), 0.85)
        ctx.set_line_width(3.0)
        corners = [
            (x, y + arm, x, y, x + arm, y),
            (x + w - arm, y, x + w, y, x + w, y + arm),
            (x, y + h - arm, x, y + h, x + arm, y + h),
            (x + w - arm, y + h, x + w, y + h, x + w, y + h - arm),
        ]
        for x1, y1, x2, y2, x3, y3 in corners:
            ctx.move_to(x1, y1)
            ctx.line_to(x2, y2)
            ctx.line_to(x3, y3)
        ctx.stroke()
        ctx.restore()

    @staticmethod
    def draw_target_reticle(ctx, x, y, t, radius=54, label="TARGET LOCKED"):
        ctx.save()
        ctx.translate(x, y)
        ctx.arc(0, 0, radius, 0, 2 * math.pi)
        stroke_and_fill(ctx, None, PALETTE["hud_amber"], lw=2.2, alpha=0.9)

        # Vòng cung quét xoay quanh tâm
        ctx.rotate(t * 1.8)
        ctx.arc(0, 0, radius + 10, 0, math.pi * 0.65)
        stroke_and_fill(ctx, None, PALETTE["hud_amber"], lw=4.0)
        ctx.restore()

        if label:
            ctx.select_font_face("Monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            ctx.set_font_size(18)
            ctx.set_source_rgb(*hex_rgb(PALETTE["hud_amber"]))
            ctx.move_to(x + radius + 18, y + 6)
            ctx.show_text(label)

    @staticmethod
    def draw_scale_wireframe(ctx, x, y, width_px=320, label_text="~4.2 M LONG | UP TO 680 KG"):
        """Vẽ khung xe hơi Wireframe màu vàng hổ phách và thanh kích thước để so sánh tỷ lệ."""
        ctx.save()
        ctx.translate(x, y)
        scale_f = width_px / 240.0
        safe_scale(ctx, scale_f, scale_f)

        # Khung thân xe hơi Sedan chuẩn
        ctx.move_to(-110, 20)
        ctx.line_to(-105, -8)
        ctx.line_to(-65, -14)
        ctx.line_to(-32, -38)
        ctx.line_to(45, -38)
        ctx.line_to(82, -12)
        ctx.line_to(110, -4)
        ctx.line_to(110, 20)
        ctx.close_path()
        stroke_and_fill(ctx, None, PALETTE["hud_amber"], lw=2.0, alpha=0.85)

        # 2 bánh xe wireframe
        for wx in (-65, 68):
            ctx.new_sub_path()
            ctx.arc(wx, 20, 18, 0, 2 * math.pi)
            stroke_and_fill(ctx, None, PALETTE["hud_amber"], lw=2.2, alpha=0.9)
        ctx.restore()

        # Thanh đo kích thước bên dưới
        bar_y = y + 48
        ctx.move_to(x - width_px / 2, bar_y)
        ctx.line_to(x + width_px / 2, bar_y)
        for bx in (x - width_px / 2, x + width_px / 2):
            ctx.move_to(bx, bar_y - 8)
            ctx.line_to(bx, bar_y + 8)
        stroke_and_fill(ctx, None, PALETTE["hud_amber"], lw=2.4)

        ctx.select_font_face("Monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(20)
        ctx.set_source_rgb(*hex_rgb(PALETTE["hud_amber"]))
        ctx.move_to(x - width_px * 0.42, bar_y + 28)
        ctx.show_text(label_text)

    @staticmethod
    def draw_donut_gauge(ctx, x, y, radius=68, pct=0.75, label="EFFICIENCY", color_hex="#F5C242"):
        ctx.save()
        ctx.translate(x, y)
        ctx.arc(0, 0, radius, 0, 2 * math.pi)
        stroke_and_fill(ctx, None, PALETTE["grid_line"], lw=14.0)

        end_angle = -math.pi / 2 + max(0.01, min(1.0, pct)) * 2 * math.pi
        ctx.arc(0, 0, radius, -math.pi / 2, end_angle)
        stroke_and_fill(ctx, None, color_hex, lw=14.0)

        ctx.select_font_face("Monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(26)
        ctx.set_source_rgb(*hex_rgb(PALETTE["hud_white"]))
        ctx.move_to(-28, 9)
        ctx.show_text(f"{int(pct * 100)}%")

        ctx.set_font_size(18)
        ctx.set_source_rgb(*hex_rgb(color_hex))
        ctx.move_to(-radius, radius + 34)
        ctx.show_text(label)
        ctx.restore()

    @staticmethod
    def draw_callout_pin(ctx, target_x, target_y, box_x, box_y, title, subtitle):
        # Chấm tròn tại vị trí giải phẫu
        ctx.arc(target_x, target_y, 6, 0, 2 * math.pi)
        stroke_and_fill(ctx, PALETTE["hud_amber"], PALETTE["outline"], lw=2.0)

        # Đường gấp khúc dẫn tới hộp thông tin
        elbow_x = (target_x + box_x) * 0.5
        ctx.move_to(target_x, target_y)
        ctx.line_to(elbow_x, box_y)
        ctx.line_to(box_x, box_y)
        stroke_and_fill(ctx, None, PALETTE["hud_amber"], lw=2.4)

        # Hộp chữ
        rounded_rect(ctx, box_x, box_y - 34, 290, 68, 8)
        stroke_and_fill(ctx, PALETTE["bg_navy"], PALETTE["hud_amber"], lw=2.2, alpha=0.92)

        ctx.select_font_face("Monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(20)
        ctx.set_source_rgb(*hex_rgb(PALETTE["hud_amber"]))
        ctx.move_to(box_x + 14, box_y - 8)
        ctx.show_text(title)

        ctx.set_font_size(16)
        ctx.set_source_rgb(*hex_rgb(PALETTE["hud_white"]))
        ctx.move_to(box_x + 14, box_y + 18)
        ctx.show_text(subtitle)

    @staticmethod
    def draw_rubber_stamp(ctx, x, y, text, t, trigger_t, angle_deg=-12.0):
        if t < trigger_t:
            return
        pop = HUDRenderer.spring_pop(t, trigger_t)
        ctx.save()
        ctx.translate(x, y)
        ctx.rotate(math.radians(angle_deg))
        safe_scale(ctx, pop, pop)

        w, h = max(260, len(text) * 24 + 48), 74
        rounded_rect(ctx, -w / 2, -h / 2, w, h, 10)
        stroke_and_fill(ctx, PALETTE["bg_navy"], PALETTE["alert_coral"], lw=5.0, alpha=0.94)

        ctx.select_font_face("Segoe UI", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(32)
        ctx.set_source_rgb(*hex_rgb(PALETTE["alert_coral"]))
        ctx.move_to(-w / 2 + 24, 11)
        ctx.show_text(text)
        ctx.restore()

    @staticmethod
    def draw_subtitle_box(ctx, W, H, text, font="Segoe UI", font_size=28, text_color="#F4F7F9", bg_alpha=0.82):
        """Hộp phụ đề nổi bật chuẩn điện ảnh, tự động xuống dòng và căn giữa cạnh dưới màn hình."""
        if not text:
            return
        ctx.save()
        ctx.select_font_face(font, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(font_size)

        max_text_w = W - 180
        words = text.split()
        lines = []
        cur_line = []

        for word in words:
            test_line = " ".join(cur_line + [word])
            ext = ctx.text_extents(test_line)
            if ext[2] > max_text_w and cur_line:
                lines.append(" ".join(cur_line))
                cur_line = [word]
            else:
                cur_line.append(word)
        if cur_line:
            lines.append(" ".join(cur_line))

        line_h = font_size * 1.35
        line_extents = [ctx.text_extents(ln) for ln in lines]
        max_line_w = max((ext[2] for ext in line_extents), default=0)
        total_text_h = len(lines) * line_h

        pad_x, pad_y = 36, 16
        box_w = max_line_w + pad_x * 2
        box_h = total_text_h + pad_y * 2
        box_x = (W - box_w) / 2
        box_y = H - 110 - box_h

        rounded_rect(ctx, box_x, box_y, box_w, box_h, 12)
        ctx.set_source_rgba(0.04, 0.08, 0.12, bg_alpha)
        ctx.fill_preserve()
        ctx.set_source_rgba(0.96, 0.76, 0.26, 0.5)
        ctx.set_line_width(2.0)
        ctx.stroke()

        ctx.set_source_rgb(*hex_rgb(text_color))
        cur_y = box_y + pad_y + font_size
        for ln, ext in zip(lines, line_extents):
            ln_x = box_x + (box_w - ext[2]) / 2
            ctx.move_to(ln_x, cur_y)
            ctx.show_text(ln)
            cur_y += line_h

        ctx.restore()

    @staticmethod
    def draw_lower_third(ctx, title, subtitle, t, trigger_t=0.5, font="Segoe UI", x=140, y=860):
        """Bảng tên / chức danh / tiêu đề phong cách truyền hình sang trọng."""
        if t < trigger_t:
            return
        pop = HUDRenderer.spring_pop(t, trigger_t, duration=0.5)
        ctx.save()
        ctx.translate(x, y)
        safe_scale(ctx, pop, 1.0)

        w = max(420, len(title) * 20 + 60)
        rounded_rect(ctx, 0, 0, w, 82, 8)
        stroke_and_fill(ctx, PALETTE["bg_navy"], None, alpha=0.92)

        rounded_rect(ctx, 0, 0, 8, 82, 4)
        stroke_and_fill(ctx, PALETTE["hud_amber"], None)

        ctx.select_font_face(font, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(26)
        ctx.set_source_rgb(*hex_rgb(PALETTE["hud_white"]))
        ctx.move_to(28, 38)
        ctx.show_text(title)

        if subtitle:
            ctx.set_font_size(18)
            ctx.set_source_rgb(*hex_rgb(PALETTE["hud_amber"]))
            ctx.move_to(28, 66)
            ctx.show_text(subtitle)
        ctx.restore()

    @staticmethod
    def draw_milestone_badge(ctx, x, y, number_str="32", label="TUỔI 32", t=0.0, trigger_t=0.0, font="Segoe UI"):
        """Huy hiệu cột mốc số ấn tượng (ví dụ: TUỔI 32 / 32 NĂM)."""
        if t < trigger_t:
            return
        pop = HUDRenderer.spring_pop(t, trigger_t, duration=0.6)
        ctx.save()
        ctx.translate(x, y)
        safe_scale(ctx, pop, pop)

        ctx.arc(0, 0, 78, 0, 2 * math.pi)
        stroke_and_fill(ctx, None, PALETTE["hud_amber"], lw=2.4, alpha=0.6)
        ctx.arc(0, 0, 68, 0, 2 * math.pi)
        stroke_and_fill(ctx, PALETTE["bg_navy"], PALETTE["hud_white"], lw=3.0, alpha=0.95)

        ctx.select_font_face(font, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(52)
        ctx.set_source_rgb(*hex_rgb(PALETTE["hud_amber"]))
        cw = len(str(number_str)) * 26
        ctx.move_to(-cw / 2, 18)
        ctx.show_text(str(number_str))

        if label:
            ctx.set_font_size(16)
            ctx.set_source_rgb(*hex_rgb(PALETTE["hud_white"]))
            lw = len(label) * 8.5
            ctx.move_to(-lw / 2, 50)
            ctx.show_text(label)
        ctx.restore()


# ==============================================================================
# 7. BỘ CHẠY KỊCH BẢN JSON TỰ ĐỘNG (SCENE TIMELINE RUNNER)
# ==============================================================================
class SceneRunner:
    """
    Nhận cấu trúc JSON do AI phân tích từ cốt truyện và kết xuất frame (1920x1080).
    AI không cần viết code chuyển động, chỉ cần truyền tên rig và motion_preset.
    """
    RIG_FACTORIES = {
        "human_diver": lambda: RigBuilder.build_human_rig("diver"),
        "human_explorer": lambda: RigBuilder.build_human_rig("explorer"),
        "human_swimmer": lambda: RigBuilder.build_human_rig("swimmer"),
        "human_civilian": lambda: RigBuilder.build_human_rig("civilian"),
        "human_casual": lambda: RigBuilder.build_human_rig("casual"),
        "human_formal": lambda: RigBuilder.build_human_rig("formal"),
        "human_suit": lambda: RigBuilder.build_human_rig("suit"),
        "human_officer": lambda: RigBuilder.build_human_rig("officer"),
        "human_machinist": lambda: RigBuilder.build_human_rig("machinist"),
        "shark": lambda: RigBuilder.build_shark_rig("shark"),
        "orca": lambda: RigBuilder.build_shark_rig("orca"),
        "whale": RigBuilder.build_whale_rig,
        "bird": RigBuilder.build_bird_rig,
        "wolf": lambda: RigBuilder.build_quadruped_rig("wolf"),
        "bear": lambda: RigBuilder.build_quadruped_rig("bear"),
        "submersible": lambda: RigBuilder.build_vessel_rig("submersible"),
        "research_boat": lambda: RigBuilder.build_vessel_rig("research_boat"),
    }

    @classmethod
    def register_rig(cls, name, factory_fn):
        """Đăng ký thêm Rig tùy biến từ bên ngoài."""
        cls.RIG_FACTORIES[name] = factory_fn

    def __init__(self, scene_config, width=W_DEFAULT, height=H_DEFAULT):
        self.cfg = scene_config
        self.W = width
        self.H = height
        self.actor_instances = {}
        for act in self.cfg.get("actors", []):
            rtype = act.get("rig_type", "human_casual")
            factory = self.RIG_FACTORIES.get(rtype, self.RIG_FACTORIES.get("human_casual", lambda: RigBuilder.build_human_rig("casual")))
            self.actor_instances[act["id"]] = factory()

    def render_frame(self, ctx, t):
        env = self.cfg.get("environment", {})
        env_preset = env.get("preset", "modern_workspace")
        cam_x = env.get("camera_pan_speed_x", 0.0) * t

        # 1. Vẽ môi trường nền
        if env_preset == "underwater_cross_section":
            EnvironmentRenderer.draw_underwater_cross_section(
                ctx, self.W, self.H, t,
                surf_y=env.get("water_level_y", 210),
                cam_x=cam_x,
                deep_mode=env.get("deep_mode", False)
            )
        elif env_preset == "mountain_forest":
            EnvironmentRenderer.draw_mountain_forest_parallax(ctx, self.W, self.H, t, cam_x=cam_x)
        elif env_preset == "blueprint_grid":
            EnvironmentRenderer.draw_blueprint_grid(ctx, self.W, self.H, cam_x=cam_x)
        elif env_preset == "journal_card":
            EnvironmentRenderer.draw_historical_journal_card(
                ctx, self.W, self.H,
                title_text=env.get("title", "EXPEDITION LOG"),
                body_lines=env.get("lines", []),
                underline_progress=min(1.0, t / max(0.5, self.cfg.get("duration_sec", 4.0) * 0.7))
            )
        elif env_preset == "modern_workspace":
            EnvironmentRenderer.draw_modern_workspace(ctx, self.W, self.H, t, cam_x=cam_x)
        elif env_preset == "cinematic_gradient":
            EnvironmentRenderer.draw_cinematic_gradient(
                ctx, self.W, self.H, t,
                top_col=env.get("top_color", "#081B29"),
                bot_col=env.get("bot_color", "#133147")
            )
        elif env_preset == "crossroad_horizon":
            EnvironmentRenderer.draw_crossroad_horizon(ctx, self.W, self.H, t, cam_x=cam_x)

        # 2. Cập nhật Procedural Motion & Vẽ từng Actor
        actor_positions = {}
        for act in self.cfg.get("actors", []):
            aid = act["id"]
            if aid not in self.actor_instances:
                continue
            rig = self.actor_instances[aid]
            sx, sy = act.get("start_pos", [960, 540])
            vx, vy = act.get("velocity", [0.0, 0.0])
            cur_x, cur_y = sx + vx * t, sy + vy * t
            actor_positions[aid] = (cur_x, cur_y)

            ProceduralMotion.apply_preset(
                rig,
                act.get("motion_preset", "idle"),
                t,
                **act.get("motion_params", {})
            )
            rig.set_transform(
                cur_x, cur_y,
                scale=act.get("scale", 1.0),
                angle_deg=act.get("angle_deg", 0.0),
                flip_x=act.get("flip_x", False)
            )
            rig.render(ctx)

        # 3. Vẽ các lớp phủ HUD & Infographic
        for hud in self.cfg.get("hud_overlays", []):
            trig = hud.get("trigger_time", 0.0)
            if t < trig:
                continue
            htype = hud.get("type")
            tx, ty = actor_positions.get(hud.get("target_actor"), hud.get("pos", [960, 540]))

            if htype == "scale_wireframe":
                HUDRenderer.draw_scale_wireframe(
                    ctx, tx, ty + hud.get("offset_y", 130),
                    width_px=hud.get("width_px", 320),
                    label_text=hud.get("label", "~4.2 M LONG")
                )
            elif htype == "target_reticle":
                HUDRenderer.draw_target_reticle(ctx, tx, ty, t, label=hud.get("label", "LOCKED"))
            elif htype == "callout_pin":
                HUDRenderer.draw_callout_pin(
                    ctx, tx, ty,
                    tx + hud.get("box_offset_x", 120),
                    ty + hud.get("box_offset_y", -110),
                    hud.get("title", "ANATOMY"),
                    hud.get("subtitle", "DETAIL")
                )
            elif htype == "donut_gauge":
                gx, gy = hud.get("pos", [220, 220])
                HUDRenderer.draw_donut_gauge(ctx, gx, gy, pct=hud.get("pct", 0.8), label=hud.get("label", "STAT"))
            elif htype == "rubber_stamp":
                sx, sy = hud.get("pos", [960, 540])
                HUDRenderer.draw_rubber_stamp(ctx, sx, sy, hud.get("label", "VERIFIED"), t, trig)
            elif htype == "lower_third":
                lx, ly = hud.get("pos", [140, 860])
                HUDRenderer.draw_lower_third(
                    ctx, hud.get("title", ""), hud.get("subtitle", ""),
                    t, trigger_t=trig, x=lx, y=ly
                )
            elif htype == "milestone_badge":
                bx, by = hud.get("pos", [960, 480])
                HUDRenderer.draw_milestone_badge(
                    ctx, bx, by,
                    number_str=hud.get("number", "32"),
                    label=hud.get("label", "TUỔI 32"),
                    t=t, trigger_t=trig
                )

        # 4. Vẽ Subtitles nếu có
        for sub in self.cfg.get("subtitles", []):
            st = sub.get("start_time", 0.0)
            et = sub.get("end_time", self.cfg.get("duration_sec", 999.0))
            if st <= t <= et:
                HUDRenderer.draw_subtitle_box(
                    ctx, self.W, self.H, sub.get("text", ""),
                    font=sub.get("font", "Segoe UI"),
                    font_size=sub.get("font_size", 28)
                )


# ==============================================================================
# 8. BỘ KẾ HOẠCH ĐA PHÂN CẢNH & XUẤT VIDEO (STORYBOARD TIMELINE & VIDEO PIPELINE)
# ==============================================================================
class StoryboardRunner:
    """
    Trình phát và quản lý video toàn diện qua Storyboard (nhiều Scene liên tiếp).
    Tự động chia thời lượng, chuyển cảnh (fades), camera và đồng bộ phụ đề.
    """
    def __init__(self, storyboard_or_file, width=W_DEFAULT, height=H_DEFAULT, lang="vi"):
        if isinstance(storyboard_or_file, str):
            with open(storyboard_or_file, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        elif isinstance(storyboard_or_file, dict):
            self.data = storyboard_or_file
        else:
            raise ValueError("Storyboard must be a file path or dict.")

        self.W = self.data.get("width", width)
        self.H = self.data.get("height", height)
        self.fps = self.data.get("fps", FPS_DEFAULT)
        self.lang = lang or self.data.get("lang", "vi")
        self.title = self.data.get("title", "Cinematic Video")

        raw_scenes = self.data.get("scenes", [])
        if not raw_scenes and "actors" in self.data:
            raw_scenes = [self.data]

        self.scenes = []
        cur_time = 0.0
        for sc in raw_scenes:
            sc_copy = dict(sc)
            sc_dur = float(sc_copy.get("duration_sec", 5.0))
            st_time = float(sc_copy.get("start_time", cur_time))
            sc_copy["start_time"] = st_time
            sc_copy["duration_sec"] = sc_dur
            sc_copy["end_time"] = st_time + sc_dur
            sc_copy["runner"] = SceneRunner(sc_copy, self.W, self.H)
            self.scenes.append(sc_copy)
            cur_time = sc_copy["end_time"]

        self.total_duration = float(self.data.get("duration_sec", cur_time))
        if cur_time > self.total_duration:
            self.total_duration = cur_time

    def scale_to_duration(self, target_duration):
        """Tự động co giãn thời lượng các Scene theo độ dài giọng đọc (voiceover)."""
        if self.total_duration <= 0 or target_duration <= 0:
            return
        ratio = target_duration / self.total_duration
        cur = 0.0
        for sc in self.scenes:
            sc["start_time"] = cur
            sc["duration_sec"] = sc["duration_sec"] * ratio
            sc["end_time"] = cur + sc["duration_sec"]
            # Co giãn subtitles trong scene nếu có
            for sub in sc.get("subtitles", []):
                sub["start_time"] = sub.get("start_time", 0.0) * ratio
                sub["end_time"] = sub.get("end_time", sc["duration_sec"]) * ratio
            cur = sc["end_time"]
        self.total_duration = target_duration

    def get_active_scene(self, t):
        if not self.scenes:
            return None, 0.0
        t_clamped = max(0.0, min(t, self.total_duration - 0.0001))
        for sc in self.scenes:
            if sc["start_time"] <= t_clamped < sc["end_time"]:
                return sc, t_clamped - sc["start_time"]
        last = self.scenes[-1]
        return last, t_clamped - last["start_time"]

    def render_frame(self, ctx, t):
        scene, local_t = self.get_active_scene(t)
        if not scene:
            ctx.set_source_rgb(0, 0, 0)
            ctx.paint()
            return

        runner = scene["runner"]
        runner.render_frame(ctx, local_t)

        # Chuyển cảnh làm tối / mờ dần (Fade In / Fade Out)
        dur = scene["duration_sec"]
        fade_in = scene.get("fade_in_sec", 0.35 if scene.get("fade_in", False) else 0.0)
        fade_out = scene.get("fade_out_sec", 0.35 if scene.get("fade_out", False) else 0.0)

        if fade_in > 0 and local_t < fade_in:
            alpha = 1.0 - (local_t / fade_in)
            ctx.set_source_rgba(0, 0, 0, alpha)
            ctx.paint()
        elif fade_out > 0 and local_t > (dur - fade_out):
            alpha = (local_t - (dur - fade_out)) / fade_out
            ctx.set_source_rgba(0, 0, 0, alpha)
            ctx.paint()


def setup_ffmpeg_environment():
    """Bổ sung FFmpeg và Python vào PATH môi trường Windows."""
    extra_paths = [
        r"C:\Users\Admin\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.2-full_build\bin",
        r"C:\Users\Admin\AppData\Local\Programs\Python\Python312",
        r"C:\Users\Admin\AppData\Local\Programs\Python\Python312\Scripts",
    ]
    cur = os.environ.get("PATH", "")
    for p in extra_paths:
        if os.path.exists(p) and p.lower() not in cur.lower():
            os.environ["PATH"] = p + ";" + os.environ.get("PATH", "")
            cur = os.environ["PATH"]


def render_storyboard_video(storyboard_or_file, voiceover_file=None, sfx_file=None, output_mp4=None, duration=None, fps=FPS_DEFAULT, lang="vi"):
    """
    Kết xuất video hoàn chỉnh chuẩn Full HD 1080p từ Storyboard JSON.
    Tự động đồng bộ giọng đọc, hòa âm SFX và xuất ra file MP4 chất lượng cao.
    """
    setup_ffmpeg_environment()

    runner = StoryboardRunner(storyboard_or_file, lang=lang)
    if duration is not None and duration > 0:
        runner.scale_to_duration(duration)
    else:
        duration = runner.total_duration

    if output_mp4 is None:
        output_mp4 = os.path.join(CURRENT_DIR, "..", "output", "storyboard_cinematic.mp4")
    output_mp4 = os.path.abspath(output_mp4)
    os.makedirs(os.path.dirname(output_mp4), exist_ok=True)

    total_frames = int(duration * fps)
    W, H = runner.W, runner.H

    # Xây dựng lệnh FFmpeg tùy thuộc vào các nguồn âm thanh có sẵn
    ffmpeg_bin = shutil.which("ffmpeg") or "ffmpeg"
    ffmpeg_cmd = [
        ffmpeg_bin, "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{W}x{H}",
        "-pix_fmt", "bgr24",
        "-r", str(fps),
        "-i", "-", # Stdin stream
    ]

    has_voice = voiceover_file and os.path.exists(voiceover_file)
    has_sfx = sfx_file and os.path.exists(sfx_file)

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
        ffmpeg_cmd += ["-map", "0:v"]

    ffmpeg_cmd += [
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "fast",
        "-crf", "18",
        "-shortest",
        output_mp4
    ]

    print(f"\n[Storyboard Engine] Bắt đầu render video: {output_mp4}")
    print(f"[Storyboard Engine] Kích thước: {W}x{H} | Độ dài: {duration:.2f}s | Tổng frame: {total_frames} @ {fps} FPS")
    proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)

    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)

    for f in range(total_frames):
        t = f / float(fps)
        runner.render_frame(ctx, t)
        buf = np.frombuffer(surf.get_data(), dtype=np.uint8).reshape((H, W, 4))
        bgr = buf[:, :, :3]
        proc.stdin.write(bgr.tobytes())

        if f % 180 == 0 or f == total_frames - 1:
            pct = (f + 1) / total_frames * 100.0
            print(f"[Storyboard Engine] Đang render: frame {f+1}/{total_frames} ({pct:.1f}%)")

    proc.stdin.close()
    proc.wait()
    print(f"[Storyboard Engine] Hoàn tất render video: {output_mp4}")
    return output_mp4


def generate_storyboard_previews(storyboard_or_file, output_dir=None, fps=FPS_DEFAULT, lang="vi"):
    """Xuất hình ảnh xem trước (Preview Plates) cho từng Scene trong Storyboard."""
    runner = StoryboardRunner(storyboard_or_file, lang=lang)
    if output_dir is None:
        output_dir = os.path.join(CURRENT_DIR, "..", "output")
    os.makedirs(output_dir, exist_ok=True)

    W, H = runner.W, runner.H
    preview_paths = []

    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)

    for i, sc in enumerate(runner.scenes):
        st = sc["start_time"]
        dur = sc["duration_sec"]
        shot_t = st + min(1.8, dur * 0.5)
        runner.render_frame(ctx, shot_t)

        sc_id = sc.get("id", f"scene_{i+1:02d}")
        out_png = os.path.join(output_dir, f"preview_{sc_id}.png")
        surf.write_to_png(out_png)
        preview_paths.append(out_png)
        print(f"[Storyboard Preview] Đã tạo ảnh mẫu: {out_png}")

    return preview_paths


# ==============================================================================
# 8. DEMO KIỂM THỬ NHANH (CHẠY TRỰC TIẾP FILE ĐỂ XUẤT ẢNH MẪU)
# ==============================================================================
if __name__ == "__main__":
    sample_scene = {
        "duration_sec": 5.0,
        "environment": {
            "preset": "underwater_cross_section",
            "water_level_y": 210,
            "camera_pan_speed_x": 30.0,
            "deep_mode": False
        },
        "actors": [
            {
                "id": "boat_01",
                "rig_type": "research_boat",
                "start_pos": [380, 205],
                "velocity": [12.0, 0.0],
                "scale": 1.1,
                "motion_preset": "vessel_cruise"
            },
            {
                "id": "diver_01",
                "rig_type": "human_diver",
                "start_pos": [520, 520],
                "velocity": [25.0, 0.0],
                "scale": 1.0,
                "motion_preset": "swim_horizontal",
                "motion_params": {"freq": 3.2, "kick_deg": 28.0}
            },
            {
                "id": "shark_01",
                "rig_type": "shark",
                "start_pos": [1380, 620],
                "velocity": [-65.0, 0.0],
                "scale": 1.35,
                "flip_x": True,
                "motion_preset": "spine_undulation",
                "motion_params": {"freq": 3.8, "amp_deg": 15.0, "jaw_open": 0.3}
            }
        ],
        "hud_overlays": [
            {
                "type": "scale_wireframe",
                "target_actor": "shark_01",
                "trigger_time": 0.5,
                "offset_y": 145,
                "width_px": 340,
                "label": "~4.5 M LONG | APEX PREDATOR"
            },
            {
                "type": "callout_pin",
                "target_actor": "shark_01",
                "trigger_time": 1.0,
                "box_offset_x": 90,
                "box_offset_y": -140,
                "title": "SERRATED JAW",
                "subtitle": "BITE FORCE: 18,000 NEWTONS"
            },
            {
                "type": "rubber_stamp",
                "trigger_time": 1.2,
                "pos": [1580, 160],
                "label": "ZERO FATALITIES"
            }
        ]
    }

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, W_DEFAULT, H_DEFAULT)
    ctx = cairo.Context(surface)
    runner = SceneRunner(sample_scene)
    runner.render_frame(ctx, t=2.0)
    surface.write_to_png("sample_keyframe_preview.png")
    print("Đã xuất file mẫu thành công: sample_keyframe_preview.png")