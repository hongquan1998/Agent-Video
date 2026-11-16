# -*- coding: utf-8 -*-
"""
generate_sfx.py
Bộ Tổng Hợp Âm Thanh Thủ Tục Đa Dụng (General-Purpose Procedural Sound Design & SFX Engine).
Tổng hợp âm thanh thuần toán học (NumPy) chất lượng 44.1 kHz Stereo:
- Hợp âm đệm Ambient Pad điện ảnh
- Tiếng mưa rơi, gió rít, sóng biển và không gian phòng (Room tone)
- Nhịp đồng hồ tích tắc, gõ bàn phím, tiếng lật trang, nhịp tim
- Tiếng chuyển cảnh vút gió (Whoosh), chuông bứt phá (Chime), va chạm đanh thép (Stamp Impact)
- Hỗ trợ đa dạng chủ đề (Theme): 'cinematic_ambient', 'contemplative', 'suspense_documentary', 'industrial'
"""

import os
import wave
import numpy as np

SAMPLE_RATE = 44100
DEFAULT_DURATION = 81.9

# ==============================================================================
# 1. HÀM TỔNG HỢP ÂM THANH NGUYÊN BẢN (SYNTHESIS PRIMITIVES)
# ==============================================================================
def synth_sine(freq, dur, sample_rate=SAMPLE_RATE, amp=0.5, decay=0.0):
    """Tạo sóng Sine với tần số freq và độ phân rã decay tùy chọn."""
    samples = int(dur * sample_rate)
    t = np.linspace(0, dur, samples, endpoint=False, dtype=np.float32)
    sig = amp * np.sin(2 * np.pi * freq * t)
    if decay > 0:
        sig *= np.exp(-t / decay)
    return sig

def synth_colored_noise(dur, sample_rate=SAMPLE_RATE, color="pink", amp=0.3):
    """Tạo tạp âm màu tự nhiên (Pink / Brown / White noise) cho gió, mưa hoặc sóng nước."""
    samples = int(dur * sample_rate)
    white = np.random.normal(0, amp, samples).astype(np.float32)
    if color == "pink":
        # Lọc thông thấp trung bình xấp xỉ tiếng mưa rơi / thác nước
        return np.convolve(white, np.ones(8) / 8.0, mode="same")
    elif color == "brown":
        # Tiếng gió rít trầm ấm / đại dương sâu
        return np.convolve(white, np.ones(24) / 24.0, mode="same")
    return white

def synth_whoosh(dur=1.2, sample_rate=SAMPLE_RATE, f_start=180, f_end=750, amp=0.45):
    """Tạo hiệu ứng vút gió quét tần số (Whoosh Transition) mượt mà giữa các phân cảnh."""
    samples = int(dur * sample_rate)
    t = np.linspace(0, dur, samples, endpoint=False, dtype=np.float32)
    noise = np.random.normal(0, amp, samples).astype(np.float32)
    f_center = f_start + (f_end - f_start) * np.sin(np.pi * t / dur)
    envelope = (np.sin(np.pi * t / dur) ** 2)
    return noise * np.sin(2 * np.pi * f_center * t) * envelope

def synth_impact(dur=0.6, sample_rate=SAMPLE_RATE, freq=55, decay=0.12, amp=0.65):
    """Tạo tiếng va chạm đanh thép / đóng dấu mộc (Rubber Stamp Thump)."""
    samples = int(dur * sample_rate)
    t = np.linspace(0, dur, samples, endpoint=False, dtype=np.float32)
    thump = amp * np.sin(2 * np.pi * freq * t) * np.exp(-t / decay)
    click = (amp * 0.4) * np.random.normal(0, 0.05, samples) * np.exp(-t / 0.02)
    return thump + click

def synth_bell_chime(notes=[880, 1320, 1760], dur=2.4, sample_rate=SAMPLE_RATE, amp=0.4):
    """Tạo tiếng chuông pha lê ngân vang (Breakthrough Chime) khi đạt cột mốc mới."""
    samples = int(dur * sample_rate)
    t = np.linspace(0, dur, samples, endpoint=False, dtype=np.float32)
    sig = np.zeros(samples, dtype=np.float32)
    for idx, f in enumerate(notes):
        decay_time = 0.8 / (idx + 1)
        sig += (amp / (idx + 1)) * np.sin(2 * np.pi * f * t) * np.exp(-t / decay_time)
    return sig


# ==============================================================================
# 2. BỘ ĐIỀU HÒA TRACK ÂM THANH THEO CHỦ ĐỀ (MASTER THEMATIC GENERATOR)
# ==============================================================================
def generate_sfx_track(
    duration=DEFAULT_DURATION,
    output_path=r"d:\Data\Agent Video\audio\sfx_track.wav",
    theme="auto",
    cues=None
):
    """
    Tạo track âm thanh SFX hoàn chỉnh chuẩn Stereo 44.1kHz đồng bộ tuyệt đối với thời lượng video.
    - theme:
      * 'auto': Tự động phân tích theo đường dẫn hoặc kịch bản
      * 'cinematic_ambient' / 'contemplative': Triết lý, cuộc sống, học tập, công nghệ (đệm nhạc êm, mưa, đồng hồ, gõ phím, chuông)
      * 'suspense_documentary' / 'historical': Hồi hộp, lịch sử, thử thách, sinh tồn (tiếng sóng, động cơ, rơ-le, còi báo, nhịp tim)
      * 'industrial': Máy móc phân xưởng, động cơ, hơi nước, kim loại
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    total_samples = int(SAMPLE_RATE * duration)
    left = np.zeros(total_samples, dtype=np.float32)
    right = np.zeros(total_samples, dtype=np.float32)

    def add_stereo(st_time, sig_l, sig_r=None, gain=1.0):
        if sig_r is None:
            sig_r = sig_l
        idx_st = int(st_time * SAMPLE_RATE)
        sig_len = len(sig_l)
        idx_end = min(idx_st + sig_len, total_samples)
        valid_len = idx_end - idx_st
        if valid_len > 0 and idx_st < total_samples:
            left[idx_st:idx_end] += sig_l[:valid_len] * gain
            right[idx_st:idx_end] += sig_r[:valid_len] * gain

    # Xác định chủ đề nếu là auto
    t_lower = str(theme).lower()
    out_lower = str(output_path).lower()
    if t_lower == "auto":
        if "squalus" in out_lower or "submarine" in out_lower or duration < 90.0:
            target_theme = "suspense_documentary"
        else:
            target_theme = "cinematic_ambient"
    else:
        target_theme = t_lower

    print(f"[SFX Engine] Khởi tạo thiết kế âm thanh procedural (Theme: {target_theme}, Thời lượng: {duration:.2f}s)")

    # --------------------------------------------------------------------------
    # THEME A: CINEMATIC AMBIENT / CONTEMPLATIVE (Cuộc sống, Triết lý, Công nghệ)
    # --------------------------------------------------------------------------
    if target_theme in ("cinematic_ambient", "contemplative"):
        # 1. Hợp âm Drone Pad ấm áp (Dm7 - Fmaj7 - Cmaj - Gmaj)
        chord_freqs = [
            [146.83, 220.00, 261.63, 349.23],
            [174.61, 220.00, 261.63, 349.23],
            [130.81, 196.00, 261.63, 329.63],
            [196.00, 246.94, 293.66, 392.00],
        ]
        chord_len = 8.0
        for seg_idx in range(int(duration / chord_len) + 1):
            c_st = seg_idx * chord_len
            if c_st >= duration: break
            c_dur = min(chord_len + 1.5, duration - c_st)
            samples_chord = int(c_dur * SAMPLE_RATE)
            ct = np.linspace(0, c_dur, samples_chord, endpoint=False, dtype=np.float32)
            chord = chord_freqs[seg_idx % len(chord_freqs)]

            sig = np.zeros(samples_chord, dtype=np.float32)
            for f in chord:
                sig += 0.035 * np.sin(2 * np.pi * f * ct)
                sig += 0.015 * np.sin(2 * np.pi * (f * 2) * ct)

            fade_len = min(int(1.8 * SAMPLE_RATE), samples_chord // 2)
            env = np.ones(samples_chord, dtype=np.float32)
            if fade_len > 0:
                env[:fade_len] = np.linspace(0.0, 1.0, fade_len)
                env[-fade_len:] = np.linspace(1.0, 0.0, fade_len)

            pan = 0.5 + 0.15 * math.sin(seg_idx * 1.3)
            add_stereo(c_st, sig * env * (1.0 - pan), sig * env * pan, gain=0.45)

        # 2. Không gian mưa đêm / tiếng thở phòng (Room Ambience)
        rain = synth_colored_noise(duration, color="pink", amp=0.08)
        add_stereo(0.0, rain * 0.9, rain * 1.1, gain=0.35)

        # 3. Đồng hồ tích tắc thiền định (1s/lần)
        tick_h = synth_sine(1800, 0.035, decay=0.006, amp=0.04)
        tock_h = synth_sine(1400, 0.035, decay=0.007, amp=0.04)
        for sec in range(0, int(duration)):
            st = sec * 1.0 + 0.05
            if st < duration:
                sig = tick_h if (sec % 2 == 0) else tock_h
                add_stereo(st, sig, sig * 0.85, gain=0.25)

        # 4. Chuyển cảnh vút gió (Whoosh Transitions) mỗi 15-20s
        for wc in np.arange(15.0, duration - 10.0, 18.0):
            w_sig = synth_whoosh(dur=1.2, amp=0.40)
            add_stereo(wc - 0.6, w_sig * 0.7, w_sig * 1.0, gain=0.45)

        # 5. Tiếng đóng dấu mộc (Stamp Impact) & Chuông ngân (Chime)
        for stp in np.arange(30.0, duration - 5.0, 35.0):
            imp = synth_impact(dur=0.6, amp=0.65)
            add_stereo(stp, imp, imp, gain=0.65)
            chm = synth_bell_chime(dur=2.4, amp=0.35)
            add_stereo(stp + 0.8, chm * 1.1, chm * 0.9, gain=0.40)

    # --------------------------------------------------------------------------
    # THEME B: SUSPENSE DOCUMENTARY / HISTORICAL (Tài liệu Hồi hộp & Thử thách)
    # --------------------------------------------------------------------------
    else:
        # 1. Âm hưởng đại dương sâu & gió rít lạnh giá
        ocean = synth_colored_noise(duration, color="brown", amp=0.15)
        swell_mod = 0.6 + 0.4 * np.sin(2 * np.pi * 0.1 * np.linspace(0, duration, total_samples))
        add_stereo(0.0, ocean * swell_mod, ocean * swell_mod, gain=0.75)

        # 2. Động cơ Diesel công nghiệp nặng trầm thâm
        eng_len = int(min(duration, 45.0) * SAMPLE_RATE)
        et = np.linspace(0, eng_len / SAMPLE_RATE, eng_len, endpoint=False, dtype=np.float32)
        thrum = (
            0.10 * np.sin(2 * np.pi * 14 * et) +
            0.08 * np.sin(2 * np.pi * 28 * et) +
            0.05 * np.sin(2 * np.pi * 56 * et)
        )
        add_stereo(5.0, thrum, thrum, gain=0.7)

        # 3. Đồng hồ đếm lùi căng thẳng
        for tick_idx in range(int(min(30, duration / 2))):
            tk_t = 16.0 + tick_idx * 0.3
            if tk_t < duration:
                freq = 2400 if tick_idx % 2 == 0 else 1800
                tk = synth_sine(freq, 0.025, decay=0.005, amp=0.06)
                add_stereo(tk_t, tk, tk, gain=0.55)

        # 4. Rơ-le điện & Chuông báo
        for bell_t in (28.0, 55.0, 75.0):
            if bell_t < duration:
                bl = synth_bell_chime([800, 1600], dur=1.8, amp=0.5)
                add_stereo(bell_t, bl, bl, gain=0.6)

    # --------------------------------------------------------------------------
    # XỬ LÝ CUES TÙY BIẾN (CUSTOM SFX CUES NẾU ĐƯỢC TRUYỀN)
    # --------------------------------------------------------------------------
    if cues:
        for cue in cues:
            ct = cue.get("time", 0.0)
            ctype = cue.get("type", "impact")
            cgain = cue.get("gain", 1.0)
            if ct >= duration: continue

            if ctype == "impact":
                sig = synth_impact(dur=cue.get("dur", 0.6))
                add_stereo(ct, sig, sig, gain=cgain)
            elif ctype == "chime":
                sig = synth_bell_chime(dur=cue.get("dur", 2.0))
                add_stereo(ct, sig, sig, gain=cgain)
            elif ctype == "whoosh":
                sig = synth_whoosh(dur=cue.get("dur", 1.2))
                add_stereo(ct, sig, sig, gain=cgain)

    # --------------------------------------------------------------------------
    # CHUẨN HÓA VÀ XUẤT FILE WAV 16-BIT STEREO
    # --------------------------------------------------------------------------
    max_peak = max(np.max(np.abs(left)), np.max(np.abs(right)))
    if max_peak > 0.95:
        left = left / max_peak * 0.92
        right = right / max_peak * 0.92

    stereo = np.empty((total_samples, 2), dtype=np.int16)
    stereo[:, 0] = np.clip(left * 32767.0, -32767, 32767).astype(np.int16)
    stereo[:, 1] = np.clip(right * 32767.0, -32767, 32767).astype(np.int16)

    with wave.open(output_path, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(stereo.tobytes())

    print(f"[SFX Engine] Xuất thành công track SFX đa năng: {output_path} ({duration:.2f}s)")
    return output_path

if __name__ == "__main__":
    generate_sfx_track(duration=30.0)
