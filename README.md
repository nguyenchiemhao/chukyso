# RSA Digital Signature Demo

Hệ thống demo chữ ký số RSA trên file PDF — bao gồm backend (Python/FastAPI) và frontend (Vue 3) với giao diện trực quan hóa luồng mã hóa.

---

## Mục lục

- [Tổng quan](#tổng-quan)
- [Kiến trúc dự án](#kiến-trúc-dự-án)
- [Yêu cầu hệ thống](#yêu-cầu-hệ-thống)
- [Cài đặt & Chạy](#cài-đặt--chạy)
  - [Backend](#1-backend-pythonfastapi)
  - [Frontend](#2-frontend-vue-3)
- [Chạy CLI demo (không cần web)](#chạy-cli-demo-không-cần-web)
- [API Endpoints](#api-endpoints)
- [Hướng dẫn sử dụng Web App](#hướng-dẫn-sử-dụng-web-app)
- [Lưu ý quan trọng](#lưu-ý-quan-trọng)

---

## Tổng quan

### Chữ ký số là gì?

Chữ ký số là cơ chế dùng **khóa bí mật (private key)** để ký lên dữ liệu và dùng **khóa công khai (public key)** để xác minh:

- Tài liệu có bị sửa sau khi ký hay không (**Integrity**)
- Ai là người đã ký (**Authenticity**)
- Người ký không thể chối bỏ chữ ký (**Non-repudiation**)

### Chữ ký số trên PDF hoạt động thế nào?

```
PDF gốc → Hash (SHA-256) → Ký bằng Private Key (RSA) → Chữ ký số → Nhúng vào PDF
```

1. Ứng dụng tính hash (SHA-256) từ nội dung PDF
2. Hash được ký bằng private key → tạo chữ ký số
3. Chữ ký và thông tin chứng thư được nhúng vào file PDF
4. Người nhận dùng public key trong certificate để xác minh

---

## Kiến trúc dự án

```
chukyso/
├── backend/
│   ├── app.py                  # FastAPI server
│   └── requirements.txt        # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/         # Vue components
│   │   ├── stores/             # Pinia state management
│   │   ├── api.js              # API integration
│   │   ├── App.vue             # Root component
│   │   ├── main.js             # Entry point
│   │   └── style.css           # Global styles + animations
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
├── demo_sign_pdf.py            # CLI: ký PDF
├── demo_verify_pdf.py          # CLI: xác minh PDF
├── demo_tamper_pdf.py          # CLI: tạo bản PDF bị sửa đổi
├── requirements.txt            # Python deps (CLI only)
├── output/
│   ├── certs/                  # Chứng thư & khóa
│   └── pdf/                    # File PDF đầu ra
└── README.md
```

---

## Yêu cầu hệ thống

| Thành phần | Phiên bản tối thiểu |
|---|---|
| Python | 3.9+ |
| Node.js | 18+ |
| npm | 9+ |
| pip | 21+ |

---

## Cài đặt & Chạy

### 1. Backend (Python/FastAPI)

```bash
# Di chuyển vào thư mục dự án
cd chukyso

# (Khuyến nghị) Tạo virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Cài đặt dependencies
pip install -r backend/requirements.txt

# Chạy server
python3 -m uvicorn backend.app:app --reload --port 8000
```

Backend sẽ chạy tại: **http://localhost:8000**

Kiểm tra: `curl http://localhost:8000/api/health` → `{"status":"ok"}`

### 2. Frontend (Vue 3)

Mở terminal mới:

```bash
cd chukyso/frontend

# Cài đặt dependencies
npm install

# Chạy dev server
npm run dev
```

Frontend sẽ chạy tại: **http://localhost:5173**

> Vite proxy tự động chuyển tiếp `/api/*` sang backend `localhost:8000`.

### Build production

```bash
cd frontend
npm run build      # Output: frontend/dist/
npm run preview    # Xem bản build tại localhost:4173
```

---

## Chạy CLI demo (không cần web)

```bash
# Cài thư viện CLI
pip install -r requirements.txt

# Ký PDF
python demo_sign_pdf.py

# Xác minh PDF
python demo_verify_pdf.py
python demo_verify_pdf.py --show-details

# Tạo bản bị sửa đổi (để test INVALID)
python demo_tamper_pdf.py
python demo_verify_pdf.py --pdf output/pdf/tampered_demo.pdf
```

---

## API Endpoints

| Method | Endpoint | Mô tả |
|---|---|---|
| `GET` | `/api/health` | Kiểm tra server |
| `POST` | `/api/generate-keys` | Tạo cặp khóa RSA-2048 + certificate |
| `POST` | `/api/upload` | Upload file PDF, trả về SHA-256 hash |
| `POST` | `/api/sign` | Ký PDF bằng pyHanko |
| `POST` | `/api/verify` | Xác minh chữ ký PDF |
| `GET` | `/api/download/{id}` | Tải file PDF đã ký |
| `POST` | `/api/tamper` | Tạo bản PDF bị sửa đổi (demo) |

---

## Lưu ý quan trọng

- Đây là **demo học tập**, dùng certificate tự ký (self-signed).
- Khi mở PDF đã ký, trình đọc có thể báo người ký **chưa được tin cậy**.
- Trong hệ thống thật, bạn thường dùng USB token, HSM, smart card, hoặc certificate do CA hợp lệ cấp.
- Không sử dụng cho mục đích production.
