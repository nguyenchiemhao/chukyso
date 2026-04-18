# Demo chu ky so va ky PDF bang Python

## 1. Chu ky so la gi?

Chu ky so la co che dung **khoa bi mat** de ky len du lieu va dung **khoa cong khai** de xac minh:

- Tai lieu co bi sua sau khi ky hay khong.
- Ai la nguoi da ky.
- Nguoi ky co the choi bo chu ky cua minh hay khong.

Trong thuc te, chu ky so thuong duoc dung voi:

- Chung thu so (certificate) do CA cap.
- Thuat toan bam nhu SHA-256.
- Thuat toan bat doi xung nhu RSA hoac ECDSA.

## 2. Chu ky so tren PDF hoat dong the nao?

Khi ky PDF:

1. Ung dung tinh hash cua cac phan du lieu can bao ve trong file PDF.
2. Hash do duoc ky bang private key.
3. Chu ky va thong tin chung thu duoc nhung vao trong file PDF.
4. Trinh doc PDF dung public key trong certificate de xac minh.

Neu file bi sua sau khi ky, kiem tra chu ky se that bai.

## 3. Demo trong thu muc nay

File `demo_sign_pdf.py` se:

1. Tao mot cap RSA key va certificate tu ky.
2. Tao file PDF mau.
3. Chen o chu ky hien thi vao trang dau.
4. Ky file PDF bang `pyHanko`.

## 4. Cai thu vien

```bash
pip install -r requirements.txt
```

## 5. Chay demo

```bash
python demo_sign_pdf.py
```

Sau khi chay xong, ban se thay:

- `output/certs/demo_private_key.pem`
- `output/certs/demo_certificate.pem`
- `output/pdf/unsigned_demo.pdf`
- `output/pdf/signed_demo.pdf`

## 6. Demo xac minh phia nguoi nhan

Nguoi nhan dung certificate cua nguoi gui (certificate nay chua public key) de kiem tra:

```bash
python demo_verify_pdf.py
```

Neu muon xem them chi tiet:

```bash
python demo_verify_pdf.py --show-details
```

Demo se kiem tra:

- PDF co chu ky hay khong.
- Noi dung co bi sua sau khi ky hay khong.
- Chu ky ma hoc co hop le hay khong.
- Certificate dung de xac minh co khop chu ky hay khong.

## 7. Thu truong hop PDF bi sua sau khi ky

Tao mot ban sao da bi sua:

```bash
python demo_tamper_pdf.py
```

Sau do xac minh:

```bash
python demo_verify_pdf.py --pdf output/pdf/tampered_demo.pdf
```

Luc nay ket qua se bao `INVALID`.

## 8. Luu y quan trong

- Day la **demo hoc tap**, dung certificate tu ky.
- Khi mo PDF da ky, trinh doc co the bao nguoi ky **chua duoc tin cay**.
- Trong he thong that, ban thuong dung USB token, HSM, smart card, hoac certificate do CA hop le cap.
# chukyso
