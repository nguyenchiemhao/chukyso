# Hướng dẫn sử dụng — RSA Digital Signature Demo

Tài liệu này hướng dẫn chi tiết cách sử dụng ứng dụng web demo chữ ký số RSA từng bước.

---

## Mục lục

1. [Truy cập ứng dụng](#1-truy-cập-ứng-dụng)
2. [Tạo cặp khóa RSA](#2-tạo-cặp-khóa-rsa)
3. [Upload file PDF](#3-upload-file-pdf)
4. [Ký file PDF](#4-ký-file-pdf)
5. [Tải file PDF đã ký](#5-tải-file-pdf-đã-ký)
6. [Xác minh chữ ký](#6-xác-minh-chữ-ký)
7. [Giải thích giao diện](#7-giải-thích-giao-diện)
8. [Câu hỏi thường gặp](#8-câu-hỏi-thường-gặp)

---

## 1. Truy cập ứng dụng

Đảm bảo cả backend và frontend đã chạy (xem `README.md`), sau đó mở trình duyệt:

```
http://localhost:5173
```

Giao diện gồm 3 phần chính:

| Vùng | Vị trí | Chức năng |
|---|---|---|
| **Progress Bar** | Trên cùng | Hiển thị tiến trình: Upload → Hash → Sign → Attach |
| **Action Panel** | Bên trái | Upload PDF, tạo khóa, nút Ký & Xác minh |
| **Visualization Panel** | Bên phải | Luồng mã hóa trực quan, kết quả đầu ra |

---

## 2. Tạo cặp khóa RSA

> ⚠️ **Bước bắt buộc** — phải tạo khóa trước khi ký hoặc xác minh.

1. Ở panel bên trái, nhấn nút **"Generate RSA Key Pair"**
2. Chờ hệ thống tạo khóa (vài giây)
3. Sau khi hoàn tất, bạn sẽ thấy:
   - **Public Key (Verification)** — hiển thị đầy đủ, dùng để xác minh
   - **Private Key (Signing)** — ẩn mặc định, nhấn 👁 để hiện/ẩn

### Lưu ý:
- Mỗi lần nhấn "Generate" sẽ tạo cặp khóa **mới hoàn toàn**
- Cặp khóa cũ sẽ không sử dụng được nữa cho lần ký/xác minh tiếp theo
- Khóa dùng thuật toán **RSA-2048** với certificate tự ký

---

## 3. Upload file PDF

1. Kéo thả file PDF vào vùng "Drop PDF here" **hoặc** nhấn vào vùng đó để chọn file
2. Hệ thống sẽ:
   - Upload file lên server
   - Tính hash **SHA-256** của file
   - Hiển thị tên file và dung lượng
3. Thanh progress bar sẽ chuyển sang bước **"Hash (SHA-256)"**

### Yêu cầu file:
- Định dạng: chỉ chấp nhận `.pdf`
- Kích thước tối đa: **10 MB**

### Muốn đổi file?
- Nhấn link **"Remove"** bên dưới tên file để xóa và upload file khác

---

## 4. Ký file PDF

> ⚠️ Cần đã hoàn thành bước 2 (Tạo khóa) và bước 3 (Upload PDF).

1. Nhấn nút **"Sign PDF Document"** (nút xanh dương)
2. Quan sát Visualization Panel bên phải — luồng ký sẽ hiển thị từng bước:

   ```
   📄 Original File → 🔐 HASHING... → 📝 Digital Digest → ✅ Attached
   ```

3. Quá trình ký diễn ra:
   - **Bước 1**: Hash file PDF gốc bằng SHA-256
   - **Bước 2**: Mã hóa hash bằng Private Key (RSA-2048)
   - **Bước 3**: Nhúng chữ ký vào file PDF

4. Sau khi ký xong:
   - Panel **"Signed Output"** hiển thị file đã ký
   - Visualization hiển thị giá trị hash và signature preview

---

## 5. Tải file PDF đã ký

1. Ở phần **"Signed Output"** (dưới bên trái của visualization)
2. Nhấn biểu tượng **⬇ Download**
3. File PDF đã ký sẽ được tải về máy

---

## 6. Xác minh chữ ký

> ⚠️ Cần đã tạo khóa (bước 2). File xác minh phải được ký bằng **đúng cặp khóa hiện tại**.

1. Nhấn nút **"Verify Signature"** (nút xanh lá)
2. Hệ thống sẽ mở hộp thoại chọn file — chọn file PDF đã ký
3. Chờ kết quả xác minh

### Kết quả:

| Kết quả | Hiển thị | Ý nghĩa |
|---|---|---|
| ✅ **VALID SIGNATURE** | Viền xanh lá, biểu tượng ✓ | Chữ ký hợp lệ, file chưa bị sửa đổi |
| ❌ **INVALID SIGNATURE** | Viền đỏ, biểu tượng ✗ | Chữ ký không hợp lệ hoặc file đã bị thay đổi |

### Thông tin chi tiết hiển thị:
- **Signer** — tên người ký
- **Hash** — thuật toán hash đã dùng
- **Mechanism** — cơ chế chữ ký (vd: RSA with SHA-256)
- **Signed at** — thời điểm ký

### Thử nghiệm INVALID:
Để demo trường hợp chữ ký không hợp lệ, bạn có thể:
- Mở file PDF đã ký bằng trình soạn thảo hex và sửa 1 byte bất kỳ
- Hoặc dùng API `/api/tamper` để tạo bản bị sửa tự động
- Upload bản đã sửa vào phần Verify → kết quả sẽ là **INVALID**

---

## 7. Giải thích giao diện

### Progress Bar (thanh tiến trình)

```
[Upload PDF] → [Hash SHA-256] → [RSA Signing] → [Attach Signature]
     ●              ●                ●                  ●
```

- Bước đang thực hiện: vòng tròn **xanh dương** có hiệu ứng nhấp nháy
- Bước đã hoàn thành: vòng tròn **xanh dương** đặc
- Bước chưa đến: vòng tròn **xám** mờ

### Visual Cryptography Flow

Hiển thị trực quan luồng mã hóa:

```
┌──────────────┐          ┌──────────────────┐
│ Original File │  ════►  │  Digital Digest   │
│   (PDF gốc)  │ HASHING │  (SHA-256 hash)   │
└──────────────┘          │  + Signature      │
                          │  (RSA encrypted)  │
                          └──────────────────┘
```

- **Original File**: icon tài liệu, hiển thị tên file khi đã upload
- **Digital Digest**: giá trị hash rút gọn (16 ký tự đầu)
- **Signature Preview**: giá trị chữ ký (hex) khi đã ký xong
- **Biểu tượng 🔒 + 🔑**: cho biết trạng thái sử dụng private key

### Ba thuộc tính bảo mật

| Thuộc tính | Icon | Giải thích |
|---|---|---|
| **Integrity** | 🛡️ | Hash đảm bảo dữ liệu không bị sửa đổi |
| **Authenticity** | 👤 | Private key chứng minh nguồn gốc tài liệu |
| **Non-repudiation** | 📜 | Người ký không thể chối bỏ chữ ký |

---

## 8. Câu hỏi thường gặp

### Q: Tại sao cần tạo khóa trước khi ký?
**A:** Chữ ký số RSA yêu cầu cặp khóa bất đối xứng. Private key dùng để ký, public key (trong certificate) dùng để xác minh. Không có khóa thì không thể thực hiện quy trình.

### Q: Tôi có thể dùng khóa của lần trước không?
**A:** Trong phiên hiện tại, bạn có thể dùng lại khóa đã tạo. Nhưng nếu đã nhấn "Generate" lần nữa, cặp khóa cũ không còn khả dụng.

### Q: File PDF gốc có bị thay đổi không?
**A:** Không. Hệ thống tạo một file PDF **mới** (signed copy) chứa chữ ký. File gốc không bị sửa.

### Q: Tại sao trình đọc PDF báo "chữ ký chưa được tin cậy"?
**A:** Đây là demo dùng certificate **tự ký** (self-signed), không được cấp bởi CA uy tín. Trong hệ thống thật, bạn cần certificate do CA hợp lệ cấp phát.

### Q: Hỗ trợ file nào ngoài PDF?
**A:** Hiện tại chỉ hỗ trợ file PDF. Đây là định dạng phổ biến nhất cho chữ ký số.

### Q: Có giới hạn kích thước file không?
**A:** Tối đa **10 MB** cho mỗi file upload.

---

## Luồng sử dụng mẫu (Quick Start)

```
1. Mở http://localhost:5173
2. Nhấn "Generate RSA Key Pair"        → Tạo khóa
3. Kéo thả file PDF vào drop zone      → Upload
4. Nhấn "Sign PDF Document"            → Ký (xem animation)
5. Nhấn ⬇ Download ở Signed Output     → Tải file đã ký
6. Nhấn "Verify Signature"             → Chọn file đã ký
7. Xem kết quả: VALID ✅ hoặc INVALID ❌
```
