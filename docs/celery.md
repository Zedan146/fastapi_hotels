# 🥬 Celery - Шпаргалка

## Основы Celery

Celery - это распределенная система очередей задач для Python, которая позволяет выполнять задачи асинхронно в фоновом режиме.

### Установка
```bash
pip install celery redis  # Redis как брокер
pip install celery rabbitmq  # RabbitMQ как брокер
```

## Настройка Celery

### Базовая конфигурация
```python
from celery import Celery

# Создание экземпляра Celery
app = Celery('myapp')

# Конфигурация
app.conf.update(
    broker_url='redis://localhost:6379/0',
    result_backend='redis://localhost:6379/0',
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)
```

### Расширенная конфигурация
```python
from celery import Celery

app = Celery('myapp')

app.conf.update(
    # Брокер и результат
    broker_url='redis://localhost:6379/0',
    result_backend='redis://localhost:6379/0',
    
    # Сериализация
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    
    # Время
    timezone='UTC',
    enable_utc=True,
    
    # Настройки задач
    task_always_eager=False,  # False для продакшена
    task_eager_propagates=True,
    
    # Настройки воркеров
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_disable_rate_limits=False,
    
    # Настройки результата
    result_expires=3600,  # 1 час
    result_persistent=True,
    
    # Настройки очередей
    task_routes={
        'myapp.tasks.send_email': {'queue': 'email'},
        'myapp.tasks.process_image': {'queue': 'image'},
    },
    
    # Настройки retry
    task_default_retry_delay=60,
    task_max_retries=3,
)
```

## Создание задач

### Простые задачи
```python
from celery import Celery

app = Celery('myapp')

@app.task
def add(x, y):
    return x + y

@app.task
def send_email(to, subject, body):
    # Логика отправки email
    print(f"Sending email to {to}: {subject}")
    return f"Email sent to {to}"

# Вызов задач
result = add.delay(4, 4)
email_result = send_email.delay('user@example.com', 'Hello', 'World')
```

### Задачи с параметрами
```python
@app.task(bind=True, max_retries=3)
def retry_task(self, x, y):
    try:
        # Логика задачи
        result = x / y
        return result
    except ZeroDivisionError as exc:
        # Повтор через 60 секунд
        raise self.retry(countdown=60, exc=exc)

@app.task(rate_limit='10/m')  # 10 задач в минуту
def rate_limited_task():
    return "Task completed"

@app.task(time_limit=30)  # Лимит времени 30 секунд
def time_limited_task():
    import time
    time.sleep(25)  # Долгая операция
    return "Task completed"
```

### Асинхронные задачи
```python
import asyncio
from celery import Celery

app = Celery('myapp')

@app.task
def async_task():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(async_function())
    finally:
        loop.close()

async def async_function():
    # Асинхронная логика
    await asyncio.sleep(1)
    return "Async task completed"
```

## Типы задач

### Одноразовые задачи
```python
@app.task
def one_time_task(data):
    # Обработка данных
    return f"Processed: {data}"

# Вызов
result = one_time_task.delay("some data")
```

### Периодические задачи (Celery Beat)
```python
from celery.schedules import crontab

app.conf.beat_schedule = {
    'send-daily-report': {
        'task': 'myapp.tasks.send_daily_report',
        'schedule': crontab(hour=9, minute=0),  # Каждый день в 9:00
    },
    'cleanup-logs': {
        'task': 'myapp.tasks.cleanup_logs',
        'schedule': crontab(hour=2, minute=0, day_of_week=1),  # Каждый понедельник в 2:00
    },
    'health-check': {
        'task': 'myapp.tasks.health_check',
        'schedule': 60.0,  # Каждые 60 секунд
    },
}

@app.task
def send_daily_report():
    # Логика отправки отчета
    return "Daily report sent"

@app.task
def cleanup_logs():
    # Логика очистки логов
    return "Logs cleaned up"

@app.task
def health_check():
    # Проверка здоровья системы
    return "System is healthy"
```

### Цепочки задач (Chains)
```python
from celery import chain

# Последовательное выполнение
workflow = chain(
    task1.s(10),
    task2.s(),
    task3.s()
)
result = workflow.apply_async()

# Или с использованием |
result = (task1.s(10) | task2.s() | task3.s()).apply_async()
```

### Группы задач (Groups)
```python
from celery import group

# Параллельное выполнение
job = group(
    task1.s(1, 2),
    task1.s(3, 4),
    task1.s(5, 6)
)
result = job.apply_async()

# Или с использованием +
result = (task1.s(1, 2) + task1.s(3, 4) + task1.s(5, 6)).apply_async()
```

### Аккорды (Chords)
```python
from celery import chord

# Выполнение группы задач, затем callback
callback = chord([
    task1.s(1, 2),
    task1.s(3, 4),
    task1.s(5, 6)
])(callback_task.s())
```

## Обработка результатов

### Получение результатов
```python
# Синхронное получение
result = add.delay(4, 4)
value = result.get(timeout=10)  # Ждать до 10 секунд

# Асинхронная проверка
if result.ready():
    value = result.result
else:
    print("Task not ready yet")

# Получение с обработкой ошибок
try:
    value = result.get(timeout=10)
except Exception as exc:
    print(f"Task failed: {exc}")
```

### Callbacks и Error Callbacks
```python
@app.task
def success_callback(result):
    print(f"Task succeeded: {result}")

@app.task
def error_callback(task_id, exc, traceback):
    print(f"Task {task_id} failed: {exc}")

@app.task(bind=True)
def task_with_callbacks(self):
    return "Task completed"

# Вызов с callbacks
result = task_with_callbacks.apply_async(
    link=success_callback.s(),
    link_error=error_callback.s()
)
```

## Мониторинг и отладка

### Flower - веб-интерфейс для мониторинга
```bash
# Установка
pip install flower

# Запуск
celery -A myapp flower

# С настройками
celery -A myapp flower --port=5555 --broker=redis://localhost:6379/0
```

### Логирование
```python
import logging
from celery import Celery

app = Celery('myapp')

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.task
def logged_task(data):
    logger.info(f"Processing data: {data}")
    try:
        # Логика задачи
        result = process_data(data)
        logger.info(f"Task completed successfully: {result}")
        return result
    except Exception as e:
        logger.error(f"Task failed: {e}")
        raise
```

### Отслеживание прогресса
```python
@app.task(bind=True)
def long_running_task(self, total_steps):
    for i in range(total_steps):
        # Обновление прогресса
        self.update_state(
            state='PROGRESS',
            meta={'current': i, 'total': total_steps, 'status': f'Step {i}'}
        )
        # Выполнение шага
        time.sleep(1)
    
    return {'current': total_steps, 'total': total_steps, 'status': 'Completed'}

# Проверка прогресса
result = long_running_task.delay(10)
if result.state == 'PROGRESS':
    progress = result.info['current'] / result.info['total']
    print(f"Progress: {progress * 100:.1f}%")
```

## Обработка ошибок

### Retry механизм
```python
from celery.exceptions import Retry

@app.task(bind=True, max_retries=3, default_retry_delay=60)
def unreliable_task(self, data):
    try:
        # Логика, которая может упасть
        result = risky_operation(data)
        return result
    except Exception as exc:
        # Логирование ошибки
        self.logger.warning(f"Task failed: {exc}")
        
        # Повтор через 60 секунд
        raise self.retry(countdown=60, exc=exc)

@app.task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3})
def auto_retry_task(self):
    # Автоматический retry для любых исключений
    raise Exception("Something went wrong")
```

### Обработка специфичных ошибок
```python
from celery.exceptions import Retry

@app.task(bind=True)
def handle_specific_errors(self, data):
    try:
        return process_data(data)
    except ConnectionError as exc:
        # Повтор для ошибок соединения
        raise self.retry(countdown=60, exc=exc)
    except ValueError as exc:
        # Не повторять для ошибок валидации
        self.logger.error(f"Validation error: {exc}")
        raise
    except Exception as exc:
        # Повтор для других ошибок
        raise self.retry(countdown=120, exc=exc)
```

## Интеграция с FastAPI

### Базовая интеграция
```python
from fastapi import FastAPI, BackgroundTasks
from celery import Celery

app = FastAPI()
celery_app = Celery('myapp', broker='redis://localhost:6379/0')

@app.task
def send_email_task(email: str, subject: str, body: str):
    # Логика отправки email
    return f"Email sent to {email}"

@app.post("/send-email")
async def send_email(email: str, subject: str, body: str):
    # Запуск задачи в фоне
    task = send_email_task.delay(email, subject, body)
    return {"task_id": task.id, "status": "Email queued"}

@app.get("/task-status/{task_id}")
async def get_task_status(task_id: str):
    task = celery_app.AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": task.status,
        "result": task.result if task.ready() else None
    }
```

### Асинхронная интеграция
```python
from fastapi import FastAPI, HTTPException
from celery import Celery
import asyncio

app = FastAPI()
celery_app = Celery('myapp', broker='redis://localhost:6379/0')

@app.task
def process_data_task(data: dict):
    # Обработка данных
    time.sleep(5)  # Имитация долгой операции
    return {"processed": data, "status": "completed"}

@app.post("/process-data")
async def process_data(data: dict):
    # Запуск задачи
    task = process_data_task.delay(data)
    
    # Ожидание результата (неблокирующее)
    result = await asyncio.to_thread(task.get, timeout=10)
    return result
```

## Запуск и управление

### Запуск воркера
```bash
# Базовый запуск
celery -A myapp worker --loglevel=info

# С несколькими воркерами
celery -A myapp worker --loglevel=info --concurrency=4

# С определенной очередью
celery -A myapp worker --loglevel=info --queues=email,image

# В фоновом режиме
celery -A myapp worker --loglevel=info --detach
```

### Запуск планировщика (Beat)
```bash
# Запуск Beat
celery -A myapp beat --loglevel=info

# С сохранением расписания в файл
celery -A myapp beat --loglevel=info --schedule=/tmp/celerybeat-schedule
```

### Запуск Flower
```bash
# Запуск Flower
celery -A myapp flower --port=5555
```

### Docker Compose
```yaml
version: '3.8'
services:
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
  
  worker:
    build: .
    command: celery -A myapp worker --loglevel=info
    depends_on:
      - redis
  
  beat:
    build: .
    command: celery -A myapp beat --loglevel=info
    depends_on:
      - redis
  
  flower:
    build: .
    command: celery -A myapp flower --port=5555
    ports:
      - "5555:5555"
    depends_on:
      - redis
```

## Лучшие практики

### 1. Идемпотентность задач
```python
@app.task
def idempotent_task(task_id, data):
    """Задача должна быть идемпотентной"""
    # Проверка, не выполнялась ли задача ранее
    if check_task_completed(task_id):
        return get_task_result(task_id)
    
    # Выполнение задачи
    result = process_data(data)
    
    # Сохранение результата
    save_task_result(task_id, result)
    return result
```

### 2. Обработка больших данных
```python
@app.task
def process_large_dataset(dataset_id):
    """Обработка больших наборов данных по частям"""
    dataset = get_dataset(dataset_id)
    chunk_size = 1000
    
    for i in range(0, len(dataset), chunk_size):
        chunk = dataset[i:i + chunk_size]
        process_chunk.delay(chunk, dataset_id, i)
    
    return f"Started processing {len(dataset)} items in chunks of {chunk_size}"
```

### 3. Мониторинг и алерты
```python
@app.task(bind=True)
def monitored_task(self, data):
    try:
        result = process_data(data)
        
        # Отправка уведомления об успехе
        send_success_notification.delay(self.request.id, result)
        
        return result
    except Exception as exc:
        # Отправка уведомления об ошибке
        send_error_notification.delay(self.request.id, str(exc))
        raise
```

### 4. Ограничение ресурсов
```python
# Ограничение памяти
@app.task(soft_time_limit=300, time_limit=360)
def memory_intensive_task(data):
    # Задача с ограничением по времени
    return process_large_data(data)

# Ограничение CPU
@app.task(rate_limit='10/m')
def cpu_intensive_task(data):
    # Максимум 10 задач в минуту
    return compute_intensive_operation(data)
```

### 5. Тестирование задач
```python
import pytest
from celery import Celery

@pytest.fixture
def celery_app():
    app = Celery('test')
    app.conf.update(
        task_always_eager=True,
        task_eager_propagates=True,
    )
    return app

def test_task_execution(celery_app):
    @celery_app.task
    def test_task(x, y):
        return x + y
    
    result = test_task.delay(2, 2)
    assert result.result == 4
```
