# Vietlott Analyzer (SaaS) Implementation Plan

## Goal
Xây dựng nền tảng SaaS dự đoán Vietlott bao gồm Crawler tự động, API Backend (FastAPI + AI LSTM), Web App (Vue.js) và Mobile App (Flutter) với cơ chế phân quyền Free/Premium.

## Tasks

- [ ] Task 1: Thiết lập Database & Caching
  - Action: Khởi tạo PostgreSQL (các bảng users, draw_results, number_stats, ai_predictions) và Redis.
  - Verify: Kết nối thành công DB qua DataGrip/DBeaver, set/get key thử trên Redis CLI.

- [ ] Task 2: Xây dựng Core API (FastAPI) & Auth
  - Action: Setup dự án FastAPI, tích hợp JWT Authentication, phân quyền Free/Premium.
  - Verify: API `/login` trả về JWT token, API yêu cầu quyền Premium chặn Free user trả mã 403.

- [ ] Task 3: Phát triển Crawler & Fallback
  - Action: Viết script Python cào dữ liệu Vietlott, setup Cronjob chạy lúc 18:30, tích hợp gửi lỗi qua Telegram Bot.
  - Verify: Chạy script lấy thành công kết quả mới nhất lưu vào DB và raw HTML, giả lập lỗi để check tin nhắn Telegram.

- [ ] Task 4: Tích hợp AI (LSTM Inference)
  - Action: Viết luồng load mô hình LSTM pre-train, lấy dữ liệu 100 kỳ gần nhất tính toán Feature Engineering và sinh dự đoán.
  - Verify: Chạy script AI sinh ra bộ số dự đoán mới ghi vào bảng `ai_predictions`.

- [ ] Task 5: Xây dựng Web App Admin & User (Vue.js)
  - Action: Setup Vue 3 + Tailwind/ECharts. Làm màn hình tra cứu lịch sử, màn Admin quản lý và **Màn hình thống kê theo từng loại giải** (phân tích chu kỳ nổ Jackpot từ kỳ có người trúng đến kỳ có người trúng tiếp theo, đo lường tần suất bóng và tỷ lệ trúng trong chu kỳ này).
  - Verify: Đăng nhập thành công trên Web, render biểu đồ lịch sử Vietlott và báo cáo chu kỳ giải thưởng từ API.

- [ ] Task 6: Xây dựng Mobile App (Flutter)
  - Action: Setup Flutter project, giao diện Dark/Neon theme hiển thị thẻ bộ số AI, tích hợp Firebase Cloud Messaging (FCM).
  - Verify: App build thành công trên Simulator, nhận được notification "Có kết quả mới".

## Done When
- [ ] Backend API chạy ổn định, tự động cào dữ liệu lúc 18:30 không lỗi.
- [ ] AI sinh dự đoán mới hàng ngày dựa trên dữ liệu cập nhật.
- [ ] User có thể đăng nhập Web/App để xem kết quả và dự đoán tùy theo gói Free hay Premium.
- [ ] Hệ thống chịu tải tốt nhờ Redis Cache cache các truy vấn tra cứu.
