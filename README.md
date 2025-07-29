# API Crawler cho Báo Dân Trí và Tuổi Trẻ

Dự án này cung cấp một API xây dựng bằng FastAPI để trích xuất thông tin các bài báo mới từ file HTML hoặc payload JSON của báo Dân Trí và Tuổi Trẻ.

## Cấu trúc dự án

- `main.py`: File chính của FastAPI, định nghĩa các API endpoints.
- `crawlers/`: Thư mục chứa logic xử lý HTML.
  - `dantri_parser.py`: Xử lý HTML của Dân Trí.
  - `tuoitre_parser.py`: Xử lý HTML của Tuổi Trẻ.
- `requirements.txt`: Các thư viện cần thiết.

## Cài đặt

1.  Clone repository này về máy.
2.  Tạo và kích hoạt môi trường ảo (khuyến khích):
    ```bash
    python -m venv venv
    source venv/bin/activate  # Trên Windows: venv\Scripts\activate
    ```
3.  Cài đặt các thư viện cần thiết:
    ```bash
    pip install -r requirements.txt
    ```

## Chạy Server

Để chạy server FastAPI ở chế độ phát triển (tự động tải lại khi có thay đổi):

```bash
uvicorn main:app --reload
