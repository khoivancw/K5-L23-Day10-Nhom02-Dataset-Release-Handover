Release: lab250_1aa4ca8dd833_v2
Parent: lab250_1aa4ca8dd833
Số ảnh: 243
Số nhãn: 1664
Guideline: Theo jobs.csv, ghi theo từng ảnh trong truyvet.csv.
QC v1: 17/250 = 6.8%
Kết luận v1: Hold - tỷ lệ lỗi vượt ngưỡng 2%.
Kết luận v2: Release - bàn giao nhãn detection sau khi tách 7 ảnh sang rework.
Ghi chú: Mỗi cảnh theo split đa số của v1. Dùng guideline của job. Hai ảnh lệch hash đã mở kiểm tra và tính SHA-256 mới trong manifest.csv. Xem rework_queue.csv để biết người gán và người kiểm từng ảnh. Các ảnh giữ trong v2 cần báo nhóm panoptic: 000000005992 (thing_overlap), 000000011760 (thing_overlap), 000000013177 (category_swap), 000000017379 (category_swap), 000000025057 (invalid_category_id).
