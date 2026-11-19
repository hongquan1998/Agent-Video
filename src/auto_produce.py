import os
import sys
import argparse
import subprocess
import shutil
import re
import importlib.util

# Ensure local imports from src work properly
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from generate_sfx import generate_sfx_track
from render_cinematic_animation import render_cinematic_video, generate_previews
from localization import get_font_for_lang, SCENE_LOCALIZATIONS
from layout_validator import validate_and_audit_scenes, sanitize_text
from assets_library import (
    StoryboardRunner, render_storyboard_video, generate_storyboard_previews,
    SceneRunner, RigBuilder, ProceduralMotion, EnvironmentRenderer, HUDRenderer
)

def setup_environment():
    """Ensure ffmpeg, ffprobe, and python paths are in os.environ['PATH']"""
    extra_paths = [
        r"C:\Users\Admin\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.2-full_build\bin",
        r"C:\Users\Admin\AppData\Local\Programs\Python\Python312",
        r"C:\Users\Admin\AppData\Local\Programs\Python\Python312\Scripts",
    ]
    current_path = os.environ.get("PATH", "")
    for p in extra_paths:
        if os.path.exists(p) and p.lower() not in current_path.lower():
            os.environ["PATH"] = p + ";" + os.environ.get("PATH", "")
            current_path = os.environ["PATH"]

def detect_language_from_path(audio_path, fallback="vi"):
    """
    Detect language based on audio file name, metadata, or path clues.
    E.g., squalus_en.mp3 -> en, voice_vi.wav -> vi.
    """
    path_lower = audio_path.lower()
    
    # Common language patterns in filenames
    patterns = [
        (r"[\b_\-\.](en|eng|english)[\b_\-\.]", "en"),
        (r"[\b_\-\.](vi|vie|viet|vietnamese|tieng_viet)[\b_\-\.]", "vi"),
        (r"[\b_\-\.](fr|fra|fre|french)[\b_\-\.]", "fr"),
        (r"[\b_\-\.](de|deu|ger|german)[\b_\-\.]", "de"),
        (r"[\b_\-\.](es|esp|spa|spanish)[\b_\-\.]", "es"),
        (r"[\b_\-\.](ja|jpn|japanese)[\b_\-\.]", "ja"),
        (r"[\b_\-\.](zh|zho|chi|chinese)[\b_\-\.]", "zh"),
        (r"[\b_\-\.](ru|rus|russian)[\b_\-\.]", "ru"),
    ]
    
    for pattern, lang in patterns:
        if re.search(pattern, path_lower):
            return lang
            
    return fallback

def probe_audio_duration(audio_file):
    """Accurately probe audio file duration using ffprobe with fallbacks"""
    setup_environment()
    
    ffprobe_bin = shutil.which("ffprobe")
    if ffprobe_bin:
        try:
            cmd = [
                ffprobe_bin,
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                audio_file
            ]
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            dur_str = result.stdout.strip()
            if dur_str:
                return float(dur_str)
        except Exception as e:
            print(f"[Warning] ffprobe probe failed: {e}")

    ffmpeg_bin = shutil.which("ffmpeg")
    if ffmpeg_bin:
        try:
            cmd = [ffmpeg_bin, "-i", audio_file]
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            for line in result.stderr.splitlines():
                if "Duration:" in line:
                    dur_part = line.split("Duration:")[1].split(",")[0].strip()
                    h, m, s = dur_part.split(":")
                    return float(h) * 3600 + float(m) * 60 + float(s)
        except Exception as e:
            print(f"[Warning] ffmpeg duration fallback failed: {e}")

    print("[Warning] Could not accurately determine duration, using default 81.9s")
    return 81.9

def auto_produce(audio_path=None, output_mp4=None, sfx_path=None, fps=30, lang="auto", preview_only=False, storyboard_path=None, script_path=None, no_sfx=False, include_noise=False):
    """
    Master automated turnkey pipeline:
    Voice Audio In -> Language Detection -> Duration Probe -> Synced SFX Generation -> PyCairo 1080p Render -> FFmpeg Audio Mix -> MP4 Out
    Tích hợp thư viện đồ họa vector procedural assets_library.py (hỗ trợ Storyboard JSON và Script mở rộng).
    """
    setup_environment()
    
    project_root = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
    
    if audio_path and not os.path.isabs(audio_path) and not os.path.exists(audio_path):
        alt_path = os.path.join(project_root, audio_path)
        if os.path.exists(alt_path):
            audio_path = alt_path

    if audio_path and not os.path.exists(audio_path):
        raise FileNotFoundError(f"Voiceover audio file not found: {audio_path}")

    # Determine language
    if not lang or lang.lower() == "auto":
        target_lang = detect_language_from_path(audio_path, fallback="vi") if audio_path else "vi"
    else:
        target_lang = lang.lower()
    
    base_name = os.path.splitext(os.path.basename(audio_path))[0] if audio_path else (
        os.path.splitext(os.path.basename(storyboard_path))[0] if storyboard_path else "tuoi32"
    )

    # Auto-detect storyboard if not specified
    if not storyboard_path and not script_path and audio_path:
        candidate_sb = [
            os.path.join(os.path.dirname(audio_path), f"{base_name}.json"),
            os.path.join(project_root, "storyboards", f"{base_name}.json"),
            os.path.join(project_root, "audio", f"{base_name}.json"),
        ]
        for csb in candidate_sb:
            if os.path.exists(csb):
                storyboard_path = csb
                print(f"[*] Tự động phát hiện Storyboard JSON: {storyboard_path}")
                break

    # Auto-detect custom render script if not specified
    if not storyboard_path and not script_path and audio_path:
        candidate_scripts = [
            os.path.join(project_root, "src", f"render_{base_name}_animation.py"),
            os.path.join(project_root, "src", f"render_{base_name}.py"),
        ]
        for csc in candidate_scripts:
            if os.path.exists(csc):
                script_path = csc
                print(f"[*] Tự động phát hiện Script render riêng: {script_path}")
                break

    if not output_mp4:
        output_mp4 = os.path.join(project_root, "output", f"{base_name}_{target_lang}_cinematic.mp4")
        
    if not no_sfx:
        if not sfx_path:
            sfx_path = os.path.join(project_root, "audio", "sfx_track.wav")
        os.makedirs(os.path.dirname(sfx_path), exist_ok=True)
    else:
        sfx_path = None

    output_dir = os.path.dirname(output_mp4)
    os.makedirs(output_dir, exist_ok=True)

    font_name = get_font_for_lang(target_lang)

    print("=====================================================================")
    print("      AUTOMATED 2D CINEMATIC DOCUMENTARY ANIMATION PIPELINE         ")
    print("=====================================================================")
    print(f"[*] Voiceover Audio : {audio_path or '(Không có file voice - Chế độ Storyboard đồ họa)'}")
    print(f"[*] Visual Language : {target_lang.upper()} (Font: {font_name})")
    print(f"[*] Target MP4      : {output_mp4}")
    print(f"[*] SFX Track       : {sfx_path or 'DISABLED (No SFX / Không âm thanh nền)'}")
    print(f"[*] Frame Rate      : {fps} FPS")
    if storyboard_path:
        print(f"[*] Engine Mode     : Storyboard JSON (src/assets_library.py)")
        print(f"[*] Storyboard File : {storyboard_path}")
    elif script_path:
        print(f"[*] Engine Mode     : Custom Script ({script_path})")
    else:
        print(f"[*] Engine Mode     : Built-in Cinematic Renderer (render_cinematic_animation.py)")

    # Step 1: Probe Audio Duration
    print("\n--- [Step 1/4] Probing Duration ---")
    if audio_path:
        duration = probe_audio_duration(audio_path)
        print(f"[+] Audio Duration: {duration:.2f} seconds ({duration/60:.2f} minutes)")
    elif storyboard_path:
        temp_runner = StoryboardRunner(storyboard_path)
        duration = temp_runner.total_duration
        print(f"[+] Storyboard Duration: {duration:.2f} seconds ({duration/60:.2f} minutes)")
    else:
        duration = 81.9
        print(f"[+] Default Duration: {duration:.2f} seconds")

    # Step 2: Generate Synchronized SFX Track
    if not no_sfx:
        print("\n--- [Step 2/5] Synthesizing Synchronized Foley & Ambiance SFX (No Noise/Xèo Xèo) ---")
        generate_sfx_track(duration=duration, output_path=sfx_path, include_noise=include_noise)
    else:
        print("\n--- [Step 2/5] SFX Disabled (--no-sfx). Skipping SFX synthesis ---")

    # Step 3: Automated Typography & Layout Quality Gate (Pre-Render Validation)
    print(f"\n--- [Step 3/5] Automated Typography & Layout Quality Gate ({target_lang.upper()}) ---")
    active_mod = None
    if script_path:
        spec = importlib.util.spec_from_file_location("custom_render_module", script_path)
        active_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(active_mod)
    validate_and_audit_scenes(active_mod, duration=duration, fps=fps, lang=target_lang, verbose=True)

    # Step 4: Generate Preview Keyframe Plates in Target Language
    print(f"\n--- [Step 4/5] Generating Preview Keyframes ({target_lang.upper()}) ---")
    if storyboard_path:
        generate_storyboard_previews(storyboard_path, output_dir=output_dir, fps=fps, lang=target_lang)
    elif script_path:
        spec = importlib.util.spec_from_file_location("custom_render_module", script_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        if hasattr(mod, "generate_previews"):
            mod.generate_previews(output_dir=output_dir, total_duration=duration, fps=fps, lang=target_lang)
        else:
            print("[Info] Custom script does not define generate_previews; skipping preview step.")
    else:
        generate_previews(output_dir=output_dir, total_duration=duration, fps=fps, lang=target_lang)

    if preview_only:
        print("\n[Preview Mode] Previews generated. Skipping video encoding.")
        return output_mp4

    # Step 5: Render Full 1080p 30fps Video and Pipe to FFmpeg
    print(f"\n--- [Step 5/5] Rendering 2D Vector Animation ({target_lang.upper()}) & Piping to FFmpeg ---")
    if storyboard_path:
        final_video = render_storyboard_video(
            storyboard_or_file=storyboard_path,
            voiceover_file=audio_path,
            sfx_file=sfx_path,
            output_mp4=output_mp4,
            duration=duration,
            fps=fps,
            lang=target_lang
        )
    elif script_path:
        spec = importlib.util.spec_from_file_location("custom_render_module", script_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        render_fn = getattr(mod, "render_cinematic_video", getattr(mod, "render_video", None))
        if render_fn:
            final_video = render_fn(
                voiceover_file=audio_path,
                sfx_file=sfx_path,
                output_mp4=output_mp4,
                duration=duration,
                fps=fps,
                lang=target_lang
            )
        else:
            raise AttributeError(f"Custom script {script_path} must define render_cinematic_video(...) or render_video(...)")
    else:
        final_video = render_cinematic_video(
            voiceover_file=audio_path,
            sfx_file=sfx_path,
            output_mp4=output_mp4,
            duration=duration,
            fps=fps,
            lang=target_lang
        )

    # Verification
    if os.path.exists(final_video):
        size_mb = os.path.getsize(final_video) / (1024 * 1024)
        print("\n=====================================================================")
        print("                 VIDEO PRODUCTION COMPLETE!                          ")
        print("=====================================================================")
        print(f"[SUCCESS] Final Video : {final_video}")
        print(f"[SUCCESS] Language    : {target_lang.upper()}")
        print(f"[SUCCESS] File Size   : {size_mb:.2f} MB")
        print(f"[SUCCESS] Resolution  : 1920x1080 (Full HD)")
        print(f"[SUCCESS] Framerate   : {fps} FPS")
        print("=====================================================================")
    else:
        print(f"[ERROR] Expected output file not found: {final_video}")

    return final_video

def main():
    parser = argparse.ArgumentParser(description="Automated Voice-to-Video 2D Cinematic Documentary Pipeline (PyCairo & assets_library)")
    parser.add_argument("--audio", "-a", default=None, help="Path to input voiceover audio file (MP3, WAV, etc.)")
    parser.add_argument("--output", "-o", default=None, help="Path to output MP4 file")
    parser.add_argument("--sfx", "-s", default=None, help="Path to generated SFX WAV file")
    parser.add_argument("--fps", type=int, default=30, help="Frames per second (default: 30)")
    parser.add_argument("--lang", "-l", default="auto", help="Language for on-screen text/HUD (e.g., vi, en, or auto)")
    parser.add_argument("--storyboard", "-sb", default=None, help="Path to JSON storyboard file (powered by assets_library.py)")
    parser.add_argument("--script", "-sc", default=None, help="Path to custom Python render script")
    parser.add_argument("--preview-only", action="store_true", help="Generate preview plates only")
    parser.add_argument("--no-sfx", action="store_true", help="Vô hiệu hóa hoàn toàn âm thanh nền SFX (chỉ dùng voiceover gốc)")
    parser.add_argument("--include-noise", action="store_true", help="Bật lại tạp âm phòng/mưa (mặc định đã tắt để chống xèo xèo)")
    
    args = parser.parse_args()
    if not args.audio and not args.storyboard and not args.script:
        parser.error("Cần cung cấp ít nhất một trong các tham số: --audio, --storyboard, hoặc --script.")

    auto_produce(
        audio_path=args.audio,
        output_mp4=args.output,
        sfx_path=args.sfx,
        fps=args.fps,
        lang=args.lang,
        preview_only=args.preview_only,
        storyboard_path=args.storyboard,
        script_path=args.script,
        no_sfx=args.no_sfx,
        include_noise=args.include_noise
    )

if __name__ == "__main__":
    main()
