# Hệ thống API quản lý công việc nhóm (Team Task Manager API)

## Giới thiệu
Đây là một dự án mini nhằm xây dựng một hệ thống RESTful API cơ bản để quản lý công việc nhóm. Dự án này sử dụng framework FastAPI của Python, với cơ sở dữ liệu mô phỏng trong bộ nhớ (in-memory database). Mục tiêu chính là làm quen với kiến trúc Decoupled, định tuyến API, kiểm tra dữ liệu với Pydantic, chuẩn hóa phản hồi API (Unified Envelope) và quản lý dự án hiệu quả.

## Các chức năng chính
Hệ thống hỗ trợ các chức năng quản lý công việc sau:
1.  **Xem danh sách công việc**: Lấy toàn bộ danh sách công việc, có thể lọc theo trạng thái.
    *   `GET /tasks?status={status}`
2.  **Tạo mới công việc**: Thêm một công việc mới vào hệ thống với ID tự động, trạng thái mặc định là "todo" và thời gian tạo tự động. Có kiểm tra trùng tiêu đề.
    *   `POST /tasks`
3.  **Cập nhật trạng thái công việc**: Thay đổi trạng thái của một công việc cụ thể. Có kiểm tra ID tồn tại và ngăn chặn cập nhật công việc đã hoàn thành.
    *   `PUT /tasks/{task_id}`
4.  **Thống kê hiệu suất nhóm**: Cung cấp số liệu thống kê về tổng số công việc, số lượng công việc đã hoàn thành và tỷ lệ hoàn thành.
    *   `GET /tasks/analytics/dashboard`

## Công nghệ sử dụng
*   **FastAPI**: Web framework hiện đại, nhanh (high-performance), dễ sử dụng để xây dựng API.
*   **Pydantic**: Thư viện dùng để định nghĩa các cấu trúc dữ liệu và thực hiện validation tự động.
*   **Uvicorn**: Máy chủ ASGI để chạy ứng dụng FastAPI.
*   **Python 3.9+**: Ngôn ngữ lập trình chính.

## Hướng dẫn cài đặt và chạy ứng dụng
Để chạy ứng dụng này, bạn cần có Python 3.9 hoặc cao hơn đã được cài đặt trên hệ thống.

1.  **Clone repository:**
    ```bash
    git clone <YOUR_REPOSITORY_URL>
    cd <YOUR_REPOSITORY_NAME>
    ```

2.  **Tạo và kích hoạt môi trường ảo (Virtual Environment):**
    ```bash
    python -m venv venv
    # Trên Windows:
    .\venv\Scripts\activate
    # Trên macOS/Linux:
    source venv/bin/activate
    ```

3.  **Cài đặt các thư viện cần thiết:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Chạy ứng dụng FastAPI với Uvicorn:**
    ```bash
    uvicorn main:app --reload
    ```
    Ứng dụng sẽ chạy trên `http://127.0.0.1:8000`. Bạn có thể truy cập tài liệu API tương tác tại `http://127.0.0.1:8000/docs` (Swagger UI) hoặc `http://127.0.0.1:8000/redoc` (ReDoc).

## Các Endpoint API

### 1. Lấy danh sách công việc
*   **Method:** `GET`
*   **Path:** `/tasks`
*   **Query Parameter (Optional):** `status` (e.g., `todo`, `in_progress`, `done`)
*   **Mô tả:** Trả về danh sách tất cả công việc hoặc danh sách công việc theo trạng thái.

### 2. Tạo mới công việc
*   **Method:** `POST`
*   **Path:** `/tasks`
*   **Request Body:** `TaskCreateSchema`
    ```json
    {
      "title": "Viet tai lieu SRS project",
      "description": "Mo ta chi tiet endpoint va model dac ta",
      "assignee": "Gu AI",
      "priority": 3
    }
    ```
*   **Mô tả:** Tạo một công việc mới. ID, trạng thái ban đầu (`todo`) và thời gian tạo sẽ được tự động gán. Trả về lỗi nếu tiêu đề công việc bị trùng.

### 3. Cập nhật trạng thái công việc
*   **Method:** `PUT`
*   **Path:** `/tasks/{task_id}`
*   **Request Body:** `TaskStatusUpdateSchema`
    ```json
    {
      "status": "in_progress"
    }
    ```
*   **Mô tả:** Cập nhật trạng thái của công việc. Trả về lỗi nếu `task_id` không tồn tại hoặc nếu công việc đã ở trạng thái `done`.

### 4. Lấy số liệu thống kê hiệu suất nhóm
*   **Method:** `GET`
*   **Path:** `/tasks/analytics/dashboard`
*   **Mô tả:** Trả về tổng số công việc, số lượng công việc đã hoàn thành và tỷ lệ hoàn thành dưới dạng phần trăm.
