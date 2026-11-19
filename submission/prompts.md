# Dùng AI

| # | Ai dùng | Công cụ | Prompt (tóm tắt) | AI sai ở đâu | Nhóm kiểm lại thế nào |
|---|---|---|---|---|---|
| 1 | khoivancw | ChatGPT/Codex | Viết phần kiểm thiếu ảnh, sai SHA và công cụ hỗ trợ review bằng mắt. | Gợi ý ban đầu chỉ xét hash ảnh; manifest thực tế còn có hash nhãn và mask. | AI đã chạy lô sạch và ca lỗi tạo trên bản sao tạm. Thành viên tự mở ảnh, kiểm lại và ghi nhận xét thật khi làm lab. |
| 2 | khoivancw | ChatGPT/Codex | Nâng cấp tool sàng lọc để người xem lại vùng nghi vấn. | Các ngưỡng chỉ gợi ý, lô sạch cũng có ứng viên. | AI đã thử bốn tình huống tổng hợp và tạo được lớp hiển thị cho hai ứng viên trên 50 ảnh sạch; kết luận do thành viên tự ghi. |
| 3 | khoivancw | ChatGPT/Codex | Hoàn thiện bảy luật CP1 và kiểm tra lại bằng hai seed cùng lô sạch. | Con số hai lỗi ban đầu chỉ bao phủ hai loại kiểm tra file. | Chạy validator trên delivery, tự đo bằng scorer chính thức, giữ nguyên log review của nhóm. |
| 4 | khoivancw | ChatGPT/Codex | Gửi ảnh chụp từ viewer COCO và hỏi cách hiểu cảnh báo, loại lỗi và kết luận. | AI suy đoán xe máy từ phần màu cam phía sau bánh xe. Người dùng nhận diện là xe đạp. | Nhóm cần tự đối chiếu vật, box và mask khi xác nhận các dòng review. |
| 5 | khoivancw | ChatGPT/Codex | Viết tool CP5 từ ticket và changelog. | Phải lấy guideline theo job vì metadata từng ảnh có thể lệch. | Đối chiếu trace với scorer và H16 của bộ kiểm. |
| 6 | khoivancw | ChatGPT/Codex | Viết phần bảo mật theo ba tình huống CP6a cho lô r2007. | Phân biệt Hold trong tình huống cần làm mờ với quyết định detection đã ghi ở CP4. | Đối chiếu mẫu, ảnh minh họa đã xem và chạy lại bộ kiểm bàn giao. |
