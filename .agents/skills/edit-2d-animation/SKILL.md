---
name: edit-2d-animation
description: Automated end-to-end 2D cinematic flat-vector documentary animation director and video generator. Ingests any voiceover audio file (MP3/WAV) and automatically produces a 1080p 30fps cinematic animated documentary video with dynamic matching language typography, concept art background plates, procedural atmospheric FX, and synchronized sound design.
allowed-tools: google default_api image_gen run_command
---
# Edit-2d-animation: Automated Cinematic Documentary Production

A turnkey, hybrid AI Concept Art + PyCairo 2D cinematic vector animation pipeline designed for historical chronicles, gaming retrospectives, scientific investigations, and storytelling documentaries.

When the user uploads or provides **ANY voiceover audio file** (MP3, WAV, M4A, etc.), automatically execute this end-to-end production workflow to generate a broadcast-grade 1080p 30fps MP4 video with custom cinematic art plates, dynamic camera movements, synchronized procedural SFX, matching language typography, and zero layout bugs.

---

## 1. Style & Production Core Principles (Strictly Enforced)

1. **Cinematic Storytelling Over Bullet-Point Slides (TUYỆT ĐỐI KHÔNG LÀM SLIDE POWERPOINT)**:
   - Nghiêm cấm hoàn toàn việc vẽ các khung thẻ chứa các gạch đầu dòng (`• ...`, `• ...`) trông giống slide thuyết trình khô khan.
   - Toàn bộ các phân cảnh phải là các cảnh phim hoạt họa sống động (Living Cinematic Sequences): sử dụng tranh vẽ minh họa điện ảnh tỉ lệ 16:9 sắc nét làm phông nền, kết hợp máy quay dolly zoom từ từ, ánh sáng thể tích, khói bụi bốc lên và các yếu tố giao diện tương tác thật (như màn hình CRT đếm ngược, hộp thoại thông báo, dấu mộc va đập).
2. **Quy Trình Hybrid: Concept Art Plate + PyCairo Compositor**:
   - Chia kịch bản voiceover thành các phân đoạn tự sự chính (6 - 10 cảnh).
   - Với mỗi phân cảnh, tự động kích hoạt tạo tranh minh họa nền 16:9 (1920x1080) bằng `image-generator` với phong cách 2D vector điện ảnh (flat-vector anime documentary art, không chứa chữ text rác).
   - Lưu trữ tại `d:\Data\Agent Video\art\sceneX_<slug>.png`.
   - PyCairo nạp trực tiếp ImageSurface vào bộ nhớ và tạo chuyển động máy quay (Slow Dolly Zoom 1.0 -> 1.08, Parallax Pan), phủ lớp hạt bụi, vệt mưa, luồng sáng, khói thuốc và các hiệu ứng động đồng bộ thời gian thực.
3. **Dynamic Matching Language (Voice tiếng nào -> Video tiếng đó)**:
   - Voice Tiếng Việt -> Toàn bộ tiêu đề, thông số HUD, phụ đề hiển thị bằng Tiếng Việt.
   - Voice Tiếng Anh -> Toàn bộ hiển thị bằng Tiếng Anh.
   - Font chữ chuẩn: Luôn dùng `Segoe UI` cho Tiếng Việt / Tiếng Anh để đảm bảo 100% không bao giờ lỗi dấu hay ô vuông Unicode.
4. **Quy Chuẩn Bố Cục Chữ & Tránh Đè Nét Tuyệt Đối (Zero Text Overlap & Collision)**:
   - **Khoảng cách nhãn huy hiệu (Badge) & Tiêu đề chính**: Đảm bảo khoảng cách lề tối thiểu >= 45px giữa Badge và Title.
     * Cụ thể: Badge đặt ở `y = 70 - 80` (cao ~30px, kết thúc ở `y = 100 - 110`).
     * Tiêu đề chính (Font 50 - 56) đặt ở `y = 175 - 185` (vùng an toàn cách mép dưới badge >= 40px).
     * Phụ đề phụ (Font 17 - 18) đặt ở `y = 210 - 225`.
   - **Vị trí các thẻ bổ trợ**: Đặt ở vùng dưới chân màn hình (`y = 730 - 840`), tách biệt hoàn toàn khỏi nhân vật và không bao giờ để kiếm/vật thể cắt ngang chữ.
   - **Hộp phụ đề nổi (Dynamic Subtitle Box)**: Đặt ở đáy màn hình (`y = 960`), có khung nền kính mờ đen mờ bo góc an toàn (`rgba(0.04, 0.06, 0.09, 0.88)`), không chạm thanh Letterbox (60px).
5. **Thiết Kế Âm Thanh Đồng Bộ Thủ Tục (Procedural Foley SFX Track)**:
   - Tự động nhận diện chủ đề âm thanh qua `src/generate_sfx.py`:
     * `gaming_documentary`: Tiếng gõ phím phòng nét, còi đếm ngược máy chủ, tiếng chập điện ngắt kết nối, chuông tái sinh phượng hoàng, cơ khí nghiền tiền và tiếng đồng xu.
     * `suspense_documentary`: Tiếng sóng ngầm đại dương, động cơ diesel, rơ-le điện, còi báo động lặn.
     * `cinematic_ambient`: Hợp âm pad ấm áp, tiếng mưa rơi, tích tắc đồng hồ.
   - Tự động tổng hợp file âm thanh nổi Stereo 44.1kHz khớp chuẩn xác từng mili-giây với voiceover.
6. **Kiểm Định Tự Động Trước Khi Render (Pre-Render Quality Gate)**:
   - Tự động chạy `validate_and_audit_scenes` trước khi kích hoạt FFmpeg.
   - Tự động khử ký tự lạ Unicode gây ô vuông [].
   - Tự động ngắt dòng thông minh (`wrap_text_to_lines` / `draw_safe_text`).
7. **Bảo Tồn 100% Giọng Đọc Nguyên Bản**:
   - Không tự ý cắt ngắn hoặc sửa đổi kịch bản giọng đọc gốc.

---

## 2. Quy Trình Sản Xuất Tự Động (Turnkey Workflow)

Khi người dùng cung cấp file voice bất kỳ:

### Bước 1: Lưu File Voice Đầu Vào
Sao chép file voice vào `d:\Data\Agent Video\audio\<voice_name>.<ext>`.

### Bước 2: Phân Tích Kịch Bản & Tạo Tranh Nền Điện Ảnh (Art Plates)
1. Dùng `ffprobe` xác định thời lượng chính xác của audio.
2. Phân tách kịch bản voiceover thành các phân cảnh tự sự (thường từ 6 - 8 cảnh).
3. Sử dụng `image-generator` để tạo tranh minh họa 2D vector điện ảnh 16:9 cho từng cảnh (không chứa chữ text trên ảnh), chuyển đổi về định dạng PNG 1080p và lưu vào `d:\Data\Agent Video\art\sceneX_<name>.png`.

### Bước 3: Tạo Render Script Kế Thừa Bộ Engine Mới
Tạo `d:\Data\Agent Video\src\render_<voice_name>_animation.py`:
- Nạp và đệm các ImageSurface từ `d:\Data\Agent Video\art\`.
- Áp dụng hàm `draw_cinematic_plate(...)` với chuyển động camera dolly zoom và parallax pan.
- Bổ sung hiệu ứng động: hạt sáng (`draw_particles_floating`), vệt mưa, khói thuốc, hơi nóng, đốm lửa, tia chớp, màn hình CRT, hộp thoại popup.
- Áp dụng hệ thống đồ họa tài liệu (Metadata HUD góc trên, tiêu đề vàng kim/cyan phát sáng, thẻ ngữ cảnh, hộp phụ đề nổi chuẩn Segoe UI).
- Danh sách `SUBTITLES = [(st, et, "text..."), ...]` đồng bộ từng câu thoại.

### Bước 4: Tạo Track Âm Thanh Đồng Bộ SFX
Chạy `generate_sfx_track(duration=duration, output_path=sfx_path, theme="auto")` từ `src/generate_sfx.py`.

### Bước 5: Kiểm Định Bố Cục & Kết Xuất Video Hoàn Chỉnh
Chạy qua lệnh master:
```powershell
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","User") + ";" + [System.Environment]::GetEnvironmentVariable("Path","Machine")
python "d:\Data\Agent Video\src\auto_produce.py" --audio "d:\Data\Agent Video\audio\<voice_name>.<ext>" --lang auto
```
Quy trình tự động thực hiện:
1. Tạo 8 ảnh mẫu xem trước (Preview Keyframe Plates) tại `d:\Data\Agent Video\output\`.
2. Kiểm tra trực quan ảnh mẫu để đảm bảo 100% không có lỗi bố cục.
3. Render từng khung hình 1080p 30fps qua PyCairo, truyền trực tiếp stream BGR vào FFmpeg.
4. Hòa âm Giọng đọc (Volume 1.0) và SFX (Volume 0.55) qua bộ lọc `amix`.
5. Xuất file MP4 độ nét cao (`-crf 18`, `-preset fast`, bitrate cao 3.5 - 4.5 Mbps).

### Bước 6: Trình Bày Kết Quả Cho Người Dùng
- Cung cấp link markdown trực tiếp đến video hoàn chỉnh: `file:///d:/Data/Agent%20Video/output/<video_name>.mp4`.
- Bảng danh sách các ảnh xem trước (Preview Plates) cho từng phân cảnh để người dùng duyệt nhanh chất lượng đồ họa.

---

## 3. Kiến Trúc Mã Nguồn Dùng Chung (`src/`)

- **`src/render_dzogame_voice_animation.py`**: Bản mẫu chuẩn mực cao nhất cho thể loại phim tài liệu / phóng sự điều tra gaming, sử dụng hoàn toàn cơ chế Hybrid Art Plate + PyCairo Compositor.
- **`src/generate_sfx.py`**: Engine âm thanh thủ tục với đa dạng chủ đề (`gaming_documentary`, `suspense_documentary`, `cinematic_ambient`, `industrial`).
- **`src/localization.py`**: Quản lý từ điển đa ngôn ngữ (VI, EN...) và ánh xạ font `Segoe UI`.
- **`src/layout_validator.py`**: Quality Gate tự động chống tràn viền, khử ô vuông Unicode và bảo vệ bố cục.
- **`src/auto_produce.py`**: Trình điều khiển trung tâm tự động nhận diện file script/storyboard và điều phối toàn bộ chuỗi sản xuất.
- **`produce.bat` / `produce.ps1`**: Bộ phóng tắt một bước cho Windows.
