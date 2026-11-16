---
name: edit-2d-animation
description: Automated end-to-end 2D cinematic flat-vector documentary animation director and video generator. Ingests any voiceover audio file (MP3/WAV) and automatically produces a 1080p 30fps cinematic animated documentary video with dynamic matching language typography, anatomical character rigs, atmospheric environments, and synchronized sound design.
allowed-tools: google default_api image_gen run_command
---
# Edit-2d-animation: Automated Cinematic Documentary Production

A turnkey, fully procedural 2D cinematic vector animation pipeline designed for historical chronicles and scientific documentary storytelling.

When the user uploads or provides **ANY voiceover audio file** (MP3, WAV, M4A, etc.), automatically run the end-to-end production pipeline to generate a broadcast-grade 1080p 30fps MP4 video with synchronized procedural SFX, dynamic camera movements, matching language typography, and detailed character/environmental rigs.

---

## 1. Style & Production Core Principles (Strictly Enforced)

1. **Animated Storytelling Over Statistics**: Focus heavily on living, cinematic animated sequences that bring the narrative to life (character actions, tension, camera movement, atmospheric depth). Never turn the video into a static image slideshow or an infographic lecture.
2. **Historical Chronicle Atmosphere**: Suspenseful, dramatic, and emotionally engaging pacing.
3. **Dynamic Matching Language (CRITICAL RULE)**:
   - **Voice tiếng nào -> Ngôn ngữ trên video hiển thị Tiếng đó**:
     * Voice Tiếng Việt -> Toàn bộ tiêu đề, thông số HUD, nhãn van và phụ đề hiển thị bằng Tiếng Việt.
     * Voice Tiếng Anh (English) -> Toàn bộ tiêu đề, thông số HUD, nhãn van và phụ đề hiển thị bằng Tiếng Anh.
     * Voice các ngôn ngữ khác (Pháp, Đức, Nhật, v.v.) -> Hệ thống tự động chuyển đổi sang ngôn ngữ tương ứng.
   - **Font Chữ Chuẩn Từng Ngôn Ngữ**: Tự động chọn font hiển thị tối ưu (`Segoe UI` cho Tiếng Việt / Tiếng Anh để không bị lỗi dấu Unicode; `Yu Gothic` / `Microsoft YaHei` cho tiếng Nhật / Trung).
4. **Cinematic Camera Techniques**: Continuous depth parallax, slow dolly creeps, camera rumble/shake on explosions/impacts, and dramatic Dutch angles.
5. **Detailed Animated Environments**: Rich, immersive environments with atmospheric depth (North Atlantic dawn mist, volumetric sunbeams, opposed-piston diesel engine rooms, cast-iron naval bulkhead telephone stations, flooded compartments).
6. **Natural Anatomical Character Rigging**: Chiaroscuro rim lighting, distinct facial expressions (determination, tension, horror), uniform details (Service Dress Blue coats, lieutenant gold braid, officer combination caps, denim machinist workwear).
7. **Frame-Accurate Synchronized SFX**: Procedurally synthesized environmental foley (deep ocean swells, diesel idle/cutoff, dual AHOOGA dive klaxons, pocket watch ticks, electrical relays, 80cm valve impact, high-pressure water deluge, brass telephone bells, equipment slide clatter, sub-bass heartbeat).
8. **Preserve Approved Voiceover**: Maintain 100% fidelity to the provided voiceover narration without rewriting or shortening.

---

## 2. Immediate Automated Workflow on Voice File Ingestion

When the user says "Tôi gửi file voice...", "Hãy dựng video từ voice này...", or uploads an audio file:

### Step 1: Ingest Voiceover Audio
Save or copy the audio file to `d:\Data\Agent Video\audio\<voice_name>.<ext>`.

### Step 2: Determine Language & Run Turnkey Pipeline
Detect the language of the voiceover (or specify `--lang <vi|en|auto>`) and execute:

```powershell
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","User") + ";" + [System.Environment]::GetEnvironmentVariable("Path","Machine")
python "d:\Data\Agent Video\src\auto_produce.py" --audio "d:\Data\Agent Video\audio\<voice_name>.<ext>" --lang auto
```
*(Or in Windows CMD/terminal: `d:\Data\Agent Video\produce.bat "audio\<voice_name>.<ext>" "" "<vi|en>"`).*

### Step 3: What `auto_produce.py` Handles Automatically:
1. **Audio Probe**: Uses `ffprobe` to determine the exact audio duration down to the millisecond.
2. **Language Adaptation**: Maps all on-screen titles, HUD callouts, and captions to the detected language via `src/localization.py`.
3. **SFX Track Generation**: Automatically calls `src/generate_sfx.py` to synthesize a complete synchronized foley/SFX track matching the audio length.
4. **Keyframe Previews**: Renders 13 high-resolution keyframe preview plates in `d:\Data\Agent Video\output\cinematic_<lang>_preview_*.png` across all narrative beats.
5. **Video Rendering & Mixing**:
   - Renders 1920x1080 30fps vector frames via PyCairo.
   - Slices Cairo ARGB32 memory directly into FFmpeg `bgr24` stdin stream.
   - Mixes Voiceover (volume 1.0) with Foley SFX (volume 0.62) using FFmpeg `amix`.
   - Encodes high-bitrate H.264 video (`-crf 18`, `-preset fast`, `-pix_fmt yuv420p`).
6. **Outputs Final Video**:
   Saves to `d:\Data\Agent Video\output\<voice_name>_<lang>_cinematic.mp4`.

### Step 4: Verification & Presentation
1. Inspect generated preview plates and verify video specs with `ffprobe`.
2. Present clickable markdown links to the final video (`file:///d:/Data/Agent%20Video/output/<video_name>.mp4`) and preview plates to the user.

---

## 3. Shared Modular Architecture (`d:\Data\Agent Video\src\`)

The codebase is organized into clean, reusable modules preserved for future productions:

- **`src/assets_library.py`**: Core 2D vector & procedural animation library:
  * Hierarchical skeletal rigging (`BoneNode`, `ActorRig`).
  * Rig builders (`RigBuilder`): human rigs (diver, explorer, swimmer, civilian, casual, officer, machinist), aquatic creatures (shark, orca, whale), animals (wolf, bear, bird), and vessels (submersible, research boat).
  * Procedural motion solvers (`ProceduralMotion`): walk, run, sit, type at desk, talk, inspect, swim, spine undulation, wing flap, vessel cruise.
  * Reusable parallax environments (`EnvironmentRenderer`): cozy workspace at night, crossroad horizon, blueprint grid, historical journal card, underwater cross-section, mountain forest.
  * Technical HUD & Infographics (`HUDRenderer`): scale wireframe, reticle, percent donut gauge, callout pin, rubber stamp, subtitle box, lower third, milestone badge.
  * Master Storyboard Engine (`StoryboardRunner`): interprets JSON storyboards (`storyboards/<name>.json`) and renders full videos without manual animation code.
- **`src/auto_produce.py`**: Turnkey master entry point for automated voice-to-video production with automatic language detection, duration scaling, Storyboard JSON auto-dispatch, and custom script support.
- **`src/render_tuoi32_animation.py`**: Life reflection & documentary animation script for "Tuổi 32", demonstrating full integration with `assets_library.py`.
- **`src/localization.py`**: Centralized language dictionary and font mapping for Vietnamese, English, and other languages.
- **`src/components.py`**: Sargo-class fleet submarine hull, watertight oval door with dogging lugs, multi-layer ocean waves, vignette, and vector primitives.
- **`src/art_assets.py`**: Lieutenant Oliver Naquin portrait with chiaroscuro rim lighting and emotional expressions, submarine control room, sound-powered bulkhead telephone station, and flooded diesel engine room.
- **`src/generate_sfx.py`**: Procedural sound design engine synthesizing synchronized SFX layers.
- **`src/render_cinematic_animation.py`**: Language-adaptive PyCairo master scene renderer and FFmpeg video pipeline.
- **`produce.bat` / `produce.ps1`**: Fast one-click launchers for Windows supporting voiceovers, Storyboard JSONs, and custom scripts.
