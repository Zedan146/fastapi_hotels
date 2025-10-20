# 🚀 FastAPI - Шпаргалка

## Основы FastAPI

FastAPI - современный веб-фреймворк для создания API на Python с автоматической генерацией документации.

### Установка
```bash
pip install fastapi uvicorn
```

### Базовое приложение
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}
```

### Запуск сервера
```bash
# Разработка
uvicorn main:app --reload

# Продакшн
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Типы данных и валидация

### Pydantic модели
```python
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date

class User(BaseModel):
    id: int
    name: str
    email: EmailStr
    age: Optional[int] = None
    is_active: bool = True

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    age: Optional[int] = None
```

### Валидация параметров
```python
from fastapi import Query, Path, Body

@app.get("/users/{user_id}")
async def get_user(
    user_id: int = Path(..., gt=0, description="ID пользователя"),
    skip: int = Query(0, ge=0, description="Пропустить записи"),
    limit: int = Query(10, ge=1, le=100, description="Лимит записей")
):
    return {"user_id": user_id, "skip": skip, "limit": limit}
```

## HTTP методы

### GET запросы
```python
@app.get("/users")
async def get_users():
    return {"users": []}

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    return {"user_id": user_id}
```

### POST запросы
```python
@app.post("/users")
async def create_user(user: UserCreate):
    return {"message": "User created", "user": user}
```

### PUT и PATCH
```python
@app.put("/users/{user_id}")
async def update_user(user_id: int, user: User):
    return {"message": "User updated"}

@app.patch("/users/{user_id}")
async def partial_update_user(user_id: int, user: UserUpdate):
    return {"message": "User partially updated"}
```

### DELETE
```python
@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    return {"message": "User deleted"}
```

## Зависимости (Dependencies)

### Простые зависимости
```python
from fastapi import Depends

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/users")
async def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()
```

### Зависимости с параметрами
```python
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/users/{user_id}")
async def get_user(user: User = Depends(get_user_by_id)):
    return user
```

## Обработка ошибок

### HTTP исключения
```python
from fastapi import HTTPException

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    if user_id < 1:
        raise HTTPException(
            status_code=400,
            detail="Invalid user ID"
        )
    return {"user_id": user_id}
```

### Кастомные исключения
```python
from fastapi import Request
from fastapi.responses import JSONResponse

class CustomException(Exception):
    def __init__(self, message: str):
        self.message = message

@app.exception_handler(CustomException)
async def custom_exception_handler(request: Request, exc: CustomException):
    return JSONResponse(
        status_code=400,
        content={"message": exc.message}
    )
```

## Аутентификация

### JWT токены
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/protected")
async def protected_route(current_user: int = Depends(get_current_user)):
    return {"user_id": current_user}
```

## Файлы и загрузка

### Загрузка файлов
```python
from fastapi import File, UploadFile

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    return {"filename": file.filename, "size": len(contents)}
```

### Множественная загрузка
```python
@app.post("/upload-multiple")
async def upload_files(files: List[UploadFile] = File(...)):
    return {"files": [{"filename": f.filename} for f in files]}
```

## Кэширование

### Простое кэширование
```python
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

# Инициализация
FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

@app.get("/expensive-operation")
@cache(expire=60)  # кэш на 60 секунд
async def expensive_operation():
    # Дорогая операция
    return {"result": "expensive_data"}
```

## Middleware

### CORS
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Кастомный middleware
```python
from fastapi import Request
import time

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

## Тестирование

### Тестирование endpoints
```python
from fastapi.testclient import TestClient

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}

def test_create_user():
    response = client.post("/users", json={"name": "John", "email": "john@example.com"})
    assert response.status_code == 200
```

## Полезные паттерны

### Пагинация
```python
from typing import Optional

class PaginationParams:
    def __init__(self, skip: int = Query(0, ge=0), limit: int = Query(10, ge=1, le=100)):
        self.skip = skip
        self.limit = limit

@app.get("/users")
async def get_users(pagination: PaginationParams = Depends()):
    return {"skip": pagination.skip, "limit": pagination.limit}
```

### Фильтрация
```python
@app.get("/users")
async def get_users(
    name: Optional[str] = Query(None),
    age: Optional[int] = Query(None, ge=0),
    is_active: Optional[bool] = Query(None)
):
    filters = {}
    if name:
        filters["name"] = name
    if age:
        filters["age"] = age
    if is_active is not None:
        filters["is_active"] = is_active
    
    return {"filters": filters}
```

## Производительность

### Асинхронные операции
```python
import asyncio
import httpx

@app.get("/external-data")
async def get_external_data():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com/data")
        return response.json()
```

### Фоновые задачи
```python
from fastapi import BackgroundTasks

def send_notification(email: str, message: str):
    # Отправка уведомления
    pass

@app.post("/users")
async def create_user(user: UserCreate, background_tasks: BackgroundTasks):
    # Создание пользователя
    background_tasks.add_task(send_notification, user.email, "Welcome!")
    return {"message": "User created"}
```

## Лучшие практики

1. **Используйте типизацию** - FastAPI автоматически генерирует документацию
2. **Валидируйте данные** - используйте Pydantic модели
3. **Обрабатывайте ошибки** - создавайте понятные HTTP исключения
4. **Тестируйте код** - используйте TestClient для тестирования
5. **Документируйте API** - FastAPI автоматически создает OpenAPI схему
6. **Используйте зависимости** - для переиспользования логики
7. **Кэшируйте данные** - для повышения производительности
8. **Мониторьте производительность** - используйте middleware для логирования
