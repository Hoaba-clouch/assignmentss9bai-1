from fastapi import FastAPI, HTTPException, status, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Any, Tuple, Dict
from datetime import datetime, timezone
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

app = FastAPI(
    title="Team Task Manager API",
    description="Hệ thống RESTful API quản lý công việc nhóm với FastAPI.",
    version="1.0.0",
)

# In-memory Database
tasks_db: List[Dict[str, Any]] = [
    {
        "id": 1,
        "title": "Thiet ke database Shop AI",
        "description": "Xay dung bang va toi uu index",
        "assignee": "QuyDev",
        "priority": 1,
        "status": "todo",
        "created_at": "2026-07-01T09:00:00Z"
    },
    {
        "id": 2,
        "title": "Code bo API Authen",
        "description": "Trien khai filter verify JWT token",
        "assignee": "FixerQ",
        "priority": 2,
        "status": "done",
        "created_at": "2026-07-01T10:00:00Z"
    }
]

# Helper for Unified Response
def create_unified_response(
    status_code: int,
    message: str,
    data: Optional[Any],
    error: Optional[str],
    path: str
) -> Dict[str, Any]:
    """Helper to create a standardized Unified Envelope JSON response."""
    return {
        "statusCode": status_code,
        "message": message,
        "data": data,
        "error": error,
        "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        "path": path,
    }

# --- Pydantic Models (Schemas) ---

class TaskBase(BaseModel):
    title: str = Field(min_length=3, max_length=100)
    description: str = Field(min_length=1, max_length=500) # Ensure not empty
    assignee: str = Field(min_length=1, max_length=50) # Ensure not empty
    priority: int = Field(ge=1, le=5)

    @field_validator('assignee')
    @classmethod
    def check_assignee_whitespace(cls, v: str) -> str:
        """Strips leading/trailing whitespace and ensures assignee is not empty."""
        stripped_v = v.strip()
        if not stripped_v:
            raise ValueError('Assignee cannot be empty or consist only of whitespace')
        return stripped_v

class TaskCreateSchema(TaskBase):
    pass # Inherits validation rules from TaskBase

class TaskResponseSchema(TaskBase):
    id: int
    status: str
    created_at: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "title": "Thiet ke database Shop AI",
                    "description": "Xay dung bang va toi uu index",
                    "assignee": "QuyDev",
                    "priority": 1,
                    "status": "todo",
                    "created_at": "2026-07-01T09:00:00Z"
                }
            ]
        }
    }

class TaskStatusUpdateSchema(BaseModel):
    status: str = Field(..., pattern="^(todo|in_progress|done)$", description="Trạng thái công việc: todo, in_progress, hoặc done")

class TeamMetricsSchema(BaseModel):
    total_tasks: int
    completed_tasks: int
    completion_rate_percentage: float

# --- Global Exception Handlers ---

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    detail_message = "Lỗi không xác định."
    detail_error = f"HTTP-{exc.status_code}: An unexpected error occurred."

    if isinstance(exc.detail, dict):
        detail_message = exc.detail.get("message", detail_message)
        detail_error = exc.detail.get("error", detail_error)
    elif isinstance(exc.detail, str):
        detail_message = exc.detail
        detail_error = f"HTTP-{exc.status_code}: {exc.detail}"

    response_content = create_unified_response(
        status_code=exc.status_code,
        message=detail_message,
        data=None,
        error=detail_error,
        path=request.url.path
    )
    return JSONResponse(status_code=exc.status_code, content=response_content)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    response_content = create_unified_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        message="Lỗi: Dữ liệu đầu vào không hợp lệ hoặc sai định dạng quy định!",
        data=None,
        error="ERR-VAL-422: Validation error at Request Body fields constraint layout. " + str(exc.errors()),
        path=request.url.path
    )
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=response_content)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    response_content = create_unified_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message="Lỗi: Hệ thống gặp sự cố không mong muốn, vui lòng thử lại sau!",
        data=None,
        error=f"ERR-SERVER-500: Internal server error. Detail: {type(exc).__name__}: {str(exc)}",
        path=request.url.path
    )
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=response_content)


# --- Endpoint Path Operation Functions ---

@app.get("/tasks", response_model=Dict[str, Any], summary="Xem danh sách công việc hiện có")
async def get_all_tasks(request: Request, status_filter: Optional[str] = None):
    """
    Trả về toàn bộ danh sách công việc trong hệ thống.
    Hỗ trợ Query Parameter `status` để lọc công việc theo trạng thái nếu Client truyền lên.
    """
    filtered_tasks = tasks_db
    if status_filter:
        filtered_tasks = [task for task in tasks_db if task["status"] == status_filter]

    # Map raw dicts to TaskResponseSchema for consistent output
    response_data = [TaskResponseSchema(**task).model_dump() for task in filtered_tasks]

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=create_unified_response(
            status_code=status.HTTP_200_OK,
            message="Lấy danh sách công việc thành công!",
            data=response_data,
            error=None,
            path=request.url.path
        )
    )


@app.post("/tasks", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED, summary="Tạo mới công việc nhóm")
async def create_task(request: Request, task_in: TaskCreateSchema):
    """
    Tiếp nhận dữ liệu JSON từ Request Body để tạo công việc mới.
    Hệ thống tự động tăng ID, mặc định gán trạng thái ban đầu là "todo",
    và tự động sinh thời gian khởi tạo hệ thống.
    Kiểm tra trùng tiêu đề công việc.
    """
    # Check for duplicate title
    for task in tasks_db:
        if task["title"] == task_in.title:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Lỗi: Tiêu đề công việc này đã tồn tại trong nhóm!",
                    "error": "ERR-TASK-01: Task conflict: Title field duplicates an existing record."
                }
            )

    # Auto-generate ID
    new_id = max([t["id"] for t in tasks_db]) + 1 if tasks_db else 1
    current_time_iso = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

    new_task = {
        "id": new_id,
        "title": task_in.title,
        "description": task_in.description,
        "assignee": task_in.assignee,
        "priority": task_in.priority,
        "status": "todo",
        "created_at": current_time_iso
    }
    tasks_db.append(new_task)

    response_data = TaskResponseSchema(**new_task).model_dump()

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=create_unified_response(
            status_code=status.HTTP_201_CREATED,
            message="Khởi tạo công việc mới thành công!",
            data=response_data,
            error=None,
            path=request.url.path
        )
    )


@app.put("/tasks/{task_id}", response_model=Dict[str, Any], summary="Cập nhật trạng thái tiến độ công việc")
async def update_task_status(request: Request, task_id: int, status_in: TaskStatusUpdateSchema):
    """
    Cập nhật trạng thái tiến độ của một công việc cụ thể.
    """
    found_task = None
    task_index = -1
    for i, task in enumerate(tasks_db):
        if task["id"] == task_id:
            found_task = task
            task_index = i
            break

    if not found_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": f"Lỗi: Không tìm thấy công việc với ID: {task_id}.",
                "error": "ERR-TASK-03: Task not found."
            }
        )

    # Check if task is already 'done' and prevent updating
    if found_task["status"] == "done":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Lỗi: Không thể cập nhật trạng thái của công việc đã hoàn thành!",
                "error": "ERR-TASK-04: Cannot update status of a completed task."
            }
        )

    # Update status
    tasks_db[task_index]["status"] = status_in.status
    updated_task = tasks_db[task_index]

    response_data = TaskResponseSchema(**updated_task).model_dump()

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=create_unified_response(
            status_code=status.HTTP_200_OK,
            message="Cập nhật tiến độ công việc thành công!",
            data=response_data,
            error=None,
            path=request.url.path
        )
    )

# Internal business logic function (no FastAPI components)
def calculate_team_metrics() -> Tuple[int, int, float]:
    """
    Tính toán các số liệu thống kê về hiệu suất nhóm.
    Trả về (tổng_số_công_việc, số_lượng_việc_đã_hoàn_thành, tỷ_lệ_hoàn_thành_phần_trăm).
    """
    total_tasks = len(tasks_db)
    completed_tasks = sum(1 for task in tasks_db if task["status"] == "done")
    
    completion_rate_percentage = 0.0
    if total_tasks > 0:
        completion_rate_percentage = (completed_tasks / total_tasks) * 100

    return total_tasks, completed_tasks, completion_rate_percentage


@app.get("/tasks/analytics/dashboard", response_model=Dict[str, Any], summary="Thống kê hiệu suất và Phân bổ tài nguyên")
async def get_dashboard_analytics(request: Request):
    """
    Lấy số liệu thống kê tổng quan về hiệu suất nhóm.
    """
    total, completed, rate = calculate_team_metrics()

    metrics = TeamMetricsSchema(
        total_tasks=total,
        completed_tasks=completed,
        completion_rate_percentage=rate
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=create_unified_response(
            status_code=status.HTTP_200_OK,
            message="Lấy số liệu thống kê hiệu suất nhóm thành công!",
            data=metrics.model_dump(),
            error=None,
            path=request.url.path
        )
    )
