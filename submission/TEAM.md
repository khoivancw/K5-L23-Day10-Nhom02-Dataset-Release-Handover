# Nhóm 02

- Seed luyện tập: <2007>
- Repo: <https://github.com/khoivancw/K5-L23-Day10-Nhom02-Dataset-Release-Handover>

| Họ và tên | MSHV | Tài khoản GitHub | Phần chính |
|---|---|---|---|
| Lê Văn Khởi | 2A202603290 | @khoivancw | Phụ trách validator lõi: missing_image, wrong_hash, invalid_class, bbox_out_of_bounds và duplicate_box; tích hợp toàn bộ luật kiểm tra vào CLI; đóng gói bàn giao v2 gồm ảnh, nhãn, manifest, SHA-256, label_summary, rework_queue, truyvet và README; ghi log hỗ trợ AI cho validator và công cụ review trong prompts.md |
| Vũ Hoàng Nam | 2A202603268 | @hoangnam312 | Viết validator phát hiện scene_leak, guideline_mismatch, invalid_category_id và thing_overlap; phối hợp với Khởi kiểm tra phần tích hợp, phụ trách kiểm thử lỗi luật trên nhiều seed và lô sạch |
| Hoàng Quốc Mạnh | 2A202603219 | @quocmanh0502 | Viết phần đối chiếu detection–panoptic, xuất candidates.json; đo ứng viên trên lô sạch và ghi lý do chọn ngưỡng |
| Vũ Tiến Vinh | 2A202603269 | @TienVinh03 | Làm công cụ xem ảnh có box và segment; chia hàng đợi cho 6 người, tổng hợp review_log.csv và kiểm tra ghi chú review |
| Nguyễn Mạnh Dũng | 2A202603197 | @ngmanhdungg | Lead: cập nhật TEAM.md và điều phối tiến độ; đối chiếu review_log.csv, tổng hợp errors.json từ lỗi luật và review đã xác nhận; ghi quyết định QC và lineage; phối hợp kiểm tra gói bàn giao v2 do Khởi đóng gói; tổng hợp REPORT.md, bổ sung và hoàn thiện prompts.md từ log của Khởi, kiểm tra bài nộp |
| Đỗ Tuấn Long | 2A202604066 | @superuj-coder | Đọc ticket và changelog guideline, lập trace.json gồm tier_a, tier_b, notify; hoàn thành security.md |
