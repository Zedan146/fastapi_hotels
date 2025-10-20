# 🏭 Factory Pattern - Шпаргалка

## Что такое Factory Pattern

Factory Pattern - это паттерн проектирования, который предоставляет интерфейс для создания объектов без указания их конкретных классов. Фабрика инкапсулирует логику создания объектов и может возвращать различные типы объектов в зависимости от переданных параметров.

## Зачем нужен Factory Pattern

### Преимущества:
- **Инкапсуляция создания** - логика создания объектов скрыта от клиента
- **Гибкость** - легко добавлять новые типы объектов
- **Разделение ответственности** - создание объектов отделено от их использования
- **Конфигурируемость** - можно настраивать создание объектов через конфигурацию
- **Тестируемость** - легко подставлять моки для тестирования

## Типы Factory Pattern

### 1. Simple Factory (Простая фабрика)
```python
from abc import ABC, abstractmethod
from enum import Enum

class DatabaseType(Enum):
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"

class Database(ABC):
    @abstractmethod
    def connect(self):
        pass
    
    @abstractmethod
    def execute_query(self, query: str):
        pass

class PostgreSQLDatabase(Database):
    def connect(self):
        print("Connecting to PostgreSQL")
    
    def execute_query(self, query: str):
        print(f"Executing PostgreSQL query: {query}")

class MySQLDatabase(Database):
    def connect(self):
        print("Connecting to MySQL")
    
    def execute_query(self, query: str):
        print(f"Executing MySQL query: {query}")

class SQLiteDatabase(Database):
    def connect(self):
        print("Connecting to SQLite")
    
    def execute_query(self, query: str):
        print(f"Executing SQLite query: {query}")

class DatabaseFactory:
    """Простая фабрика для создания баз данных"""
    
    @staticmethod
    def create_database(db_type: DatabaseType) -> Database:
        if db_type == DatabaseType.POSTGRESQL:
            return PostgreSQLDatabase()
        elif db_type == DatabaseType.MYSQL:
            return MySQLDatabase()
        elif db_type == DatabaseType.SQLITE:
            return SQLiteDatabase()
        else:
            raise ValueError(f"Unsupported database type: {db_type}")

# Использование
db = DatabaseFactory.create_database(DatabaseType.POSTGRESQL)
db.connect()
```

### 2. Factory Method (Фабричный метод)
```python
from abc import ABC, abstractmethod

class DatabaseFactory(ABC):
    """Абстрактная фабрика баз данных"""
    
    @abstractmethod
    def create_database(self) -> Database:
        pass
    
    def get_connection_string(self) -> str:
        """Общий метод для получения строки подключения"""
        db = self.create_database()
        return f"Connected to {type(db).__name__}"

class PostgreSQLFactory(DatabaseFactory):
    def create_database(self) -> Database:
        return PostgreSQLDatabase()

class MySQLFactory(DatabaseFactory):
    def create_database(self) -> Database:
        return MySQLDatabase()

class SQLiteFactory(DatabaseFactory):
    def create_database(self) -> Database:
        return SQLiteDatabase()

# Использование
postgres_factory = PostgreSQLFactory()
db = postgres_factory.create_database()
```

### 3. Abstract Factory (Абстрактная фабрика)
```python
from abc import ABC, abstractmethod

class Database(ABC):
    @abstractmethod
    def connect(self): pass

class Cache(ABC):
    @abstractmethod
    def get(self, key: str): pass

class PostgreSQLDatabase(Database):
    def connect(self):
        print("Connecting to PostgreSQL")

class RedisCache(Cache):
    def get(self, key: str):
        print(f"Getting from Redis: {key}")

class MySQLDatabase(Database):
    def connect(self):
        print("Connecting to MySQL")

class MemcachedCache(Cache):
    def get(self, key: str):
        print(f"Getting from Memcached: {key}")

class DatabaseFactory(ABC):
    """Абстрактная фабрика для создания семейства объектов"""
    
    @abstractmethod
    def create_database(self) -> Database:
        pass
    
    @abstractmethod
    def create_cache(self) -> Cache:
        pass

class PostgreSQLFactory(DatabaseFactory):
    def create_database(self) -> Database:
        return PostgreSQLDatabase()
    
    def create_cache(self) -> Cache:
        return RedisCache()

class MySQLFactory(DatabaseFactory):
    def create_database(self) -> Database:
        return MySQLDatabase()
    
    def create_cache(self) -> Cache:
        return MemcachedCache()

# Использование
factory = PostgreSQLFactory()
db = factory.create_database()
cache = factory.create_cache()
```

## Factory Pattern в FastAPI проекте

### Фабрика для создания сервисов
```python
from typing import Protocol, Type, Dict, Any
from src.services.base import BaseService
from src.utils.db_manager import DBManager

class ServiceFactory:
    """Фабрика для создания сервисов"""
    
    def __init__(self, db_manager: DBManager):
        self.db_manager = db_manager
        self._service_cache: Dict[Type, BaseService] = {}
    
    def create_service(self, service_class: Type[BaseService]) -> BaseService:
        """Создать сервис с кэшированием"""
        if service_class not in self._service_cache:
            self._service_cache[service_class] = service_class(self.db_manager)
        return self._service_cache[service_class]
    
    def get_hotel_service(self):
        """Получить сервис отелей"""
        from src.services.hotels import HotelService
        return self.create_service(HotelService)
    
    def get_user_service(self):
        """Получить сервис пользователей"""
        from src.services.users import UserService
        return self.create_service(UserService)
    
    def get_booking_service(self):
        """Получить сервис бронирований"""
        from src.services.bookings import BookingService
        return self.create_service(BookingService)

# Использование в FastAPI
def get_service_factory(db: DBDep) -> ServiceFactory:
    return ServiceFactory(db)

@app.get("/hotels/{hotel_id}")
async def get_hotel(
    hotel_id: int,
    service_factory: ServiceFactory = Depends(get_service_factory)
):
    hotel_service = service_factory.get_hotel_service()
    return await hotel_service.get_hotel(hotel_id)
```

### Фабрика для создания репозиториев
```python
from src.repositories.base import BaseRepository
from src.repositories.hotels import HotelsRepository
from src.repositories.users import UsersRepository
from src.repositories.bookings import BookingsRepository

class RepositoryFactory:
    """Фабрика для создания репозиториев"""
    
    def __init__(self, session):
        self.session = session
        self._repositories: Dict[Type, BaseRepository] = {}
    
    def create_repository(self, repo_class: Type[BaseRepository]) -> BaseRepository:
        """Создать репозиторий"""
        if repo_class not in self._repositories:
            self._repositories[repo_class] = repo_class(self.session)
        return self._repositories[repo_class]
    
    @property
    def hotels(self) -> HotelsRepository:
        return self.create_repository(HotelsRepository)
    
    @property
    def users(self) -> UsersRepository:
        return self.create_repository(UsersRepository)
    
    @property
    def bookings(self) -> BookingsRepository:
        return self.create_repository(BookingsRepository)
```

### Фабрика для создания мапперов
```python
from src.repositories.mappers.mappers import (
    HotelDataMapper,
    UserDataMapper,
    BookingDataMapper
)

class MapperFactory:
    """Фабрика для создания мапперов"""
    
    _mappers = {
        'hotel': HotelDataMapper,
        'user': UserDataMapper,
        'booking': BookingDataMapper,
    }
    
    @classmethod
    def create_mapper(cls, mapper_type: str):
        """Создать маппер по типу"""
        if mapper_type not in cls._mappers:
            raise ValueError(f"Unknown mapper type: {mapper_type}")
        return cls._mappers[mapper_type]
    
    @classmethod
    def get_hotel_mapper(cls):
        return cls.create_mapper('hotel')
    
    @classmethod
    def get_user_mapper(cls):
        return cls.create_mapper('user')
    
    @classmethod
    def get_booking_mapper(cls):
        return cls.create_mapper('booking')
```

## Конфигурируемые фабрики

### Фабрика с конфигурацией
```python
from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class DatabaseConfig:
    host: str
    port: int
    username: str
    password: str
    database: str
    pool_size: int = 10

@dataclass
class CacheConfig:
    host: str
    port: int
    ttl: int = 3600
    max_connections: int = 100

class ConfigurableDatabaseFactory:
    """Конфигурируемая фабрика баз данных"""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
    
    def create_database(self) -> Database:
        """Создать базу данных с конфигурацией"""
        return PostgreSQLDatabase(
            host=self.config.host,
            port=self.config.port,
            username=self.config.username,
            password=self.config.password,
            database=self.config.database,
            pool_size=self.config.pool_size
        )

class ConfigurableCacheFactory:
    """Конфигурируемая фабрика кэша"""
    
    def __init__(self, config: CacheConfig):
        self.config = config
    
    def create_cache(self) -> Cache:
        """Создать кэш с конфигурацией"""
        return RedisCache(
            host=self.config.host,
            port=self.config.port,
            ttl=self.config.ttl,
            max_connections=self.config.max_connections
        )

# Использование
db_config = DatabaseConfig(
    host="localhost",
    port=5432,
    username="user",
    password="password",
    database="hotels_db"
)

cache_config = CacheConfig(
    host="localhost",
    port=6379,
    ttl=3600
)

db_factory = ConfigurableDatabaseFactory(db_config)
cache_factory = ConfigurableCacheFactory(cache_config)

database = db_factory.create_database()
cache = cache_factory.create_cache()
```

### Фабрика с регистрацией
```python
from typing import Callable, Type, Dict, Any

class RegistryFactory:
    """Фабрика с регистрацией типов"""
    
    def __init__(self):
        self._creators: Dict[str, Callable] = {}
        self._instances: Dict[str, Any] = {}
    
    def register(self, name: str, creator: Callable, singleton: bool = False):
        """Зарегистрировать создатель"""
        self._creators[name] = creator
        if singleton:
            self._instances[name] = None
    
    def create(self, name: str, *args, **kwargs) -> Any:
        """Создать объект по имени"""
        if name not in self._creators:
            raise ValueError(f"Unknown type: {name}")
        
        # Проверка синглтона
        if name in self._instances and self._instances[name] is not None:
            return self._instances[name]
        
        creator = self._creators[name]
        instance = creator(*args, **kwargs)
        
        # Сохранение синглтона
        if name in self._instances:
            self._instances[name] = instance
        
        return instance

# Использование
factory = RegistryFactory()

# Регистрация создателей
factory.register('postgresql', lambda: PostgreSQLDatabase(), singleton=True)
factory.register('mysql', lambda: MySQLDatabase(), singleton=True)
factory.register('redis', lambda: RedisCache(), singleton=True)

# Создание объектов
db = factory.create('postgresql')
cache = factory.create('redis')
```

## Фабрика для создания API клиентов

### Фабрика внешних API
```python
from abc import ABC, abstractmethod
import httpx
from typing import Dict, Any

class APIClient(ABC):
    @abstractmethod
    async def get(self, url: str, **kwargs): pass
    
    @abstractmethod
    async def post(self, url: str, data: Dict[str, Any], **kwargs): pass

class PaymentAPIClient(APIClient):
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        self.client = httpx.AsyncClient()
    
    async def get(self, url: str, **kwargs):
        headers = {'Authorization': f'Bearer {self.api_key}'}
        return await self.client.get(f"{self.base_url}{url}", headers=headers, **kwargs)
    
    async def post(self, url: str, data: Dict[str, Any], **kwargs):
        headers = {'Authorization': f'Bearer {self.api_key}'}
        return await self.client.post(f"{self.base_url}{url}", json=data, headers=headers, **kwargs)

class EmailAPIClient(APIClient):
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        self.client = httpx.AsyncClient()
    
    async def get(self, url: str, **kwargs):
        headers = {'X-API-Key': self.api_key}
        return await self.client.get(f"{self.base_url}{url}", headers=headers, **kwargs)
    
    async def post(self, url: str, data: Dict[str, Any], **kwargs):
        headers = {'X-API-Key': self.api_key}
        return await self.client.post(f"{self.base_url}{url}", json=data, headers=headers, **kwargs)

class APIClientFactory:
    """Фабрика для создания API клиентов"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    def create_payment_client(self) -> PaymentAPIClient:
        return PaymentAPIClient(
            base_url=self.config['payment_api']['base_url'],
            api_key=self.config['payment_api']['api_key']
        )
    
    def create_email_client(self) -> EmailAPIClient:
        return EmailAPIClient(
            base_url=self.config['email_api']['base_url'],
            api_key=self.config['email_api']['api_key']
        )
```

## Фабрика для создания задач Celery

### Фабрика фоновых задач
```python
from celery import Celery
from typing import Dict, Any, Callable
from dataclasses import dataclass

@dataclass
class TaskConfig:
    name: str
    queue: str = 'default'
    priority: int = 0
    retry_count: int = 3
    retry_delay: int = 60

class TaskFactory:
    """Фабрика для создания Celery задач"""
    
    def __init__(self, celery_app: Celery):
        self.celery_app = celery_app
        self._task_configs: Dict[str, TaskConfig] = {}
    
    def register_task(self, config: TaskConfig, func: Callable):
        """Зарегистрировать задачу"""
        self._task_configs[config.name] = config
        
        # Декорирование функции
        task = self.celery_app.task(
            name=config.name,
            queue=config.queue,
            priority=config.priority,
            autoretry_for=(Exception,),
            retry_kwargs={'max_retries': config.retry_count, 'countdown': config.retry_delay}
        )(func)
        
        return task
    
    def create_task(self, task_name: str, *args, **kwargs):
        """Создать задачу"""
        if task_name not in self._task_configs:
            raise ValueError(f"Unknown task: {task_name}")
        
        return self.celery_app.send_task(task_name, args=args, kwargs=kwargs)

# Использование
celery_app = Celery('hotels')

task_factory = TaskFactory(celery_app)

# Регистрация задач
@task_factory.register_task(
    TaskConfig(
        name='send_booking_email',
        queue='email',
        priority=5
    )
)
async def send_booking_email_task(booking_id: int, user_email: str):
    # Логика отправки email
    pass

@task_factory.register_task(
    TaskConfig(
        name='process_payment',
        queue='payment',
        priority=10
    )
)
async def process_payment_task(payment_data: dict):
    # Логика обработки платежа
    pass

# Создание задач
task_factory.create_task('send_booking_email', booking_id=1, user_email='user@example.com')
task_factory.create_task('process_payment', payment_data={'amount': 100})
```

## Тестирование фабрик

### Unit тесты
```python
import pytest
from unittest.mock import Mock, patch

def test_database_factory():
    """Тест фабрики баз данных"""
    # Тест PostgreSQL
    db = DatabaseFactory.create_database(DatabaseType.POSTGRESQL)
    assert isinstance(db, PostgreSQLDatabase)
    
    # Тест MySQL
    db = DatabaseFactory.create_database(DatabaseType.MYSQL)
    assert isinstance(db, MySQLDatabase)
    
    # Тест неизвестного типа
    with pytest.raises(ValueError):
        DatabaseFactory.create_database("unknown")

def test_service_factory():
    """Тест фабрики сервисов"""
    mock_db = Mock()
    factory = ServiceFactory(mock_db)
    
    # Тест создания сервиса
    hotel_service = factory.get_hotel_service()
    assert hotel_service is not None
    
    # Тест кэширования
    hotel_service2 = factory.get_hotel_service()
    assert hotel_service is hotel_service2  # Тот же объект

def test_configurable_factory():
    """Тест конфигурируемой фабрики"""
    config = DatabaseConfig(
        host="test_host",
        port=5432,
        username="test_user",
        password="test_pass",
        database="test_db"
    )
    
    factory = ConfigurableDatabaseFactory(config)
    db = factory.create_database()
    
    assert db.host == "test_host"
    assert db.port == 5432
    assert db.username == "test_user"
```

### Интеграционные тесты
```python
@pytest.mark.asyncio
async def test_factory_integration():
    """Интеграционный тест фабрики"""
    # Создание реальных объектов
    db_config = DatabaseConfig(
        host="localhost",
        port=5432,
        username="test",
        password="test",
        database="test_db"
    )
    
    factory = ConfigurableDatabaseFactory(db_config)
    db = factory.create_database()
    
    # Тест подключения
    await db.connect()
    assert db.is_connected()
```

## Лучшие практики

### 1. Использование протоколов
```python
from typing import Protocol

class DatabaseFactoryProtocol(Protocol):
    def create_database(self) -> Database: ...

# Хорошо - использование протокола
def use_database_factory(factory: DatabaseFactoryProtocol):
    db = factory.create_database()
    return db
```

### 2. Валидация конфигурации
```python
class ValidatedFactory:
    def __init__(self, config: Dict[str, Any]):
        self._validate_config(config)
        self.config = config
    
    def _validate_config(self, config: Dict[str, Any]):
        """Валидация конфигурации"""
        required_fields = ['host', 'port', 'username', 'password']
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required field: {field}")
```

### 3. Логирование создания объектов
```python
import logging

class LoggingFactory:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def create_database(self, db_type: str) -> Database:
        self.logger.info(f"Creating database of type: {db_type}")
        db = self._create_database_impl(db_type)
        self.logger.info(f"Database created successfully: {type(db).__name__}")
        return db
```

### 4. Обработка ошибок
```python
class SafeFactory:
    def create_database(self, db_type: str) -> Database:
        try:
            return self._create_database_impl(db_type)
        except Exception as e:
            logging.error(f"Failed to create database {db_type}: {e}")
            raise DatabaseCreationError(f"Failed to create {db_type} database") from e
```

## Антипаттерны

### ❌ Плохо
```python
# Слишком много if-else
class BadFactory:
    def create_database(self, db_type: str):
        if db_type == "postgresql":
            return PostgreSQLDatabase()
        elif db_type == "mysql":
            return MySQLDatabase()
        elif db_type == "sqlite":
            return SQLiteDatabase()
        elif db_type == "oracle":
            return OracleDatabase()
        # ... много условий

# Смешивание ответственности
class BadFactory:
    def create_database(self, db_type: str):
        db = self._create_db(db_type)
        db.connect()  # Не должно быть в фабрике
        return db
```

### ✅ Хорошо
```python
# Использование словаря для маппинга
class GoodFactory:
    _creators = {
        'postgresql': PostgreSQLDatabase,
        'mysql': MySQLDatabase,
        'sqlite': SQLiteDatabase,
    }
    
    def create_database(self, db_type: str) -> Database:
        if db_type not in self._creators:
            raise ValueError(f"Unknown database type: {db_type}")
        return self._creators[db_type]()

# Разделение ответственности
class GoodFactory:
    def create_database(self, db_type: str) -> Database:
        return self._create_db(db_type)
    
    def _create_db(self, db_type: str) -> Database:
        # Только создание объекта
        pass
```
