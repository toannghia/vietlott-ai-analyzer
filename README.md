# Vietlott AI Analyzer 🚀

Hệ thống phân tích và dự báo kết quả xổ số Vietlott (Mega 6/45 & Power 6/55) sử dụng trí tuệ nhân tạo (Ensemble Learning). Nền tảng cung cấp bộ công cụ toàn diện từ tự động cập nhật dữ liệu, phân tích thống kê chuyên sâu đến đưa ra các bộ số tiềm năng nhất với độ tin cậy cao.

---

## 🌟 Tính năng nổi bật

### 1. Siêu máy tính dự báo (AI Ensemble)
Sử dụng kiến trúc **Ensemble Learning** kết hợp 3 mô hình học máy hiện đại để tối ưu hóa kết quả:
- **LSTM (RNN):** Học sâu chuỗi thời gian để phát hiện quy luật dài hạn.
- **Random Forest:** Phân tích các đặc trưng phi tuyến như tổng bóng, tỷ lệ chẵn/lẻ, và khoảng cách nhịp rơi.
- **Markov Chain:** Tính toán xác suất chuyển đổi trạng thái giữa các con số.
- **Top 3 Bộ số:** Hệ thống tự động đề xuất 3 bộ số tiềm năng nhất kèm theo mức độ tự tin (Confidence Score).

### 2. Tự động hóa hoàn toàn (Auto-Crawler)
- Hệ thống Crawler tự động lấy kết quả trực tiếp từ Vietlott ngay sau giờ quay thưởng (18:30 hàng ngày).
- Cơ chế kiểm soát lỗi và ghi log chi tiết, đảm bảo dữ liệu luôn chính xác và mới nhất.

### 3. Dashboard Phân tích Chuyên sâu
- **Biểu đồ biến động:** Theo dõi độ tin cậy của AI qua từng kỳ quay.
- **Thống kê thông minh:** Tần suất xuất hiện, cặp số hay về cùng nhau, các bóng lâu chưa ra (Cold Numbers).
- **Lịch sử đối chiếu:** Xem lại các dự báo cũ và so khớp trực quan với kết quả thực tế. Các bóng trúng thưởng được làm nổi bật sang trọng.

### 4. Quản lý người dùng & Phân quyền
- Hệ thống Admin quản lý tài khoản chuyên nghiệp.
- Phân quyền người dùng (Free/Premium) để cá nhân hóa trải nghiệm và nội dung dự báo.

---

## 🛠 Công nghệ sử dụng

### Backend (Lõi xử lý)
- **Framework:** FastAPI (Python 3.10+)
- **AI/ML:** TensorFlow (Keras), Scikit-learn, NumPy.
- **Database:** PostgreSQL (Lưu trữ kết quả và dự báo).
- **ORM:** SQLAlchemy (Async).

### Frontend (Giao diện)
- **Framework:** React 19 + Vite.
- **Styling:** Tailwind CSS (Modern Glassmorphism Design).
- **Biểu đồ:** Recharts.
- **Icons:** Lucide React.

### Infrastructure
- **Deployment:** Docker & Docker Compose.

---

## 📸 Hình ảnh minh họa

### Giao diện Dashboard & Dự báo Ensemble
![Dashboard Ensemble](/Users/macbook/.gemini/antigravity/brain/50c55ebe-99ad-4db1-87ff-e23e03dc6f96/final_ensemble_sets_all_1771889974397.png)

### Đối chiếu kết quả lịch sử
![History Viewer](/Users/macbook/.gemini/antigravity/brain/50c55ebe-99ad-4db1-87ff-e23e03dc6f96/dashboard_prediction_history_01474_1771859184137.png)

### Quản lý người dùng
![User Management](/Users/macbook/.gemini/antigravity/brain/50c55ebe-99ad-4db1-87ff-e23e03dc6f96/admin_users_topbar_1771840587140.png)

---

## 🚀 Hướng dẫn cài đặt (Docker)

### 1. Chuẩn bị
- Đã cài đặt Docker và Docker Compose.
- Clone mã nguồn về máy.

### 2. Khởi chạy hệ thống
Tại thư mục gốc của dự án, chạy lệnh:
```bash
docker-compose up -d --build
```

### 3. Truy cập
- **Web UI:** [http://localhost:3000](http://localhost:3000)
- **API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

### 4. Tài khoản mặc định
- **Email:** `admin@zenpos.vn`
- **Password:** `[PASSWORD]`

---

## 📂 Cấu trúc thư mục chính
- `backend/`: Chứa mã nguồn API, models và service.
- `backend/ml/`: Chứa các script huấn luyện và lưu trữ mô hình AI.
- `Web/admin-ui/`: Mã nguồn giao diện React.
- `docker-compose.yml`: File cấu hình vcontainer hóa toàn bộ hệ thống.

---

## ⚖️ License
Dự án được phát triển cho mục đích nghiên cứu và tham khảo kỹ thuật. 
Phát triển bởi đội ngũ **ZenPOS Architecture**.
