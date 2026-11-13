import os
import sys
import wave
import numpy as np

SAMPLE_RATE = 44100
DEFAULT_DURATION = 81.9

def generate_sfx_track(duration=DEFAULT_DURATION, output_path=r"d:\Data\Agent Video\audio\sfx_track.wav"):
    """
    Generates high-fidelity procedural synchronized SFX for the cinematic documentary.
    If duration differs from the standard 81.9s, cue timestamps are scaled proportionally.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    total_samples = int(SAMPLE_RATE * duration)
    audio = np.zeros(total_samples, dtype=np.float32)
    t = np.linspace(0, duration, total_samples, endpoint=False)
    
    scale = duration / DEFAULT_DURATION
    
    def sc(timestamp):
        """Scale timestamp based on duration"""
        return timestamp * scale

    def add_sound(start_t, dur, signal, gain=1.0):
        idx_start = int(start_t * SAMPLE_RATE)
        idx_end = min(idx_start + len(signal), total_samples)
        sig_len = idx_end - idx_start
        if sig_len > 0 and idx_start < total_samples:
            audio[idx_start:idx_end] += signal[:sig_len] * gain

    # =====================================================================
    # 1. SCENE 1: North Atlantic Ocean Swell & Freezing Wind (0.0s – 12.0s)
    # =====================================================================
    swell_dur = min(15.0 * scale, duration)
    swell_samples = int(swell_dur * SAMPLE_RATE)
    swell_t = t[:swell_samples]
    swell = (
        0.08 * np.sin(2 * np.pi * 38 * swell_t) +
        0.05 * np.sin(2 * np.pi * 52 * swell_t)
    ) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.12 * swell_t))

    wind_raw = np.random.normal(0, 0.05, len(swell_t)).astype(np.float32)
    wind_mod = 0.5 + 0.5 * np.sin(2 * np.pi * 0.25 * swell_t)
    wind_whistle = np.sin(2 * np.pi * (160 + 40 * np.sin(2 * np.pi * 0.1 * swell_t)) * swell_t) * 0.02
    ocean_ambience = (swell + wind_raw * wind_mod + wind_whistle) * np.exp(-swell_t / (18.0 * scale))
    add_sound(0.0, swell_dur, ocean_ambience, gain=0.9)

    for lap_t in [1.5, 3.8, 6.2, 9.5]:
        st_lap = sc(lap_t)
        if st_lap < duration:
            l_dur = 0.45
            lt = np.linspace(0, l_dur, int(l_dur * SAMPLE_RATE), endpoint=False)
            lap = np.random.normal(0, 0.04, len(lt)) * np.sin(2 * np.pi * 350 * lt) * np.exp(-lt / 0.12)
            add_sound(st_lap, l_dur, lap, gain=0.6)

    # =====================================================================
    # 2. SCENE 2: Heavy Fairbanks-Morse Diesel Idling (7.5s – 29.5s)
    # =====================================================================
    diesel_start = sc(7.5)
    diesel_dur = 22.0 * scale
    if diesel_start < duration:
        eng_len = int(min(diesel_dur, duration - diesel_start) * SAMPLE_RATE)
        if eng_len > 0:
            et = np.linspace(0, eng_len / SAMPLE_RATE, eng_len, endpoint=False)
            diesel_thrum = (
                0.10 * np.sin(2 * np.pi * 14 * et) +
                0.08 * np.sin(2 * np.pi * 28 * et) +
                0.05 * np.sin(2 * np.pi * 56 * et) +
                0.03 * np.sin(2 * np.pi * 112 * et) +
                0.02 * np.sin(2 * np.pi * 224 * et)
            )
            piston_clicks = (np.sin(2 * np.pi * 14 * et) > 0.85).astype(np.float32) * 0.05
            bow_wash = np.random.normal(0, 0.03, eng_len).astype(np.float32) * (0.6 + 0.4 * np.sin(2 * np.pi * 1.5 * et))
            diesel_total = (diesel_thrum + piston_clicks + bow_wash)
            eng_env = np.ones(eng_len, dtype=np.float32)
            fade_in = min(int(2.0 * SAMPLE_RATE), eng_len // 2)
            if fade_in > 0:
                eng_env[:fade_in] = np.linspace(0, 1.0, fade_in)
            fade_out = min(int(1.2 * SAMPLE_RATE), eng_len // 2)
            if fade_out > 0:
                eng_env[-fade_out:] = np.linspace(1.0, 0.0, fade_out)
            add_sound(diesel_start, eng_len / SAMPLE_RATE, diesel_total * eng_env, gain=0.85)

    # =====================================================================
    # 3. SCENE 3: Control Room Tension & Watch Ticking (16.0s – 25.5s)
    # =====================================================================
    for tick_idx in range(40):
        tk_t = sc(16.5 + tick_idx * 0.2)
        if tk_t > sc(25.0) or tk_t >= duration: break
        tk_dur = 0.025
        tkt = np.linspace(0, tk_dur, int(tk_dur * SAMPLE_RATE), endpoint=False)
        freq = 2400 if tick_idx % 2 == 0 else 1800
        tick_sound = np.sin(2 * np.pi * freq * tkt) * np.exp(-tkt / 0.005) * 0.06
        add_sound(tk_t, tk_dur, tick_sound, gain=0.55)

    cr_start = sc(16.0)
    cr_dur = 9.5 * scale
    if cr_start < duration:
        cr_len = int(min(cr_dur, duration - cr_start) * SAMPLE_RATE)
        if cr_len > 0:
            crt = np.linspace(0, cr_len / SAMPLE_RATE, cr_len, endpoint=False)
            cr_hum = 0.02 * np.sin(2 * np.pi * 120 * crt) + 0.01 * np.sin(2 * np.pi * 240 * crt)
            add_sound(cr_start, cr_len / SAMPLE_RATE, cr_hum, gain=0.45)

    # =====================================================================
    # 4. SCENE 4: Submarine Dive Klaxon "AHOOGA!" (26.0s & 28.0s)
    # =====================================================================
    def generate_authentic_ahooga():
        k_dur = 0.85
        kt = np.linspace(0, k_dur, int(k_dur * SAMPLE_RATE), endpoint=False)
        freq = 190 + 210 * np.sin(np.pi * kt / k_dur)
        phase = 2 * np.pi * np.cumsum(freq) / SAMPLE_RATE
        horn = 0.28 * np.sin(phase) + 0.14 * np.sin(2 * phase) + 0.08 * np.sin(3 * phase) + 0.05 * np.sin(5 * phase)
        k_env = np.ones_like(kt)
        k_env[:int(0.04 * SAMPLE_RATE)] = np.linspace(0, 1.0, int(0.04 * SAMPLE_RATE))
        k_env[-int(0.12 * SAMPLE_RATE):] = np.linspace(1.0, 0.0, int(0.12 * SAMPLE_RATE))
        return horn * k_env

    add_sound(sc(26.1), 0.85, generate_authentic_ahooga(), gain=1.0)
    add_sound(sc(28.0), 0.85, generate_authentic_ahooga(), gain=1.0)

    # Telegraph gong strike
    tg_dur = 0.6
    tgt = np.linspace(0, tg_dur, int(tg_dur * SAMPLE_RATE), endpoint=False)
    telegraph_gong = (np.sin(2 * np.pi * 1560 * tgt) + 0.5 * np.sin(2 * np.pi * 2180 * tgt)) * np.exp(-tgt / 0.12) * 0.25
    add_sound(sc(26.6), tg_dur, telegraph_gong, gain=0.8)

    # Diesel shutoff shudder
    clank_dur = 0.5
    clt = np.linspace(0, clank_dur, int(clank_dur * SAMPLE_RATE), endpoint=False)
    shutoff_clank = (np.sin(2 * np.pi * 95 * clt) * 0.25 + np.random.normal(0, 0.15, len(clt))) * np.exp(-clt / 0.08)
    add_sound(sc(29.2), clank_dur, shutoff_clank, gain=0.85)

    # Electric motor hum
    em_start = sc(30.0)
    em_dur = 18.0 * scale
    if em_start < duration:
        em_len = int(min(em_dur, duration - em_start) * SAMPLE_RATE)
        if em_len > 0:
            emt = np.linspace(0, em_len / SAMPLE_RATE, em_len, endpoint=False)
            electric_hum = (0.04 * np.sin(2 * np.pi * 340 * emt) + 0.02 * np.sin(2 * np.pi * 680 * emt))
            em_env = np.ones(em_len, dtype=np.float32)
            em_fade_in = min(int(2.0 * SAMPLE_RATE), em_len // 2)
            em_fade_out = min(int(1.5 * SAMPLE_RATE), em_len // 2)
            if em_fade_in > 0: em_env[:em_fade_in] = np.linspace(0, 1.0, em_fade_in)
            if em_fade_out > 0: em_env[-em_fade_out:] = np.linspace(1.0, 0.0, em_fade_out)
            add_sound(em_start, em_len / SAMPLE_RATE, electric_hum * em_env, gain=0.6)

    # =====================================================================
    # 5. SCENE 5: Relay Clicks & Pneumatic Valve Seal (38.0s – 40.5s)
    # =====================================================================
    for relay_t in [38.1, 38.25, 38.45, 38.7, 38.9, 39.1]:
        r_dur = 0.035
        rt = np.linspace(0, r_dur, int(r_dur * SAMPLE_RATE), endpoint=False)
        relay_click = np.sin(2 * np.pi * 2100 * rt) * np.exp(-rt / 0.006) * 0.18
        add_sound(sc(relay_t), r_dur, relay_click, gain=0.75)

    pneu_dur = 1.0
    pnt = np.linspace(0, pneu_dur, int(pneu_dur * SAMPLE_RATE), endpoint=False)
    pneu_thud = np.sin(2 * np.pi * 65 * pnt) * np.exp(-pnt / 0.18) * 0.3
    pneu_hiss = np.random.normal(0, 0.08, len(pnt)) * np.exp(-pnt / 0.4)
    add_sound(sc(39.4), pneu_dur, pneu_thud + pneu_hiss, gain=0.85)

    # =====================================================================
    # 6. SCENE 6: Hydrodynamic Deep Water Glide (42.5s – 48.0s)
    # =====================================================================
    glide_start = sc(42.5)
    glide_dur = 5.5 * scale
    if glide_start < duration:
        glide_len = int(min(glide_dur, duration - glide_start) * SAMPLE_RATE)
        if glide_len > 0:
            gt = np.linspace(0, glide_len / SAMPLE_RATE, glide_len, endpoint=False)
            glide_sub = (0.05 * np.sin(2 * np.pi * 55 * gt) + 0.03 * np.sin(2 * np.pi * 85 * gt))
            prop_slip = np.random.normal(0, 0.02, glide_len).astype(np.float32) * (0.7 + 0.3 * np.sin(2 * np.pi * 6.0 * gt))
            add_sound(glide_start, glide_len / SAMPLE_RATE, glide_sub + prop_slip, gain=0.65)

    # =====================================================================
    # 7. SCENE 7: Ominous Electrical Glitch / Drone (48.0s – 50.0s)
    # =====================================================================
    glitch_dur = 2.0
    glt = np.linspace(0, glitch_dur, int(glitch_dur * SAMPLE_RATE), endpoint=False)
    glitch_drone = (
        0.08 * np.sin(2 * np.pi * 54 * glt) +
        0.08 * np.sin(2 * np.pi * 58 * glt) +
        0.03 * np.sin(2 * np.pi * 120 * glt)
    ) * np.linspace(0.3, 1.0, len(glt))
    add_sound(sc(48.0), glitch_dur, glitch_drone, gain=0.85)

    # =====================================================================
    # 8. SCENE 8: The 80cm Valve Rupture & Rivet Shear (50.0s – 57.5s)
    # =====================================================================
    crk_dur = 3.0
    crkt = np.linspace(0, crk_dur, int(crk_dur * SAMPLE_RATE), endpoint=False)
    metal_creak = np.sin(2 * np.pi * np.linspace(420, 180, len(crkt)) * crkt) * 0.08 * (0.5 + 0.5 * np.sin(2 * np.pi * 4.5 * crkt))
    add_sound(sc(50.5), crk_dur, metal_creak, gain=0.7)

    hyd_dur = 0.8
    hyt = np.linspace(0, hyd_dur, int(hyd_dur * SAMPLE_RATE), endpoint=False)
    hyd_pop = (np.sin(2 * np.pi * 450 * hyt) * 0.3 + np.random.normal(0, 0.15, len(hyt))) * np.exp(-hyt / 0.05)
    hyd_hiss = np.random.normal(0, 0.12, len(hyt)) * np.exp(-hyt / 0.3)
    add_sound(sc(53.8), hyd_dur, hyd_pop + hyd_hiss, gain=0.85)

    for snap_t in [54.5, 54.8, 55.1, 55.4]:
        sn_dur = 0.09
        snt = np.linspace(0, sn_dur, int(sn_dur * SAMPLE_RATE), endpoint=False)
        bolt_snap = (np.sin(2 * np.pi * 1450 * snt) * 0.35 + np.random.normal(0, 0.3, len(snt))) * np.exp(-snt / 0.012)
        add_sound(sc(snap_t), sn_dur, bolt_snap, gain=0.95)

    slam_dur = 1.2
    smt = np.linspace(0, slam_dur, int(slam_dur * SAMPLE_RATE), endpoint=False)
    valve_slam = (
        0.45 * np.sin(2 * np.pi * 75 * smt) * np.exp(-smt / 0.25) +
        0.35 * np.sin(2 * np.pi * 320 * smt) * np.exp(-smt / 0.15) +
        0.25 * np.random.normal(0, 0.4, len(smt)) * np.exp(-smt / 0.08)
    )
    add_sound(sc(55.6), slam_dur, valve_slam, gain=1.0)

    # =====================================================================
    # 9. SCENE 9: Catastrophic Freezing Water Deluge (57.5s – 67.0s)
    # =====================================================================
    deluge_dur = 9.5 * scale
    dlt = np.linspace(0, deluge_dur, int(deluge_dur * SAMPLE_RATE), endpoint=False)
    water_white = np.random.normal(0, 0.22, len(dlt)).astype(np.float32)
    water_sub = 0.18 * np.sin(2 * np.pi * 42 * dlt) + 0.12 * np.sin(2 * np.pi * 78 * dlt)
    d_env = np.ones(len(dlt), dtype=np.float32)
    d_env[:int(0.25 * SAMPLE_RATE)] = np.linspace(0, 1.0, int(0.25 * SAMPLE_RATE))
    ramp_out = min(int(3.0 * SAMPLE_RATE), len(dlt) // 2)
    d_env[-ramp_out:] = np.linspace(1.0, 0.3, ramp_out)
    water_deluge_sfx = (water_white + water_sub) * d_env
    add_sound(sc(57.5), deluge_dur, water_deluge_sfx, gain=0.95)

    for arc_t in [58.8, 60.5]:
        arc_dur = 0.5
        at = np.linspace(0, arc_dur, int(arc_dur * SAMPLE_RATE), endpoint=False)
        arc_sfx = (
            np.random.normal(0, 0.3, len(at)) * np.sin(2 * np.pi * 120 * at) +
            0.3 * np.sin(2 * np.pi * 480 * at)
        ) * np.exp(-at / 0.15)
        add_sound(sc(arc_t), arc_dur, arc_sfx, gain=0.85)

    # =====================================================================
    # 10. SCENE 10: Sound-Powered Bulkhead Telephone Ring (62.2s & 64.2s)
    # =====================================================================
    def generate_bulkhead_telephone_bell():
        b_dur = 0.85
        bt = np.linspace(0, b_dur, int(b_dur * SAMPLE_RATE), endpoint=False)
        clapper = 0.5 + 0.5 * np.sin(2 * np.pi * 24 * bt)
        bell_chime = (
            np.sin(2 * np.pi * 880 * bt) +
            0.8 * np.sin(2 * np.pi * 1150 * bt) +
            0.4 * np.sin(2 * np.pi * 1760 * bt)
        ) * clapper * np.exp(-bt / 0.55) * 0.22
        return bell_chime

    add_sound(sc(62.2), 0.85, generate_bulkhead_telephone_bell(), gain=0.95)
    add_sound(sc(64.2), 0.85, generate_bulkhead_telephone_bell(), gain=0.95)

    blow_dur = 3.5
    blt = np.linspace(0, blow_dur, int(blow_dur * SAMPLE_RATE), endpoint=False)
    ballast_hiss = np.random.normal(0, 0.08, len(blt)) * np.exp(-blt / 3.0)
    add_sound(sc(65.5), blow_dur, ballast_hiss, gain=0.65)

    # =====================================================================
    # 11. SCENE 11: Abyss Plunge & Escaping Air Plumes (69.5s – 74.0s)
    # =====================================================================
    abyss_dur = 4.5 * scale
    abt = np.linspace(0, abyss_dur, int(abyss_dur * SAMPLE_RATE), endpoint=False)
    groan_freq = np.linspace(55, 24, len(abt))
    groan_phase = 2 * np.pi * np.cumsum(groan_freq) / SAMPLE_RATE
    hull_groan = np.sin(groan_phase) * 0.22 * np.sin(np.pi * abt / abyss_dur)
    air_bubbles = np.random.normal(0, 0.12, len(abt)) * (0.6 + 0.4 * np.sin(2 * np.pi * 4.5 * abt))
    add_sound(sc(69.5), abyss_dur, hull_groan + air_bubbles, gain=0.85)

    # =====================================================================
    # 12. SCENE 12: 45° Tilt & Sliding Heavy Metal Clatter (74.0s – 77.0s)
    # =====================================================================
    for clt_t in [74.2, 74.5, 74.9, 75.3, 75.7, 76.2]:
        c_dur = 0.25
        ct = np.linspace(0, c_dur, int(c_dur * SAMPLE_RATE), endpoint=False)
        freq = np.random.choice([820, 1140, 1560, 1920])
        crash = (np.sin(2 * np.pi * freq * ct) * 0.25 + np.random.normal(0, 0.2, len(ct))) * np.exp(-ct / 0.04)
        add_sound(sc(clt_t), c_dur, crash, gain=0.75)

    # =====================================================================
    # 13. SCENE 13: Cinematic Heartbeat & Final Door Latch (77.0s – 81.9s)
    # =====================================================================
    for hb_t in [77.2, 78.7, 80.2]:
        shb = sc(hb_t)
        if shb < duration:
            h1_dur = 0.14
            h1t = np.linspace(0, h1_dur, int(h1_dur * SAMPLE_RATE), endpoint=False)
            lub = np.sin(2 * np.pi * 46 * h1t) * np.sin(np.pi * h1t / h1_dur) * 0.38
            add_sound(shb, h1_dur, lub, gain=0.95)
            
            h2_dur = 0.16
            h2t = np.linspace(0, h2_dur, int(h2_dur * SAMPLE_RATE), endpoint=False)
            dub = np.sin(2 * np.pi * 40 * h2t) * np.sin(np.pi * h2t / h2_dur) * 0.32
            add_sound(shb + 0.19, h2_dur, dub, gain=0.85)

    for sp_t in [77.5, 78.5, 79.5]:
        ssp = sc(sp_t)
        if ssp < duration:
            sp_dur = 0.6
            spt = np.linspace(0, sp_dur, int(sp_dur * SAMPLE_RATE), endpoint=False)
            water_lap = np.random.normal(0, 0.06, len(spt)) * np.exp(-spt / 0.25)
            add_sound(ssp, sp_dur, water_lap, gain=0.6)

    # Final heavy steel door dogging snap ("CLANG-DOG")
    snap_t = sc(81.1)
    if snap_t < duration:
        snap_dur = 0.4
        snt = np.linspace(0, snap_dur, int(snap_dur * SAMPLE_RATE), endpoint=False)
        final_snap = (
            0.45 * np.sin(2 * np.pi * 280 * snt) * np.exp(-snt / 0.08) +
            0.35 * np.sin(2 * np.pi * 920 * snt) * np.exp(-snt / 0.03) +
            0.20 * np.random.normal(0, 0.35, len(snt)) * np.exp(-snt / 0.02)
        )
        add_sound(snap_t, snap_dur, final_snap, gain=1.0)

    # Soft limiter / Normalization
    peak = np.max(np.abs(audio))
    if peak > 0.95:
        audio = (audio / peak) * 0.95

    audio_int16 = (audio * 32767).astype(np.int16)

    with wave.open(output_path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(audio_int16.tobytes())

    print(f"[SFX Generator] Successfully generated: {output_path} ({duration:.2f}s, {len(audio_int16)} samples)")
    return output_path

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else r"d:\Data\Agent Video\audio\sfx_track.wav"
    dur = float(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_DURATION
    generate_sfx_track(duration=dur, output_path=out)
