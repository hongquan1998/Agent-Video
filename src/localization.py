# -*- coding: utf-8 -*-
"""
Comprehensive Localization Module for 2D Cinematic Documentary Production.
Dynamically adapts all on-screen titles, HUD telemetry, technical cards, gauge labels,
and narrative captions to match the exact language of the voiceover audio track.
"""

LANGUAGE_FONTS = {
    "vi": "Segoe UI",
    "en": "Segoe UI",
    "fr": "Segoe UI",
    "de": "Segoe UI",
    "es": "Segoe UI",
    "ru": "Segoe UI",
    "ja": "Yu Gothic",
    "zh": "Microsoft YaHei",
    "ko": "Malgun Gothic",
    "default": "Segoe UI"
}

SCENE_LOCALIZATIONS = {
    "vi": {
        "s1_date": "23 THÁNG 5 NĂM 1939  •  08:00 SÁNG",
        "s1_loc": "NGOÀI KHƠI BỜ BIỂN NEW HAMPSHIRE  |  BẮC ĐẠI TÂY DƯƠNG (2°C)",
        "s2_title": "USS SQUALUS (SS-192)",
        "s2_sub": "TÀU NGẦM TỐI TÂN BẬC NHẤT HẢI QUÂN HOA KỲ  •  DÀI 94 MÉT  •  LƯỢNG CHOÁN NƯỚC: 2.350 TẤN",
        "s3_gauge_1": "ÁP SUẤT",
        "s3_gauge_2": "ĐỘ SÂU",
        "s3_gauge_3": "ĐIỆN ÁP",
        "s3_title": "59 THỦY THỦ ĐOÀN VÀ KỸ SƯ DÂN SỰ TRÊN TÀU",
        "s3_sub": "ĐẠI ÚY OLIVER NAQUIN CHỈ HUY  •  BÀI KIỂM TRA LẶN TỐC ĐỘ CAO LẦN THỨ 19",
        "s4_telegraph_stop": "DỪNG",
        "s4_telegraph_ahead": "TIẾN",
        "s4_telegraph_back": "LÙI",
        "s4_telegraph_dive": "LẶN",
        "s4_caption": "08:40 SÁNG — CÒI BÁO LẶN VANG LÊN",
        "s5_title": "BẢNG TÍN HIỆU CỬA THÔNG KHÍ (CÂY THÔNG NOEL)",
        "s5_valve_1": "HÚT CHÍNH",
        "s5_valve_2": "THÔNG GIÓ",
        "s5_valve_3": "VAN XẢ ĐÁY",
        "s5_valve_4": "LỌC KHÍ",
        "s5_valve_5": "VAN THÂN",
        "s5_confirm": "XÁC NHẬN: MỌI VAN KHÍ ĐÃ KHÓA CHẶT (HÀNG ĐÈN XANH)",
        "s6_depth_unit": "ĐỘ SÂU (M)",
        "s6_caption": "LƯỚT ÊM XUỐNG ĐỘ SÂU 15 MÉT — CHÍNH XÁC NHƯ MỘT CỖ MÁY ĐỒNG HỒ",
        "s7_warning": "NHƯNG BẢNG ĐÈN XANH ẤY ĐÃ NÓI DỐI.",
        "s8_catastrophe": "SỰ CỐ CƠ KHÍ CHÍ MẠNG: VAN NẠP KHÍ CHÍNH RỘNG GẦN 80 CM BẬT MỞ DƯỚI ÁP LỰC BIỂN",
        "s10_shout": '"GIỮ ĐỘ SÂU! KHOANG ĐỘNG CƠ ĐANG NGẬP NƯỚC!"',
        "s11_abyss": "HÀNG TRĂM TẤN NƯỚC BIỂN KÉO SẬP ĐUÔI TÀU XUỐNG VỰC THẲM",
        "s12_tilt": "GÓC NGHIÊNG: -45° MŨI TÀU DỰNG NGƯỢC",
        "s13_door": "VÀ GIỮA HAI NỬA CON TÀU, CHỈ CÒN DUY NHẤT MỘT CÁNH CỬA THÉP VẪN ĐANG MỞ TOANG..."
    },
    "en": {
        "s1_date": "MAY 23, 1939  •  08:00 AM",
        "s1_loc": "OFF THE COAST OF NEW HAMPSHIRE  |  NORTH ATLANTIC (2°C)",
        "s2_title": "USS SQUALUS (SS-192)",
        "s2_sub": "STATE-OF-THE-ART U.S. NAVY FLEET SUBMARINE  •  LENGTH: 94 METERS  •  DISPLACEMENT: 2,350 TONS",
        "s3_gauge_1": "PRESSURE",
        "s3_gauge_2": "DEPTH",
        "s3_gauge_3": "VOLTAGE",
        "s3_title": "59 CREWMEN AND CIVILIAN CONTRACTORS ABOARD",
        "s3_sub": "LIEUTENANT OLIVER NAQUIN COMMANDING  •  19TH HIGH-SPEED TRIAL DIVE",
        "s4_telegraph_stop": "STOP",
        "s4_telegraph_ahead": "AHEAD",
        "s4_telegraph_back": "BACK",
        "s4_telegraph_dive": "DIVE",
        "s4_caption": "08:40 AM — THE DIVE KLAXON SOUNDS",
        "s5_title": "MAIN INDUCTION INDICATOR (THE CHRISTMAS TREE)",
        "s5_valve_1": "MAIN IND.",
        "s5_valve_2": "VENTILATION",
        "s5_valve_3": "KINGSTON",
        "s5_valve_4": "PURIFIER",
        "s5_valve_5": "HULL VALVE",
        "s5_confirm": "VERIFIED: ALL HULL OPENINGS SEALED (BOARD IS GREEN)",
        "s6_depth_unit": "DEPTH (M)",
        "s6_caption": "GLIDING SMOOTHLY TO 15 METERS — RUNNING LIKE CLOCKWORK",
        "s7_warning": "BUT THE GREEN LIGHTS WERE LYING.",
        "s8_catastrophe": "FATAL MECHANICAL FAILURE: 80 CM MAIN INDUCTION VALVE BLOWN OPEN BY SEA PRESSURE",
        "s10_shout": '"TAKE HER UP! ENGINE ROOMS ARE FLOODING!"',
        "s11_abyss": "HUNDREDS OF TONS OF SEAWATER DRAG THE STERN INTO THE ABYSS",
        "s12_tilt": "PITCH ANGLE: -45° BOW REARING SKYWARD",
        "s13_door": "AND BETWEEN THE TWO HALVES OF THE SHIP, ONLY ONE STEEL DOOR REMAINS OPEN..."
    }
}

def get_font_for_lang(lang_code="vi"):
    lang = (lang_code or "vi").lower().split("-")[0].split("_")[0]
    return LANGUAGE_FONTS.get(lang, LANGUAGE_FONTS["default"])

def T(key, lang_code="vi"):
    """Fetch localized string by key for the given language code with fallback."""
    lang = (lang_code or "vi").lower().split("-")[0].split("_")[0]
    pack = SCENE_LOCALIZATIONS.get(lang)
    if not pack:
        pack = SCENE_LOCALIZATIONS.get("en", SCENE_LOCALIZATIONS.get("vi", {}))
    return pack.get(key, SCENE_LOCALIZATIONS.get("en", {}).get(key, ""))

def register_custom_language(lang_code, translations):
    """Dynamically register or expand a language translation pack."""
    lang = lang_code.lower().split("-")[0].split("_")[0]
    if lang not in SCENE_LOCALIZATIONS:
        SCENE_LOCALIZATIONS[lang] = {}
    SCENE_LOCALIZATIONS[lang].update(translations)
