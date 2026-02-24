# Phân tích thiết kế hệ thống Vietlott Analyzer (SaaS Ready)

## 1. Mục tiêu và phạm vi của hệ thống
- **Mục tiêu cốt lõi:** Tự động thu thập kết quả từ trang web Vietlott, xử lý lưu trữ, cung cấp các biểu đồ thống kê trực quan và ứng dụng mô hình AI (LSTM) để dự đoán xu hướng bộ số.
- **Mục tiêu mở rộng (SaaS Readiness):** Xây dựng nền tảng với kiến trúc linh hoạt, sẵn sàng cho việc thương mại hóa (thu phí người dùng VIP/Premium) khi trải nghiệm cá nhân chứng minh được mức độ hiệu quả của model AI.
- **Phạm vi:** Hệ thống bao gồm một backend dùng API giao tiếp độc lập với hai nền tảng frontend (Web Vue.js và App Flutter đa nền tảng).

## 2. Kiến trúc tổng thể (Scalable Architecture)
- **Tầng thu thập dữ liệu (Crawler):** Một module Python chạy độc lập theo lịch trình (cron job) để truy cập link Vietlott. Kèm theo cơ chế cảnh báo tự động (Telegram Bot) nếu crawler thất bại hoặc website thay đổi cấu trúc.
- **Tầng Backend (Xử lý trung tâm):** Sử dụng Python + FastAPI (hiệu suất cao, hỗ trợ Async). Có tích hợp Auth (JWT) và hệ thống phân quyền (Free/Premium Roles).
- **Tầng Caching (Tối ưu hiệu năng):** Tích hợp Redis để cache các truy vấn tra cứu và thống kê. Khi Public cho nhiều người dùng, Redis sẽ giúp Database không bị quá tải.
- **Tầng AI (Học máy):** Tuân thủ cơ chế Offline Training (huấn luyện định kỳ vào ban đêm) và Online Inference (dự đoán thời gian thực nhẹ nhàng). Tích hợp Feature Engineering để mô hình học tốt hơn.
- **Tầng cơ sở dữ liệu:** PostgreSQL lưu trữ chuỗi thời gian, kết quả dự đoán, dữ liệu thô (raw HTML logs để dự phòng xử lý khi crawler vỡ form) và thông tin người dùng.
- **Tầng Frontend (Giao diện):** 
  - *Web (Vue.js):* Phục vụ tra cứu chi tiết, bảng biểu, đồ thị phức tạp và Dashboard Admin.
  - *App (Flutter):* Trải nghiệm di động mượt mà, giữ chân người chơi (Retention) qua Push notification.
- **Tầng Hạ tầng (DevOps):** Đóng gói bằng Docker và Docker Compose. Dùng Nginx làm Reverse Proxy.

## 3. Thiết kế cơ sở dữ liệu (Lược đồ logic mở rộng)

| Tên bảng | Các trường dữ liệu chính (columns) | Ý nghĩa và chức năng |
|---|---|---|
| `users` | id, email, password_hash, role (free/premium/admin), created_at | Quản lý người dùng và cấp độ truy cập (phục vụ thu phí VIP). |
| `draw_results` | id, draw_date, draw_period, numbers, type, raw_html_log | Lưu kết quả xổ số và HTML thô dự phòng để fix lỗi bóc tách. |
| `number_stats` | id, number, frequency, last_seen, max_gap, current_gap | Thống kê nâng cao (độ gan lỳ của số) làm đặc trưng cho AI. |
| `ai_predictions` | id, target_period, predicted_numbers, confidence, is_premium_only | Lưu dự đoán. Các prediction có confidence > 80% có thể gán nhãn Premium. |
| `user_favorites` | id, user_id, favorite_numbers, notification_enabled | Tính năng user: Lưu "bộ số nuôi/yêu thích" để nhận cảnh báo khi trúng. |

## 4. Thiết kế luồng xử lý nghiệp vụ (Data flow)

- **Luồng cào dữ liệu tự động & Fallback:**
  1. Scheduler kích hoạt hàm crawler lúc 18:30 hàng ngày.
  2. Gửi HTTP GET lấy HTML. 
     - **Nếu lỗi (Timeout/Thay đổi thẻ HTML):** Bắn thông báo Telegram cho Admin.
  3. Bóc tách dữ liệu và lưu cả nguyên bản HTML vào database (để truy xuất sửa lỗi nếu cần).
  4. Ghi kết quả mới vào PostgreSQL và **Flush (xóa) Redis Cache** để API cập nhật số liệu mới nhất.

- **Luồng AI, Feature Engineering & Phân tích chu kỳ:**
  1. Trích xuất khoảng 100 kỳ gần nhất và tính toán đặc trưng bổ sung (Feature Engineering: nhịp độ ra, chẵn lẻ, nhịp gan...).
  2. **[Mới] Phân tích chu kỳ trúng giải:** Đo lường khoảng cách các kỳ từ khi Jackpot nổ đến lần nổ tiếp theo. Thống kê tần suất xuất hiện và tỷ lệ trúng của từng bóng trong chu kỳ này để tìm ra quy luật "nhịp rơi" của các số.
  3. Đưa vào mô hình mạng LSTM (đã được pre-train offline từ trước).
  4. Ghi kết quả dự đoán vào `ai_predictions`.

- **Luồng người dùng (User & Monetization):**
  1. User đăng nhập lấy token JWT (Free plan by default).
  2. 18:35: Hệ thống đẩy FCM Push Notification đến máy các user: *"Đã có kết quả xổ số và Quả cầu AI đã cập nhật số mới, chạm để xem!"*.
  3. Nếu user là Free: Chỉ xem được xác suất 3 con số đầu. Nếu user Premium: Xem full bộ số và độ tin cậy (Confidence).

## 5. Phân tích thiết kế giao diện (UI/UX)
- **Giao diện web (Vue.js):** 
  - Khung nhìn đa dạng để hiển thị biến động số qua các biểu đồ (Line chart, Heatmap) được render bằng ECharts/Chart.js.
  - **Màn hình Phân tích Chu kỳ Giải (Mới):** Cung cấp Dashboard độc lập để xem thống kê theo từng loại giải. Biểu diễn chu kỳ nổ Jackpot, những quả bóng nào ra nhiều nhất và tỷ lệ trúng của chúng trong khoảng thời gian giữa 2 lần có người trúng giải.
  - Tích hợp thêm màn hình Admin để quản lý User và Theo dõi trạng thái của Crawler/AI.
- **Giao diện ứng dụng di động (Flutter):** 
  - Thiết kế Giao diện Premium: Dùng theme tối (Dark mode) kết hợp các dải màu Neon/Hologram để tạo cảm giác "AI và Công nghệ tương lai".
  - Thẻ thông tin (Cards) nổi bật cho bộ số dự đoán.
  - Tích hợp màn hình In-app Purchase/Subscription (Upgrade to Premium) sau này.
