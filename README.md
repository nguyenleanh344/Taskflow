# TaskFlow API

TaskFlow API là backend quản lý project, task, comment và project member được xây dựng bằng FastAPI, PostgreSQL, Redis và SQLAlchemy async.

## Yêu cầu

- Python 3.12+
- Docker Desktop
- Docker Compose

## Chạy local

Tạo virtual environment và cài dependencies:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

Khởi động PostgreSQL và Redis:

```powershell
docker compose up -d postgres redis
```

Chạy API:

```powershell
python -m uvicorn app.main:app --reload
```

API documentation có tại:

```text
http://127.0.0.1:8000/docs
```

## Kiểm tra code

```powershell
ruff check .
ruff format --check .
pytest -q
```

## Build Docker image

```powershell
docker build -t taskflow-api:latest .
```

## CI với Jenkins

Pipeline sử dụng file `Jenkinsfile` để tự động:

1. Cài dependencies.
2. Chạy Ruff.
3. Chạy test.
4. Build Docker image.

Jenkins job có thể dùng Poll SCM hoặc GitHub Webhook để tự động build khi có commit mới trên branch `main`.
