# 💉 Dependency Injection Pattern - Шпаргалка

## Что такое Dependency Injection

Dependency Injection (DI) - это паттерн проектирования, который реализует принцип инверсии зависимостей (Inversion of Control). Вместо того чтобы объекты сами создавали свои зависимости, зависимости передаются извне через конструктор, свойства или методы.

## Зачем нужен Dependency Injection

### Преимущества:
- **Слабая связанность** - объекты не зависят от конкретных реализаций
- **Тестируемость** - легко подставлять моки для тестирования
- **Гибкость** - можно легко менять реализации зависимостей
- **Переиспользование** - компоненты можно использовать в разных контекстах
- **Конфигурируемость** - поведение можно настраивать через конфигурацию
- **Управление жизненным циклом** - централизованное управление созданием объектов

## Типы Dependency Injection

### 1. Constructor Injection (Внедрение через конструктор)
```python
from abc import ABC, abstractmethod
from typing import Protocol

class DatabaseProtocol(Protocol):
    async def get_user(self, user_id: int): ...

class UserService:
    def __init__(self, database: DatabaseProtocol):
        self.database = database
    
    async def get_user(self, user_id: int):
        return await self.database.get_user(user_id)

# Использование
user_service = UserService(database)
```

### 2. Property Injection (Внедрение через свойства)
```python
class UserService:
    def __init__(self):
        self._database = None
    
    @property
    def database(self) -> DatabaseProtocol:
        return self._database
    
    @database.setter
    def database(self, value: DatabaseProtocol):
        self._database = value
    
    async def get_user(self, user_id: int):
        return await self.database.get_user(user_id)

# Использование
user_service = UserService()
user_service.database = database
```

### 3. Method Injection (Внедрение через методы)
```python
class UserService:
    async def get_user(self, user_id: int, database: DatabaseProtocol):
        return await database.get_user(user_id)

# Использование
user_service = UserService()
user = await user_service.get_user(user_id, database)
```

## Простой DI контейнер

### Базовый контейнер
```python
from typing import TypeVar, Type, Dict, Any, Callable, Optional
from abc import ABC, abstractmethod

T = TypeVar('T')

class DIContainer:
    """Простой контейнер для внедрения зависимостей"""
    
    def __init__(self):
        self._services: Dict[Type, Any] = {}
        self._factories: Dict[Type, Callable] = {}
        self._singletons: Dict[Type, Any] = {}
    
    def register_singleton(self, interface: Type[T], implementation: Type[T]) -> None:
        """Регистрация синглтона"""
        self._services[interface] = implementation
    
    def register_factory(self, interface: Type[T], factory: Callable[[], T]) -> None:
        """Регистрация фабрики"""
        self._factories[interface] = factory
    
    def register_instance(self, interface: Type[T], instance: T) -> None:
        """Регистрация экземпляра"""
        self._services[interface] = instance
    
    def get(self, interface: Type[T]) -> T:
        """Получение зависимости"""
        # Проверка синглтонов
        if interface in self._singletons:
            return self._singletons[interface]
        
        # Создание нового экземпляра
        if interface in self._services:
            implementation = self._services[interface]
            if isinstance(implementation, type):
                instance = self._create_instance(implementation)
            else:
                instance = implementation
        elif interface in self._factories:
            instance = self._factories[interface]()
        else:
            raise ValueError(f"Service {interface} not registered")
        
        # Кэширование синглтона
        if interface in self._services and isinstance(self._services[interface], type):
            self._singletons[interface] = instance
        
        return instance
    
    def _create_instance(self, implementation: Type[T]) -> T:
        """Создание экземпляра с автоматическим внедрением зависимостей"""
        import inspect
        
        signature = inspect.signature(implementation.__init__)
        kwargs = {}
        
        for param_name, param in signature.parameters.items():
            if param_name == 'self':
                continue
            
            if param.annotation != inspect.Parameter.empty:
                kwargs[param_name] = self.get(param.annotation)
        
        return implementation(**kwargs)

# Использование
container = DIContainer()
container.register_singleton(DatabaseProtocol, PostgreSQLDatabase)
container.register_singleton(UserService, UserService)

user_service = container.get(UserService)
```

## Продвинутый DI контейнер

### Контейнер с жизненными циклами
```python
from enum import Enum
from typing import Union, Callable, Any
import threading

class Lifecycle(Enum):
    SINGLETON = "singleton"
    TRANSIENT = "transient"
    SCOPED = "scoped"

class AdvancedDIContainer:
    """Продвинутый контейнер с поддержкой жизненных циклов"""
    
    def __init__(self):
        self._registrations: Dict[Type, Dict[str, Any]] = {}
        self._instances: Dict[Type, Any] = {}
        self._scoped_instances: Dict[str, Dict[Type, Any]] = {}
        self._lock = threading.Lock()
    
    def register(
        self,
        interface: Type[T],
        implementation: Union[Type[T], Callable[[], T]],
        lifecycle: Lifecycle = Lifecycle.TRANSIENT
    ) -> None:
        """Регистрация сервиса"""
        self._registrations[interface] = {
            'implementation': implementation,
            'lifecycle': lifecycle
        }
    
    def get(self, interface: Type[T], scope_id: str = None) -> T:
        """Получение зависимости"""
        if interface not in self._registrations:
            raise ValueError(f"Service {interface} not registered")
        
        registration = self._registrations[interface]
        lifecycle = registration['lifecycle']
        
        if lifecycle == Lifecycle.SINGLETON:
            return self._get_singleton(interface, registration)
        elif lifecycle == Lifecycle.SCOPED:
            return self._get_scoped(interface, registration, scope_id)
        else:  # TRANSIENT
            return self._create_instance(interface, registration)
    
    def _get_singleton(self, interface: Type[T], registration: Dict) -> T:
        """Получение синглтона"""
        with self._lock:
            if interface not in self._instances:
                self._instances[interface] = self._create_instance(interface, registration)
            return self._instances[interface]
    
    def _get_scoped(self, interface: Type[T], registration: Dict, scope_id: str) -> T:
        """Получение scoped экземпляра"""
        if not scope_id:
            raise ValueError("Scope ID required for scoped services")
        
        if scope_id not in self._scoped_instances:
            self._scoped_instances[scope_id] = {}
        
        if interface not in self._scoped_instances[scope_id]:
            self._scoped_instances[scope_id][interface] = self._create_instance(interface, registration)
        
        return self._scoped_instances[scope_id][interface]
    
    def _create_instance(self, interface: Type[T], registration: Dict) -> T:
        """Создание экземпляра"""
        implementation = registration['implementation']
        
        if callable(implementation) and not isinstance(implementation, type):
            return implementation()
        
        # Автоматическое внедрение зависимостей
        import inspect
        signature = inspect.signature(implementation.__init__)
        kwargs = {}
        
        for param_name, param in signature.parameters.items():
            if param_name == 'self':
                continue
            
            if param.annotation != inspect.Parameter.empty:
                kwargs[param_name] = self.get(param.annotation)
        
        return implementation(**kwargs)
    
    def create_scope(self) -> 'DIContainerScope':
        """Создание области видимости"""
        return DIContainerScope(self)

class DIContainerScope:
    """Область видимости для scoped сервисов"""
    
    def __init__(self, container: AdvancedDIContainer):
        self.container = container
        self.scope_id = str(id(self))
    
    def get(self, interface: Type[T]) -> T:
        """Получение зависимости в области видимости"""
        return self.container.get(interface, self.scope_id)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Очистка scoped экземпляров
        if self.scope_id in self.container._scoped_instances:
            del self.container._scoped_instances[self.scope_id]
```

## Интеграция с FastAPI

### FastAPI DI система
```python
from fastapi import Depends, HTTPException
from typing import Annotated
from contextlib import asynccontextmanager

# Определение протоколов
class DatabaseProtocol(Protocol):
    async def get_user(self, user_id: int): ...
    async def create_user(self, user_data: dict): ...

class UserServiceProtocol(Protocol):
    async def get_user(self, user_id: int): ...
    async def create_user(self, user_data: dict): ...

# Реализации
class PostgreSQLDatabase:
    async def get_user(self, user_id: int):
        # Реализация получения пользователя
        pass
    
    async def create_user(self, user_data: dict):
        # Реализация создания пользователя
        pass

class UserService:
    def __init__(self, database: DatabaseProtocol):
        self.database = database
    
    async def get_user(self, user_id: int):
        return await self.database.get_user(user_id)
    
    async def create_user(self, user_data: dict):
        return await self.database.create_user(user_data)

# DI контейнер
container = AdvancedDIContainer()
container.register(DatabaseProtocol, PostgreSQLDatabase, Lifecycle.SINGLETON)
container.register(UserServiceProtocol, UserService, Lifecycle.SINGLETON)

# FastAPI зависимости
async def get_database() -> DatabaseProtocol:
    return container.get(DatabaseProtocol)

async def get_user_service(
    database: Annotated[DatabaseProtocol, Depends(get_database)]
) -> UserServiceProtocol:
    return UserService(database)

# Использование в endpoints
@app.get("/users/{user_id}")
async def get_user(
    user_id: int,
    user_service: Annotated[UserServiceProtocol, Depends(get_user_service)]
):
    return await user_service.get_user(user_id)
```

### Scoped зависимости
```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def get_db_session():
    """Контекстный менеджер для сессии БД"""
    session = create_session()
    try:
        yield session
    finally:
        await session.close()

async def get_user_repository(
    session = Depends(get_db_session)
) -> UserRepository:
    """Получить репозиторий пользователей"""
    return UserRepository(session)

async def get_user_service(
    user_repo: Annotated[UserRepository, Depends(get_user_repository)]
) -> UserService:
    """Получить сервис пользователей"""
    return UserService(user_repo)

# Использование
@app.post("/users")
async def create_user(
    user_data: UserCreate,
    user_service: Annotated[UserService, Depends(get_user_service)]
):
    return await user_service.create_user(user_data)
```

## Декораторы для DI

### Декоратор для регистрации сервисов
```python
from functools import wraps
from typing import Type, Callable

def injectable(interface: Type[T], lifecycle: Lifecycle = Lifecycle.TRANSIENT):
    """Декоратор для регистрации сервисов"""
    def decorator(cls: Type[T]) -> Type[T]:
        container.register(interface, cls, lifecycle)
        return cls
    return decorator

def singleton(interface: Type[T]):
    """Декоратор для регистрации синглтона"""
    return injectable(interface, Lifecycle.SINGLETON)

def scoped(interface: Type[T]):
    """Декоратор для регистрации scoped сервиса"""
    return injectable(interface, Lifecycle.SCOPED)

# Использование
@singleton(DatabaseProtocol)
class PostgreSQLDatabase:
    pass

@scoped(UserServiceProtocol)
class UserService:
    def __init__(self, database: DatabaseProtocol):
        self.database = database
```

### Декоратор для внедрения зависимостей
```python
def inject(*dependencies: Type):
    """Декоратор для автоматического внедрения зависимостей"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Получение зависимостей из контейнера
            injected_deps = [container.get(dep) for dep in dependencies]
            
            # Вызов функции с внедренными зависимостями
            return func(*args, *injected_deps, **kwargs)
        return wrapper
    return decorator

# Использование
@inject(DatabaseProtocol, UserServiceProtocol)
def process_user_data(user_id: int, database: DatabaseProtocol, user_service: UserServiceProtocol):
    return user_service.get_user(user_id)
```

## Конфигурация через DI

### Конфигурируемые сервисы
```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class DatabaseConfig:
    host: str
    port: int
    username: str
    password: str
    database: str

@dataclass
class CacheConfig:
    host: str
    port: int
    ttl: int = 3600

class ConfigurableDatabase:
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self._connection = None
    
    async def connect(self):
        # Подключение с использованием конфигурации
        pass

class ConfigurableCache:
    def __init__(self, config: CacheConfig):
        self.config = config
        self._client = None
    
    async def connect(self):
        # Подключение к кэшу с использованием конфигурации
        pass

# Регистрация конфигурации
container.register_instance(DatabaseConfig, DatabaseConfig(
    host="localhost",
    port=5432,
    username="user",
    password="password",
    database="mydb"
))

container.register_instance(CacheConfig, CacheConfig(
    host="localhost",
    port=6379,
    ttl=3600
))

# Регистрация сервисов с конфигурацией
container.register_factory(DatabaseProtocol, lambda: ConfigurableDatabase(container.get(DatabaseConfig)))
container.register_factory(CacheProtocol, lambda: ConfigurableCache(container.get(CacheConfig)))
```

## Тестирование с DI

### Моки и заглушки
```python
import pytest
from unittest.mock import Mock, AsyncMock

class MockDatabase:
    def __init__(self):
        self.users = {}
        self.next_id = 1
    
    async def get_user(self, user_id: int):
        return self.users.get(user_id)
    
    async def create_user(self, user_data: dict):
        user_id = self.next_id
        self.next_id += 1
        user = {**user_data, 'id': user_id}
        self.users[user_id] = user
        return user

@pytest.fixture
def mock_database():
    return MockDatabase()

@pytest.fixture
def test_container(mock_database):
    container = AdvancedDIContainer()
    container.register_instance(DatabaseProtocol, mock_database)
    container.register(UserServiceProtocol, UserService, Lifecycle.TRANSIENT)
    return container

def test_user_service_with_mock(test_container):
    """Тест с мок базой данных"""
    user_service = test_container.get(UserServiceProtocol)
    
    # Тестирование создания пользователя
    user_data = {"name": "John", "email": "john@example.com"}
    user = await user_service.create_user(user_data)
    
    assert user["name"] == "John"
    assert user["email"] == "john@example.com"
    assert "id" in user

def test_user_service_integration():
    """Интеграционный тест"""
    container = AdvancedDIContainer()
    container.register(DatabaseProtocol, PostgreSQLDatabase, Lifecycle.SINGLETON)
    container.register(UserServiceProtocol, UserService, Lifecycle.SINGLETON)
    
    user_service = container.get(UserServiceProtocol)
    
    # Тестирование с реальной БД
    user_data = {"name": "Jane", "email": "jane@example.com"}
    user = await user_service.create_user(user_data)
    
    assert user.name == "Jane"
    assert user.email == "jane@example.com"
```

### Тестирование с подменой зависимостей
```python
class TestUserService:
    def setup_method(self):
        self.container = AdvancedDIContainer()
        self.mock_database = MockDatabase()
        self.container.register_instance(DatabaseProtocol, self.mock_database)
        self.container.register(UserServiceProtocol, UserService, Lifecycle.TRANSIENT)
    
    def test_get_user_success(self):
        """Тест успешного получения пользователя"""
        # Подготовка данных
        self.mock_database.users[1] = {"id": 1, "name": "John", "email": "john@example.com"}
        
        # Выполнение
        user_service = self.container.get(UserServiceProtocol)
        user = await user_service.get_user(1)
        
        # Проверки
        assert user["name"] == "John"
        assert user["email"] == "john@example.com"
    
    def test_get_user_not_found(self):
        """Тест получения несуществующего пользователя"""
        user_service = self.container.get(UserServiceProtocol)
        user = await user_service.get_user(999)
        
        assert user is None
```

## Лучшие практики

### 1. Использование протоколов
```python
from typing import Protocol

class DatabaseProtocol(Protocol):
    async def get_user(self, user_id: int) -> Optional[User]: ...
    async def create_user(self, user_data: UserCreate) -> User: ...

# Хорошо - использование протокола
class UserService:
    def __init__(self, database: DatabaseProtocol):
        self.database = database

# Плохо - зависимость от конкретного класса
class UserService:
    def __init__(self, database: PostgreSQLDatabase):
        self.database = database
```

### 2. Регистрация в модуле инициализации
```python
# di_container.py
def setup_di_container() -> AdvancedDIContainer:
    """Настройка DI контейнера"""
    container = AdvancedDIContainer()
    
    # Регистрация конфигурации
    container.register_instance(DatabaseConfig, load_database_config())
    container.register_instance(CacheConfig, load_cache_config())
    
    # Регистрация сервисов
    container.register(DatabaseProtocol, PostgreSQLDatabase, Lifecycle.SINGLETON)
    container.register(CacheProtocol, RedisCache, Lifecycle.SINGLETON)
    container.register(UserServiceProtocol, UserService, Lifecycle.SINGLETON)
    
    return container

# main.py
container = setup_di_container()
```

### 3. Валидация зависимостей
```python
class ValidatedDIContainer(AdvancedDIContainer):
    """Контейнер с валидацией зависимостей"""
    
    def validate_dependencies(self) -> None:
        """Валидация всех зарегистрированных зависимостей"""
        for interface, registration in self._registrations.items():
            try:
                # Попытка создания экземпляра для проверки зависимостей
                self._create_instance(interface, registration)
            except Exception as e:
                raise DependencyValidationError(f"Failed to validate {interface}: {e}")

class DependencyValidationError(Exception):
    pass
```

### 4. Логирование DI операций
```python
import logging

class LoggingDIContainer(AdvancedDIContainer):
    """Контейнер с логированием"""
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def get(self, interface: Type[T], scope_id: str = None) -> T:
        self.logger.debug(f"Resolving dependency: {interface}")
        instance = super().get(interface, scope_id)
        self.logger.debug(f"Resolved dependency: {interface} -> {type(instance)}")
        return instance
```

## Антипаттерны

### ❌ Плохо
```python
# Service Locator антипаттерн
class ServiceLocator:
    _services = {}
    
    @staticmethod
    def register(interface, implementation):
        ServiceLocator._services[interface] = implementation
    
    @staticmethod
    def get(interface):
        return ServiceLocator._services[interface]()

# Использование Service Locator
class UserService:
    def get_user(self, user_id):
        database = ServiceLocator.get(DatabaseProtocol)  # Плохо!
        return database.get_user(user_id)

# Скрытые зависимости
class UserService:
    def __init__(self):
        self.database = PostgreSQLDatabase()  # Плохо! Скрытая зависимость
```

### ✅ Хорошо
```python
# Явное внедрение зависимостей
class UserService:
    def __init__(self, database: DatabaseProtocol):
        self.database = database  # Хорошо! Явная зависимость
    
    def get_user(self, user_id):
        return self.database.get_user(user_id)

# Использование DI контейнера
container = AdvancedDIContainer()
container.register(DatabaseProtocol, PostgreSQLDatabase, Lifecycle.SINGLETON)
container.register(UserServiceProtocol, UserService, Lifecycle.SINGLETON)

user_service = container.get(UserServiceProtocol)
```
