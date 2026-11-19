# Báo cáo nhóm 02 — Bàn giao và truy vết dữ liệu, Lab Day 10

Nhóm kiểm tra lô 250 ảnh của seed 2007, đối chiếu khung phát hiện vật thể (box) với vùng phân đoạn (mask), rồi bàn giao bản v2 cho team AI dùng cho bài toán detection.

## 1. Số liệu luyện tập

| Seed | Kết quả đưa vào chấm | F1 lỗi luật | F1 lỗi gán nhãn | F1 tổng |
|---|---|---:|---:|---:|
| 2007 | 11 lỗi luật và 6 lỗi gán nhãn nhóm xác nhận | ≈ 1,0 | ≈ 0,7 | ≈ 0,9 |
| 2008 | 12 lỗi luật, chỉ chạy phần kiểm tự động | ≈ 1,0 | Chưa đánh giá | ≈ 0,8 |

Các điểm trên do `score_findings.py` làm tròn. Trên lô sạch 50 ảnh, validator báo 0 lỗi luật và đưa 2 ảnh vào hàng đợi xem bằng mắt. Trên seed 2007, hàng đợi có 10 ảnh trong tổng số 250 ảnh.

Để chọn ảnh cần xem, tool xét cả độ chồng giữa hai khung (IoU) và tỉ lệ điểm mask nằm trong box. Ví dụ, để gợi ý sai tên lớp, tool yêu cầu IoU ≥ 0,65, box chứa ít nhất 75% số điểm mask lấy mẫu và không có box cùng lớp khớp với mask ở IoU ≥ 0,55. Các điều kiện này giúp ưu tiên những cặp có khả năng đang mô tả cùng một vật. Nhóm kiểm tra độ nhiễu bằng lô sạch và dùng ảnh để quyết định các trường hợp còn nghi vấn. Hai cảnh báo trên lô sạch cho thấy độ lệch tự nhiên giữa box và mask vẫn có thể kích hoạt luật gợi ý.

## 2. Vì sao cần xem lại các cảnh báo?

Trong 10 ảnh nghi vấn, nhóm xác nhận 6 và bác 4 cảnh báo gộp nhầm hai vật vào một mask (`instance_merge`). Ví dụ, ở ảnh `000000013923`, viền mask bám theo ghế đỏ. Khung của ghế gỗ phía sau cũng bao một phần vùng này vì hai ghế che nhau. Việc mask xuất hiện trong cả hai khung chưa đủ để kết luận hai ghế bị gộp.

Nếu ghi cả 10 cảnh báo thành lỗi, danh sách sẽ có thêm 4 trường hợp mà bằng chứng trong ảnh không ủng hộ. Báo thừa làm giảm độ chính xác của danh sách lỗi (precision) và có thể kéo F1 xuống. Con số 6/10 là tỉ lệ nhóm xác nhận khi review. Điểm F1 lỗi gán nhãn ≈ 0,7 còn tính cả lỗi bỏ sót và yêu cầu xác định đúng loại lỗi.

## 3. Quyết định giữ v1 và bàn giao v2

Lô v1 có 17 mục lỗi trên 250 ảnh, tương đương 6,8% theo cách tính của lab, vượt ngưỡng 2%. Nhóm ghi quyết định **HOLD** cho `lab250_1aa4ca8dd833`. Truy vấn lịch sử trả về `R-021: affected=True action=review_or_retrain`. Lượt train mô phỏng này đã dùng v1, nên team AI cần đánh giá lại mô hình và cân nhắc train lại với dữ liệu đã xử lý.

Bản v2 bàn giao **243 ảnh và 1.664 nhãn detection**. Nhóm tách 7 ảnh cần sửa nhãn sang `rework_queue.csv`, kèm người gán và người kiểm theo job. Năm ảnh chỉ có lỗi panoptic vẫn dùng được cho detection và đã được liệt kê trong README để báo nhóm phụ trách mask. Kiểm tra bàn giao đạt 17/17 mục. [README của lô v2](r2007/handover/lab250_1aa4ca8dd833_v2/README.txt)

## 4. SHA-256 cho biết điều gì?

Bên nhận có thể tính lại SHA-256 và so với giá trị đã ghi trong manifest để phát hiện file có nội dung khác bản kê. Hai ảnh `000000013659` và `000000021167` vẫn mở được dù validator báo lệch hash. Sau khi kiểm tra ảnh, nhóm ghi hash thực tế vào manifest mới. Bộ kiểm xác nhận đủ 486 file của v2, gồm 243 ảnh và 243 file nhãn.

SHA-256 không đánh giá ý nghĩa của nhãn. Chẳng hạn, ở ảnh `000000017379`, mask của chiếc TV treo tường mang nhãn `laptop`. File chứa nhãn sai vẫn có thể khớp hoàn toàn với hash đã ghi; phát hiện lỗi này cần đối chiếu vật thật với nhãn.

## 5. Truy vết ticket xe tải

Team AI báo bỏ sót xe tải bị che hoặc ở mép ảnh trong hai cảnh `scene_269` và `scene_661`. Guideline v1.2 cho phép bỏ qua các trường hợp nêu trong changelog; v1.3 yêu cầu vẽ khung. Nhóm lọc các ảnh có ít nhất một box `truck` và thuộc job dùng v1.2. Phiên bản hướng dẫn được tra từ `jobs.csv` vì trường guideline trên từng ảnh có thể ghi sai.

| Nhóm | Kết quả | Việc cần làm |
|---|---|---|
| tier_a | 000000006040, 000000006723 | Rà trước hai ảnh trong các cảnh ticket nêu. |
| tier_b | 000000000724, 000000001532, 000000007088, 000000007386 | Rà thêm bốn ảnh có cùng điều kiện ở cảnh khác. |
| notify | A02, Q01, Q03 | Báo người gán và người kiểm của các job liên quan. |

Sáu ảnh trên là phạm vi cần rà lại. Muốn xác nhận thiếu box xe tải vẫn phải xem từng ảnh. Bộ chấm trả F1 ≈ 1,0 cho cả ba danh sách. [Kết quả truy vết](r2007/trace.json)

## 6. Điểm cần lưu ý khi dùng tool

Ở ảnh `000000013177`, box ghi `bicycle`, mask ghi `motorcycle`. Người xem xác định vật là xe đạp. Lúc đầu ô loại lỗi lưu `class_swap` dù nhận xét mô tả box đúng và mask sai. Nhóm đã đối chiếu hai trường và sửa mã thành `category_swap` trước khi đóng gói. Chi tiết này quyết định ảnh có được giữ trong v2 hay phải chuyển sang gán lại. [Nhật ký review](r2007/review_log.csv)
