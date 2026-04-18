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
   - **Public Key (Verification)** ✓ Công khai — dùng để xác minh chữ ký
   - **Private Key (Signing)** 🔒 Bí mật — dùng để tạo chữ ký, giấu kín

### 💡 Public Key vs Private Key — Sự khác biệt là gì?

**Private Key (Khóa bí mật) — Chỉ bạn có**
- ⚠️ Giữ bí mật, không chia sẻ với ai
- 🔐 Dùng để **SIGN** — tạo chữ ký lên tài liệu
- Nếu bị lộ, người khác có thể giả mạo chữ ký của bạn

**Public Key (Khóa công khai) — Ai cũng có thể biết**
- ✓ An toàn để chia sẻ công khai
- 🔓 Dùng để **VERIFY** — kiểm tra chữ ký của bạn
- Mọi người dùng key này để xác minh chữ ký đều của bạn

**Ví dụ thực tế:**
- Private Key = Chữ ký tay của bạn trên hợp đồng (chỉ bạn biết dấu)
- Public Key = Ảnh/bản sao chữ ký bạn in ra để mọi người đối chiếu

**Quy trình:**
```
BẠN LÝ:                    NGƯỜI KIỂM TRA:
┌─────────────┐            ┌──────────────────┐
│ File PDF    │            │ File PDF đã ký   │
│    ↓        │            │      ↓           │
│ Private Key │   ====>    │ Public Key       │
│    ↓        │            │      ↓           │
│  Ký lên     │            │  So sánh         │
│  (SIGN)     │            │  (VERIFY)        │
└─────────────┘            └──────────────────┘
     ✅                          ✅ VALID or ❌ INVALID
```

### Lưu ý:
- Mỗi lần nhấn "Generate" sẽ tạo cặp khóa **mới hoàn toàn**
- Cặp khóa cũ sẽ không sử dụng được nữa cho lần ký/xác minh tiếp theo
- Khóa dùng thuật toán **RSA-2048** với certificate tự ký
- **Luôn giữ private key bí mật**; public key có thể chia sẻ tự do

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

## 6.1 Chia sẻ Public Key để người khác xác minh

**Kịch bản:** Bạn muốn gửi file PDF đã ký cho bạn A. Bạn A muốn xác minh rằng file đó thực sự do bạn ký.

**Cách làm:**

### Bạn (người ký) gửi:
1. Ở panel bên trái, nhấn nút **"Generate RSA Key Pair"**
2. Sau khi tạo khóa, bạn sẽ thấy **Public Key** (xanh dương)
3. Nhấn nút **Copy** để sao chép public key
4. **Chia sẻ công khai** public key này cho bạn A (email, messenger, etc.)
5. Ký PDF và **Tải file đã ký** xuống
6. Gửi file đã ký cho bạn A

### Bạn A (người kiểm tra) làm:
1. **Nhận**: File PDF đã ký + **Public Key** của bạn
2. **Truy cập ứng dụng**: Mở http://localhost:5173
3. **Tạo session mới**: Nhấn "Generate RSA Key Pair" để tạo session (không ảnh hưởng đến xác minh)
4. **Xác minh file**:
    - Cuộn xuống section **"Verify with External Public Key:"** (phía dưới)
    - **Dán public key** mà bạn gửi vào textarea
       - Public key phải bắt đầu với: `-----BEGIN PUBLIC KEY-----`
       - Và kết thúc với: `-----END PUBLIC KEY-----`
    - Có thể nhấn **"Use My Current Public Key"** nếu muốn test với key hiện tại của session
    - Nhấn **"Verify with This Public Key"**
   - Chọn file PDF mà bạn gửi
5. **Xem kết quả:**
   - ✅ **VALID SIGNATURE** → File thật, bạn đã ký, không ai sửa đổi
   - ❌ **INVALID SIGNATURE** → File bị giả mạo hoặc sửa đổi
   - ⚠️ Nếu báo **Request failed (400)**: Hãy kiểm tra:
       - Đã paste đầy đủ public key? (bắt đầu với `-----BEGIN PUBLIC KEY-----` và kết thúc với `-----END PUBLIC KEY-----`)
     - Không có dòng trống hoặc ký tự lạ ở đầu/cuối?

**Ví dụ Public Key format:**
```
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQE...
[... nhiều dòng nữa ...]
-----END PUBLIC KEY-----
```

**Lưu ý:**
- ✓ Ứng dụng external verify chỉ nhận **PUBLIC KEY**
- ✓ Có thể verify nhiều file từ cùng một người nếu dùng đúng public key của người đó
- ⚠️ Nếu dán certificate hoặc private key, hệ thống sẽ báo lỗi định dạng

**Ví dụ thực tế:**

```
Bạn (Người ký):
├─ Generate key → có PUBLIC KEY
├─ Nhấn Copy → sao chép key
├─ Gửi: "Đây là public key của tôi:" + (paste key từ clipboard)
├─ Sign PDF → file.pdf.signed
└─ Gửi file.pdf.signed cho bạn A

Bạn A (Người kiểm tra):
├─ Nhận file + public key
├─ Mở app (session mới)
├─ Paste public key vào "Verify with External Public Key"
├─ Nhấn "Verify with This Public Key"
└─ Chọn file PDF đã ký để kiểm tra
```

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

### Q: Private Key và Public Key khác nhau như thế nào?
**A:**
- **Private Key** (Khóa bí mật): Chỉ bạn có, dùng để ký. Giống chữ ký tay của bạn.
- **Public Key** (Khóa công khai): Ai cũng có, dùng để xác minh chữ ký. Giống ảnh/mẫu chữ ký để mọi người đối chiếu.

**Nguyên tắc quan trọng:**
- Private key phải **giữ bí mật**
- Public key có thể **chia sẻ công khai**

### Q: Tôi có thể dùng khóa của lần trước không?
**A:** Trong phiên hiện tại, bạn có thể dùng lại khóa đã tạo. Nhưng nếu đã nhấn "Generate" lần nữa, cặp khóa cũ không còn khả dụng.

### Q: Nếu tôi muốn xác minh file ký bởi người khác thì sao?
**A:** Sử dụng mục **"Verify with Different Public Key"** ở cuối panel bên trái:
1. Dán public key của person khác vào textbox
2. Nhấn "Verify with This Key"
3. Chọn file PDF họ ký
4. Nếu valid → file thật, nếu invalid → bị sửa đổi

### Q: Public key của người khác là gì?
**A:** Là tệp text chứa certificate hoặc public key của họ. Thường có giá dạng:
```
-----BEGIN CERTIFICATE-----
MIIBkTCB+wIJAKHHChYPxxxxx...
-----END CERTIFICATE-----
```

Họ có thể copy từ nút "Copy" bên cạnh Public Key của họ.

### Q: Nếu file bị sửa đổi sau khi ký thì sao?
**A:** Sẽ báo **INVALID SIGNATURE** vì hash không khớp nữa.

### Q: Gặp lỗi "This endpoint verifies with PUBLIC KEY..." hoặc lỗi 400 khi verify external?
**A:** Lỗi này xuất hiện khi bạn dán sai định dạng key. External verify chỉ nhận **PUBLIC KEY**.

**Định dạng đúng:**
- Bắt đầu: `-----BEGIN PUBLIC KEY-----`
- Kết thúc: `-----END PUBLIC KEY-----`

**Không hợp lệ:**
- `-----BEGIN CERTIFICATE-----`
- `-----BEGIN PRIVATE KEY-----`

**Cách sửa:**
1. Người ký nhấn nút **Copy** ở phần Public Key.
2. Paste key vào ô **Verify with External Public Key**.
3. Đảm bảo không thiếu dòng BEGIN/END và không có ký tự lạ ở đầu/cuối.

### Q: Làm sao biết public key nào của người nào?
**A:**
- Người ký phải gửi kèm public key khi gửi file.
- Public key đúng luôn có block `BEGIN/END PUBLIC KEY`.
- Dùng đúng key của người đã ký file thì external verify mới báo VALID.

### Q: Tại sao verify external vẫn có thể INVALID dù file là file đã ký?
**A:** Có 3 nguyên nhân thường gặp:
1. Bạn dán nhầm public key (không phải key của người ký file đó).
2. File đã bị chỉnh sửa sau khi ký.
3. Key bị copy thiếu hoặc sai định dạng PEM.

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
