# Quy Trình Dựng Video Hoạt Họa 2D Tài Liệu Điện Ảnh Tự Động (Turnkey Automated Pipeline)

Dự án này là hệ thống **Dựng video tài liệu hoạt họa 2D điện ảnh tự động từ file voice đa ngôn ngữ**, ứng dụng kiến trúc kết hợp **AI Concept Art Generator + PyCairo Compositor Engine**. 

> [!IMPORTANT]
> **Bộ Tiêu Chuẩn Sản Xuất Mới (Cinematic Hybrid Standard)**:
> 1. **Tuyệt đối không làm slide PowerPoint**: Toàn bộ video là các cảnh hoạt họa chuyển động sống động với tranh minh họa 2D vector điện ảnh 16:9 sắc nét, máy quay dolly zoom/pan, khói bụi, ánh sáng thể tích và các thành phần giao diện tương tác thật (màn hình CRT, đồng hồ đếm ngược, hộp thoại popup, dấu mộc va đập).
> 2. **Voice tiếng nào -> Video tiếng đó**: Đồng bộ 100% ngôn ngữ hiển thị với file voice, sử dụng chuẩn font `Segoe UI` để không bao giờ bị lỗi dấu hay ô vuông Unicode.
> 3. **Phân tách bố cục hoàn hảo**: Nhãn huy hiệu (Badge) luôn cách tiêu đề chính tối thiểu >= 45px; phụ đề nổi dạng kính mờ (glassmorphic pill) đặt tại đáy màn hình không che khuất hình ảnh.

---

## 1. Cách Sử Dụng Nhanh (1 Bước Duy Nhất)

### Cách A: Yêu cầu AI Agent
Chỉ cần gửi hoặc tải lên file voice bất kỳ và nói:
> *"Dựng video từ file voice này cho tôi"*

AI Agent sẽ tự động phân tích độ dài voice, tạo bộ tranh minh họa điện ảnh, kích hoạt track SFX đồng bộ và xuất video MP4 Full HD hoàn chỉnh.

### Cách B: Chạy thủ công trên máy tính
Mở CMD hoặc PowerShell tại thư mục dự án:

```bat
:: Dựng từ file voice (tự động nhận diện kịch bản và ngôn ngữ)
produce.bat "audio\dzogame_voice.mp3" "" "vi"
```

Hoặc dùng PowerShell:
```powershell
.\produce.ps1 -Audio "audio\dzogame_voice.mp3" -Lang "vi"
```

---

## 2. Kiến Trúc Các Thành Phần Dùng Chung (`src/`)

| Tệp / Thư mục | Vai trò |
| :--- | :--- |
| **`art/`** | **Kho Tranh Minh Họa Nền Điện Ảnh (1080p Art Plates)**: Chứa các tác phẩm tranh vẽ 2D vector điện ảnh tỉ lệ 16:9 chất lượng cao làm phông nền cho từng phân cảnh (phòng nét cỏ, data center, kiếm khách trên đỉnh núi, cỗ máy bào tiền...). |
| **`src/render_dzogame_voice_animation.py`** | **Mẫu Kịch Bản Render Chuẩn Mực Cao Nhất (Master Template)**: Minh họa cách tích hợp hoàn chỉnh: nạp ImageSurface, điều khiển máy quay dolly zoom mượt mà, tạo hạt sáng/khói/hơi nước động, hiển thị đồng hồ đếm ngược CRT, hộp thoại popup và xuất trực tiếp sang FFmpeg. |
| **`src/generate_sfx.py`** | **Bộ Tổng Hợp Âm Thanh Thủ Tục Đa Năng (Procedural SFX Engine)**: Tổng hợp âm thanh Stereo 44.1kHz khớp chuẩn xác từng mili-giây với voiceover. Hỗ trợ đa dạng chủ đề (`gaming_documentary`, `suspense_documentary`, `cinematic_ambient` và `industrial`). Đã khử sạch hoàn toàn tạp âm xèo xèo/rè rè (ambient noise layer), âm thanh trong trẻo, êm dịu. |
| **`src/layout_validator.py`** | **Bộ Kiểm Định Bố Cục & Phông Chữ Tự Động (Quality Gate)**: Tự động chạy trước mọi tiến trình render video. Khử sạch ký tự lạ Unicode gây ô vuông `[]`, tự động ngắt dòng thông minh (`draw_safe_text`), kiểm soát khoảng cách an toàn chống che khuất nhân vật và cách ly đường vẽ PyCairo. |
| **`src/localization.py`** | **Bộ Từ Điển & Quản Lý Đa Ngôn Ngữ**: Quản lý toàn bộ văn bản hiển thị cho Tiếng Việt (`vi`), Tiếng Anh (`en`...) và tự động map font chuẩn `Segoe UI`. |
| **`src/auto_produce.py`** | **Bộ Điều Khiển Trung Tâm Tự Động Hóa**: Tự động đo thời lượng audio qua `ffprobe`, tự phát hiện custom render script trong `src/`, điều phối tạo SFX sạch không xèo xèo (hỗ trợ cờ `--no-sfx` để tắt hẳn SFX), chạy kiểm định layout, xuất 8 ảnh mẫu preview và render video MP4 hoàn chỉnh. |
| **`produce.bat` / `produce.ps1`** | **Script khởi chạy nhanh**: Cấu hình tự động môi trường Python 3.12 và FFmpeg trên Windows. |

---

## 3. Thư Mục Lưu Trữ

- **`audio/`**: Nơi lưu trữ file voiceover đầu vào và các file âm thanh SFX đồng bộ (`<voice_name>_sfx.wav`).
- **`art/`**: Nơi lưu trữ bộ tranh minh họa nền 1080p PNG cho từng phân cảnh.
- **`output/`**: Nơi xuất video hoàn chỉnh (`.mp4`) và các hình ảnh xem trước keyframe (`dzogame_preview_*.png`).
- **`.agents/skills/edit-2d-animation/`**: Bộ Skill được cập nhật tự động hướng dẫn AI Agent áp dụng quy trình chuẩn này vĩnh viễn cho mọi video tương lai.
