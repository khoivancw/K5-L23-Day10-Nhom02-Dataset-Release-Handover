# Bảo mật khi bàn giao lô r2007 của nhóm 02

## 1. Hết giờ khi đang kiểm tra lô

Nếu chưa xem xong hàng đợi, em lưu nhận xét đã hoàn tất trên máy làm việc, ghi lại mã ảnh đang xem rồi báo người phụ trách để tiếp tục trong ca sau. Chép ZIP ra USB hoặc gửi qua email cá nhân sẽ tạo một bản sao ảnh và nhãn bên ngoài nơi được phép lưu. Nhờ bạn làm hộ còn khiến người ngoài job nhìn thấy dữ liệu và làm sai tên người kiểm trong nhật ký. Nếu cần đổi ca, em đề nghị người phụ trách giao lại job cho người có tài khoản riêng.

## 2. Năm thao tác trong ca làm việc

| Thao tác | Quyết định | Lý do |
|---|---|---|
| Mở job được giao trên máy công ty | Được | Em dùng tài khoản của mình để xem đúng các ảnh được phân công và lưu nhận xét dưới tên mình. |
| Chụp màn hình gửi người quen | Không | Một ảnh chụp viewer có thể lộ cả khuôn mặt, mã ảnh và nhãn. Khi cần hỗ trợ, em gửi mã ảnh qua kênh dự án cho người có quyền xem. |
| Chép lô ra USB cá nhân | Không | Sau khi USB rời máy, nhóm khó kiểm soát ai giữ bản sao và bản đó còn được lưu ở đâu. |
| Dán nhãn thật của dự án lên chatbot bên ngoài | Không | Tọa độ, tên lớp và mã ảnh cũng là dữ liệu dự án. Em dùng ví dụ tự tạo nếu cần hỏi cách đọc định dạng. |
| Đưa tài khoản CVAT cho đồng nghiệp | Không | Thao tác của người khác sẽ mang tên em. Đồng nghiệp cần dùng tài khoản riêng và được cấp đúng job. |

## 3. Ca khuôn mặt khi guideline yêu cầu làm mờ

Ảnh 000000021167 trong lô r2007 cho thấy rõ mặt hai người đứng cạnh nhau. Nếu áp dụng guideline yêu cầu làm mờ trong tình huống này, em đặt lô ở trạng thái **Hold**, dừng gửi gói và báo trưởng nhóm cùng người phụ trách dữ liệu qua kênh dự án. Em nêu mã ảnh và release để họ mở đúng bản, xác định phạm vi cần rà và giao người xử lý. Dù ảnh đã mở được và đã kiểm lại SHA-256, việc đó chỉ xác nhận tình trạng file. Tự làm mờ sẽ thay đổi nội dung và mã băm, còn tự xoá khiến ảnh, nhãn và manifest mất đồng bộ. Sau khi người được giao xử lý tạo bản mới, nhóm kiểm lại khuôn mặt, nhãn và manifest trước khi đề nghị phát hành.
