import os
import sys
import argparse
import subprocess
import shutil
import re

# Ensure local imports from src work properly
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from generate_sfx import generate_sfx_track
from render_cinematic_animation import render_cinematic_video, generate_previews
from localization import get_font_for_lang, SCENE_LOCALIZATIONS

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

def auto_produce(audio_path, output_mp4=None, sfx_path=None, fps=30, lang="auto", preview_only=False):
    """
    Master automated turnkey pipeline:
    Voice Audio In -> Language Detection -> Duration Probe -> Synced SFX Generation -> PyCairo 1080p Render -> FFmpeg Audio Mix -> MP4 Out
    """
    setup_environment()
    
    project_root = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
    
    if not os.path.isabs(audio_path) and not os.path.exists(audio_path):
        alt_path = os.path.join(project_root, audio_path)
        if os.path.exists(alt_path):
            audio_path = alt_path

    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Voiceover audio file not found: {audio_path}")

    # Determine language
    if not lang or lang.lower() == "auto":
        target_lang = detect_language_from_path(audio_path, fallback="vi")
    else:
        target_lang = lang.lower()
    
    if not output_mp4:
        base_name = os.path.splitext(os.path.basename(audio_path))[0]
        output_mp4 = os.path.join(project_root, "output", f"{base_name}_{target_lang}_cinematic.mp4")
        
    if not sfx_path:
        sfx_path = os.path.join(project_root, "audio", "sfx_track.wav")

    output_dir = os.path.dirname(output_mp4)
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(os.path.dirname(sfx_path), exist_ok=True)

    font_name = get_font_for_lang(target_lang)

    print("=====================================================================")
    print("      AUTOMATED 2D CINEMATIC DOCUMENTARY ANIMATION PIPELINE         ")
    print("=====================================================================")
    print(f"[*] Voiceover Audio : {audio_path}")
    print(f"[*] Visual Language : {target_lang.upper()} (Font: {font_name})")
    print(f"[*] Target MP4      : {output_mp4}")
    print(f"[*] SFX Track       : {sfx_path}")
    print(f"[*] Frame Rate      : {fps} FPS")

    # Step 1: Probe Audio Duration
    print("\n--- [Step 1/4] Probing Audio Duration ---")
    duration = probe_audio_duration(audio_path)
    print(f"[+] Audio Duration: {duration:.2f} seconds ({duration/60:.2f} minutes)")

    # Step 2: Generate Synchronized SFX Track
    print("\n--- [Step 2/4] Synthesizing Synchronized Foley & Ambiance SFX ---")
    generate_sfx_track(duration=duration, output_path=sfx_path)

    # Step 3: Generate Preview Keyframe Plates in Target Language
    print(f"\n--- [Step 3/4] Generating Cinematic Preview Keyframes ({target_lang.upper()}) ---")
    generate_previews(output_dir=output_dir, total_duration=duration, fps=fps, lang=target_lang)

    if preview_only:
        print("\n[Preview Mode] Previews generated. Skipping video encoding.")
        return output_mp4

    # Step 4: Render Full 1080p 30fps Video and Pipe to FFmpeg
    print(f"\n--- [Step 4/4] Rendering 2D Vector Animation ({target_lang.upper()}) & Piping to FFmpeg ---")
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
    parser = argparse.ArgumentParser(description="Automated Voice-to-Video 2D Cinematic Documentary Pipeline")
    parser.add_argument("--audio", "-a", required=True, help="Path to input voiceover audio file (MP3, WAV, etc.)")
    parser.add_argument("--output", "-o", default=None, help="Path to output MP4 file")
    parser.add_argument("--sfx", "-s", default=None, help="Path to generated SFX WAV file")
    parser.add_argument("--fps", type=int, default=30, help="Frames per second (default: 30)")
    parser.add_argument("--lang", "-l", default="auto", help="Language for on-screen text/HUD (e.g., vi, en, or auto)")
    parser.add_argument("--preview-only", action="store_true", help="Generate preview plates only")
    
    args = parser.parse_args()
    auto_produce(
        audio_path=args.audio,
        output_mp4=args.output,
        sfx_path=args.sfx,
        fps=args.fps,
        lang=args.lang,
        preview_only=args.preview_only
    )

if __name__ == "__main__":
    main()
