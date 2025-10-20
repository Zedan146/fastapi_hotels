# 🧪 Pytest - Шпаргалка

## Основы Pytest

Pytest - это мощный фреймворк для тестирования Python приложений с простым синтаксисом и богатыми возможностями.

### Установка
```bash
pip install pytest pytest-asyncio pytest-cov
```

## Базовое тестирование

### Простые тесты
```python
# test_basic.py
def test_addition():
    assert 2 + 2 == 4

def test_string_concatenation():
    assert "hello" + " " + "world" == "hello world"

def test_list_operations():
    my_list = [1, 2, 3]
    assert len(my_list) == 3
    assert 2 in my_list
```

### Запуск тестов
```bash
# Запуск всех тестов
pytest

# Запуск конкретного файла
pytest test_basic.py

# Запуск с подробным выводом
pytest -v

# Запуск с выводом print
pytest -s

# Запуск конкретного теста
pytest test_basic.py::test_addition
```

## Фикстуры (Fixtures)

### Базовые фикстуры
```python
import pytest

@pytest.fixture
def sample_data():
    return {"name": "John", "age": 30, "city": "New York"}

def test_user_data(sample_data):
    assert sample_data["name"] == "John"
    assert sample_data["age"] == 30

@pytest.fixture
def numbers():
    return [1, 2, 3, 4, 5]

def test_numbers_sum(numbers):
    assert sum(numbers) == 15
```

### Фикстуры с областью видимости
```python
@pytest.fixture(scope="session")
def database_connection():
    # Создание соединения с БД (один раз за сессию)
    conn = create_connection()
    yield conn
    conn.close()

@pytest.fixture(scope="module")
def api_client():
    # Создание API клиента (один раз за модуль)
    client = APIClient()
    yield client
    client.close()

@pytest.fixture(scope="function")
def temp_file():
    # Создание временного файла (каждый тест)
    file = tempfile.NamedTemporaryFile()
    yield file
    file.close()
```

### Автоматические фикстуры
```python
@pytest.fixture(autouse=True)
def setup_test_environment():
    # Выполняется автоматически для каждого теста
    setup_environment()
    yield
    cleanup_environment()
```

### Параметризованные фикстуры
```python
@pytest.fixture(params=[1, 2, 3])
def number(request):
    return request.param

def test_number_is_positive(number):
    assert number > 0

# Или с несколькими параметрами
@pytest.fixture(params=[
    ("admin", "admin123"),
    ("user", "user123"),
    ("guest", "guest123")
])
def user_credentials(request):
    return request.param

def test_login(user_credentials):
    username, password = user_credentials
    assert len(username) > 0
    assert len(password) > 0
```

## Параметризация тестов

### Параметризация с @pytest.mark.parametrize
```python
import pytest

@pytest.mark.parametrize("input,expected", [
    (2, 4),
    (3, 9),
    (4, 16),
    (5, 25)
])
def test_square(input, expected):
    assert input ** 2 == expected

@pytest.mark.parametrize("username,password,expected", [
    ("admin", "admin123", True),
    ("user", "wrongpass", False),
    ("", "password", False),
    ("user", "", False)
])
def test_login_validation(username, password, expected):
    result = validate_login(username, password)
    assert result == expected
```

### Параметризация с фикстурами
```python
@pytest.fixture(params=["chrome", "firefox", "safari"])
def browser(request):
    return create_browser(request.param)

def test_website_compatibility(browser):
    assert browser.load_website() == "success"
```

## Тестирование исключений

### Проверка исключений
```python
import pytest

def test_division_by_zero():
    with pytest.raises(ZeroDivisionError):
        1 / 0

def test_invalid_input():
    with pytest.raises(ValueError, match="Invalid input"):
        process_input("invalid")

def test_multiple_exceptions():
    with pytest.raises((ValueError, TypeError)):
        risky_operation("bad_input")
```

### Проверка предупреждений
```python
import warnings

def test_deprecated_function():
    with pytest.warns(DeprecationWarning):
        deprecated_function()

def test_specific_warning():
    with pytest.warns(UserWarning, match="This is a warning"):
        function_that_warns()
```

## Асинхронное тестирование

### Тестирование async функций
```python
import pytest
import asyncio

@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result == "expected_result"

@pytest.mark.asyncio
async def test_async_with_fixture(async_fixture):
    result = await async_function(async_fixture)
    assert result is not None

@pytest.fixture
async def async_fixture():
    # Асинхронная фикстура
    data = await fetch_data()
    yield data
    await cleanup_data(data)
```

### Тестирование FastAPI
```python
from fastapi.testclient import TestClient
from fastapi import FastAPI

app = FastAPI()

@pytest.fixture
def client():
    return TestClient(app)

def test_read_main(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}

def test_create_item(client):
    response = client.post("/items/", json={"name": "Test Item"})
    assert response.status_code == 200
    assert response.json()["name"] == "Test Item"
```

## Моки и заглушки

### Использование unittest.mock
```python
from unittest.mock import Mock, patch, MagicMock
import pytest

def test_mock_function():
    # Создание мока
    mock_func = Mock(return_value="mocked_result")
    
    result = mock_func()
    assert result == "mocked_result"
    mock_func.assert_called_once()

def test_patch_function():
    with patch('module.function') as mock_func:
        mock_func.return_value = "patched_result"
        
        result = call_function()
        assert result == "patched_result"

@pytest.fixture
def mock_database():
    mock_db = Mock()
    mock_db.query.return_value.filter.return_value.first.return_value = {"id": 1, "name": "Test"}
    return mock_db

def test_database_query(mock_database):
    result = mock_database.query("users").filter("id=1").first()
    assert result["name"] == "Test"
```

### Патчинг в фикстурах
```python
@pytest.fixture
def mock_requests():
    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = {"status": "success"}
        yield mock_get

def test_api_call(mock_requests):
    response = make_api_call()
    assert response["status"] == "success"
    mock_requests.assert_called_once()
```

## Тестирование базы данных

### Тестирование с SQLAlchemy
```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

@pytest.fixture
def db_session():
    # Создание тестовой БД в памяти
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    yield session
    session.close()

def test_create_user(db_session):
    user = User(name="John", email="john@example.com")
    db_session.add(user)
    db_session.commit()
    
    assert user.id is not None
    assert user.name == "John"

def test_get_user(db_session):
    user = User(name="Jane", email="jane@example.com")
    db_session.add(user)
    db_session.commit()
    
    found_user = db_session.query(User).filter(User.email == "jane@example.com").first()
    assert found_user.name == "Jane"
```

### Тестирование с pytest-postgresql
```python
import pytest
from pytest_postgresql import factories

# Фикстура для тестовой БД
postgresql_proc = factories.postgresql_proc()
postgresql = factories.postgresql("postgresql_proc")

def test_database_operations(postgresql):
    # Тестирование с реальной PostgreSQL
    with postgresql.cursor() as cursor:
        cursor.execute("CREATE TABLE test (id SERIAL PRIMARY KEY, name VARCHAR(50))")
        cursor.execute("INSERT INTO test (name) VALUES ('test')")
        cursor.execute("SELECT * FROM test")
        result = cursor.fetchone()
        assert result[1] == "test"
```

## Покрытие кода

### Установка и настройка
```bash
pip install pytest-cov
```

### Запуск с покрытием
```bash
# Базовое покрытие
pytest --cov=src

# Покрытие с HTML отчетом
pytest --cov=src --cov-report=html

# Покрытие с минимальным процентом
pytest --cov=src --cov-fail-under=80

# Покрытие конкретных модулей
pytest --cov=src.models --cov=src.services
```

### Настройка в pytest.ini
```ini
[tool:pytest]
addopts = --cov=src --cov-report=html --cov-report=term-missing
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

## Маркировка тестов

### Создание маркеров
```python
# pytest.ini
[tool:pytest]
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    unit: marks tests as unit tests
    smoke: marks tests as smoke tests
```

### Использование маркеров
```python
import pytest

@pytest.mark.slow
def test_heavy_computation():
    # Долгий тест
    result = heavy_computation()
    assert result > 0

@pytest.mark.integration
def test_database_integration():
    # Интеграционный тест
    pass

@pytest.mark.unit
def test_unit_function():
    # Юнит тест
    pass

@pytest.mark.smoke
def test_basic_functionality():
    # Дымовой тест
    pass
```

### Запуск по маркерам
```bash
# Запуск только быстрых тестов
pytest -m "not slow"

# Запуск только интеграционных тестов
pytest -m integration

# Запуск дымовых тестов
pytest -m smoke
```

## Конфигурация

### pytest.ini
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
```

### conftest.py
```python
import pytest
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Глобальные фикстуры
@pytest.fixture(scope="session")
def event_loop():
    """Создание event loop для всей сессии"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def database_engine():
    """Создание движка БД для тестов"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()

@pytest.fixture
def db_session(database_engine):
    """Создание сессии БД для каждого теста"""
    SessionLocal = sessionmaker(bind=database_engine)
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()
```

## Продвинутые техники

### Пропуск тестов
```python
import pytest

@pytest.mark.skip(reason="Feature not implemented yet")
def test_future_feature():
    assert False

@pytest.mark.skipif(not hasattr(os, "getuid"), reason="Unix only")
def test_unix_feature():
    assert os.getuid() >= 0

def test_conditional_skip():
    if not check_condition():
        pytest.skip("Condition not met")
    assert True
```

### Ожидаемые сбои
```python
@pytest.mark.xfail(reason="Known issue")
def test_known_bug():
    assert False

@pytest.mark.xfail(strict=True)
def test_strict_xfail():
    assert True  # Это вызовет ошибку, так как тест прошел
```

### Кастомные утверждения
```python
def assert_user_has_required_fields(user):
    """Кастомное утверждение для проверки пользователя"""
    required_fields = ["id", "name", "email"]
    for field in required_fields:
        assert hasattr(user, field), f"User missing required field: {field}"
    assert user.id > 0, "User ID must be positive"
    assert "@" in user.email, "Email must contain @"

def test_user_creation():
    user = create_user("John", "john@example.com")
    assert_user_has_required_fields(user)
```

### Параметризация с фикстурами
```python
@pytest.fixture(params=["sqlite", "postgresql"])
def database_url(request):
    if request.param == "sqlite":
        return "sqlite:///:memory:"
    elif request.param == "postgresql":
        return "postgresql://user:pass@localhost/testdb"

def test_database_operations(database_url):
    # Тест будет запущен для каждой БД
    engine = create_engine(database_url)
    # ... тестирование
```

## Лучшие практики

### 1. Структура тестов
```
tests/
├── conftest.py
├── unit/
│   ├── test_models.py
│   ├── test_services.py
│   └── test_utils.py
├── integration/
│   ├── test_api.py
│   └── test_database.py
└── fixtures/
    ├── users.json
    └── hotels.json
```

### 2. Именование тестов
```python
# Хорошо
def test_user_creation_with_valid_data():
    pass

def test_user_creation_with_invalid_email_raises_error():
    pass

# Плохо
def test1():
    pass

def test_user():
    pass
```

### 3. Изоляция тестов
```python
@pytest.fixture(autouse=True)
def clean_database():
    # Очистка БД перед каждым тестом
    clean_all_tables()
    yield
    clean_all_tables()
```

### 4. Тестирование ошибок
```python
def test_invalid_input_raises_error():
    with pytest.raises(ValueError) as exc_info:
        process_invalid_input()
    assert "Invalid input" in str(exc_info.value)
```

### 5. Использование фикстур для данных
```python
@pytest.fixture
def sample_user():
    return {
        "name": "John Doe",
        "email": "john@example.com",
        "age": 30
    }

def test_user_processing(sample_user):
    result = process_user(sample_user)
    assert result["processed"] is True
```
