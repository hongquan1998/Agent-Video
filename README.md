# Quy Trình Dựng Video Hoạt Họa 2D Tài Liệu Điện Ảnh Tự Động (Turnkey Automated Pipeline)

Dự án này đã được tối ưu và đóng gói hoàn chỉnh thành một **Hệ thống dựng video tự động từ file voice đa ngôn ngữ**. 

> [!IMPORTANT]
> **Quy Tắc Ngôn Ngữ Đồng Bộ (Voice tiếng nào -> Video tiếng đó)**:
> Hệ thống sẽ tự động nhận diện ngôn ngữ của giọng đọc voiceover để hiển thị toàn bộ tiêu đề, thông số kỹ thuật (HUD), nhãn điều khiển và phụ đề trên video bằng chính ngôn ngữ đó (Voice Tiếng Việt -> Video Tiếng Việt; Voice Tiếng Anh -> Video Tiếng Anh; hoặc bất kỳ ngôn ngữ nào).

---

## 1. Cách Sử Dụng Nhanh (1 Bước Duy Nhất)

### Cách A: Yêu cầu AI Agent
Chỉ cần gửi hoặc tải lên file voice bất kỳ và nói:
> *"Dựng video từ file voice này cho tôi"*

AI Agent sẽ tự động nhận diện ngôn ngữ của voice, phân tích độ dài và kích hoạt quy trình sản xuất tự động.

### Cách B: Chạy thủ công trên máy tính
Mở CMD hoặc PowerShell tại thư mục dự án và chạy:

```bat
:: Chế độ tự động nhận diện ngôn ngữ (hoặc mặc định theo tên file)
produce.bat "path\to\voice.mp3"

:: Hoặc chỉ định rõ ngôn ngữ (ví dụ Tiếng Anh "en", Tiếng Việt "vi"):
produce.bat "path\to\voice.mp3" "" "en"
```

Hoặc dùng PowerShell:
```powershell
.\produce.ps1 -Audio "audio\voice.mp3" -Lang "en"
```

---

## 2. Kiến Trúc Các Thành Phần Dùng Chung (`src/`)

Toàn bộ tài nguyên và mã nguồn đã được module hóa để tái sử dụng vĩnh viễn:

| Tệp / Thư mục | Vai trò |
| :--- | :--- |
| **`src/localization.py`** | **Bộ từ điển & Quản lý đa ngôn ngữ**: Quản lý toàn bộ văn bản hiển thị trên video cho các ngôn ngữ (Tiếng Việt `vi`, Tiếng Anh `en`...) và tự động map font chữ chuẩn (`Segoe UI` cho VI/EN không lỗi dấu). |
| **`src/auto_produce.py`** | **Bộ điều khiển trung tâm tự động hóa**: Nhận file voice, đo thời lượng chính xác qua `ffprobe`, tự động chọn ngôn ngữ, kích hoạt tạo SFX, render PyCairo 1080p và xuất file MP4. |
| **`src/art_assets.py`** | **Thư viện đồ họa cao cấp**: Chân dung Đại úy Oliver Naquin (đổ bóng Chiaroscuro, biểu cảm đa dạng), phòng điều khiển trung tâm chi tiết (đồng hồ áp suất, kính tiềm vọng), trạm điện thoại xuyên vách ngăn U.S. Navy, khoang động cơ ngập nước và thủy thủ đoàn. |
| **`src/components.py`** | **Thư viện Rig & Vector**: Mô hình tàu ngầm lớp Sargo (vỏ thép, lỗ thoát nước, ốc đồng, tháp chỉ huy), cửa ngăn nước 3-inch, hệ thống sóng biển 4 tầng, hiệu ứng làm tối góc (vignette). |
| **`src/generate_sfx.py`** | **Bộ tổng hợp âm thanh thủ tục (SFX)**: Tự động điều chỉnh độ dài khớp với giọng nói. Bao gồm tiếng sóng biển Bắc Đại Tây Dương, còi lặn AHOOGA, động cơ diesel, rơ-le điện, bục van 80cm, xối nước áp lực cao, chuông điện thoại đồng và nhịp tim đập dồn dập. |
| **`src/render_cinematic_animation.py`** | **Bộ engine đồ họa vector 2D**: Chia khung hình, xử lý ngôn ngữ động theo tham số `lang` và xuất trực tiếp luồng BGR vào FFmpeg. |
| **`produce.bat` / `produce.ps1`** | **Script khởi chạy nhanh**: Tự động cấu hình biến môi trường Python 3.12 và FFmpeg trên Windows. |

---

## 3. Tiêu Chuẩn Nghệ Thuật Đã Được Thiết Lập (Style Guidelines)

1. **Voice tiếng nào -> Chữ tiếng đó**: Đảm bảo 100% văn bản hiển thị trên màn hình đồng bộ tuyệt đối với giọng đọc của file voice.
2. **Tập trung vào Kể chuyện hoạt họa (Animated Storytelling)**: Từng cảnh phim chuyển động sống động, có chiều sâu không gian, sương mù, góc máy camera lướt và rung lắc điện ảnh; không sử dụng slide tĩnh hay biểu đồ khô khan.
3. **Độ phân giải & Tần số quét**: Chuẩn Full HD `1920x1080` ở `30 fps` mượt mà.
4. **Hòa âm chuẩn Studio**: Tự động cân bằng âm lượng Giọng đọc (Voiceover: 100%) và Hiệu ứng âm thanh (SFX: 62%) để đảm bảo nghe rõ từng lời dẫn mà vẫn giữ được độ kịch tính, hùng tráng.
5. **Bảo tồn nội dung gốc**: Giữ nguyên 100% kịch bản giọng đọc được cung cấp.

---

## 4. Thư Mục Lưu Trữ
- **`audio/`**: Nơi chứa các file voice đầu vào và file âm thanh SFX đồng bộ.
- **`output/`**: Nơi xuất video hoàn chỉnh (`.mp4`) và các hình ảnh xem trước (`cinematic_vi_preview_*.png`, `cinematic_en_preview_*.png`).
- **`.agents/skills/edit-2d-animation/`**: Bộ Skill tự động kích hoạt cho AI Agent khi bạn gửi file voice trong tương lai.
