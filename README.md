# Xây dựng API kiểm tra hệ thống và lấy danh sách sách với FastAPI

## Giới thiệu
Bài tập này yêu cầu xây dựng một ứng dụng API đơn giản sử dụng FastAPI. Mục tiêu là tạo ra hai endpoint cơ bản: một để kiểm tra trạng thái hoạt động của API (`/health`) và một để trả về danh sách các cuốn sách có sẵn trong thư viện (`/books`).

## Chức năng
-   **Endpoint `/health` (GET):**
    -   Mục đích: Cung cấp một cách để kiểm tra xem API có đang hoạt động hay không.
    -   Kết quả: Trả về một JSON object với thông báo `{"message": "Library API is running"}`.

-   **Endpoint `/books` (GET):**
    -   Mục đích: Trả về toàn bộ danh sách các cuốn sách được định nghĩa sẵn trong ứng dụng.
    -   Kết quả: Trả về một JSON array chứa thông tin chi tiết của 5 cuốn sách mẫu.

## Hướng dẫn chạy chương trình

1.  **Tạo và kích hoạt môi trường ảo (khuyến nghị):**
    ```bash
    python -m venv venv
    # Trên Windows
    .\venv\Scripts\activate
    # Trên macOS/Linux
    source venv/bin/activate
    ```

2.  **Cài đặt các thư viện cần thiết:**
    ```bash
    pip install fastapi uvicorn
    ```

3.  **Lưu mã nguồn:**
    Lưu nội dung của file `main.py` vào thư mục gốc của project.

4.  **Chạy ứng dụng FastAPI:**
    ```bash
    uvicorn main:app --reload
    ```
    Ứng dụng sẽ chạy trên `http://127.0.0.1:8000` (mặc định).

5.  **Kiểm tra API:**
    -   Mở trình duyệt và truy cập: `http://127.0.0.1:8000/docs` để xem Swagger UI và kiểm tra các endpoint.
    -   Truy cập `http://127.0.0.1:8000/health` để kiểm tra trạng thái API.
    -   Truy cập `http://127.0.0.1:8000/books` để xem danh sách sách.