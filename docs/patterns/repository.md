# 🗄️ Repository Pattern - Шпаргалка

## Что такое Repository Pattern

Repository Pattern - это паттерн проектирования, который инкапсулирует логику доступа к данным и обеспечивает более объектно-ориентированный взгляд на слой персистентности.

## Зачем нужен Repository Pattern

### Преимущества:
- **Разделение ответственности** - отделяет бизнес-логику от логики доступа к данным
- **Тестируемость** - легко создавать моки для тестирования
- **Гибкость** - можно легко менять источники данных
- **Единообразие** - стандартизирует доступ к данным
- **Кэширование** - легко добавить кэширование на уровне репозитория

## Базовая структура

### Абстрактный базовый репозиторий
```python
from typing import Sequence, Any
from abc import ABC, abstractmethod
from sqlalchemy import select, insert, update, delete
from sqlalchemy.exc import NoResultFound, IntegrityError
from pydantic import BaseModel

class BaseRepository(ABC):
    """Базовый репозиторий с общими операциями CRUD"""
    
    def __init__(self, session):
        self.session = session
    
    @abstractmethod
    def get_model(self):
        """Возвращает модель SQLAlchemy"""
        pass
    
    @abstractmethod
    def get_schema(self):
        """Возвращает Pydantic схему"""
        pass
    
    async def get_all(self):
        """Получить все записи"""
        query = select(self.get_model())
        result = await self.session.execute(query)
        return [self.get_schema().model_validate(row) for row in result.scalars().all()]
    
    async def get_by_id(self, id: int):
        """Получить запись по ID"""
        query = select(self.get_model()).where(self.get_model().id == id)
        result = await self.session.execute(query)
        row = result.scalars().one_or_none()
        if not row:
            raise ObjectNotFoundException(f"Object with id {id} not found")
        return self.get_schema().model_validate(row)
    
    async def create(self, data: BaseModel):
        """Создать новую запись"""
        try:
            stmt = insert(self.get_model()).values(data.model_dump()).returning(self.get_model())
            result = await self.session.execute(stmt)
            row = result.scalars().one()
            return self.get_schema().model_validate(row)
        except IntegrityError as e:
            raise ObjectAlreadyExistsException("Object already exists") from e
    
    async def update(self, id: int, data: BaseModel):
        """Обновить запись"""
        stmt = (
            update(self.get_model())
            .where(self.get_model().id == id)
            .values(data.model_dump(exclude_unset=True))
            .returning(self.get_model())
        )
        result = await self.session.execute(stmt)
        row = result.scalars().one_or_none()
        if not row:
            raise ObjectNotFoundException(f"Object with id {id} not found")
        return self.get_schema().model_validate(row)
    
    async def delete(self, id: int):
        """Удалить запись"""
        stmt = delete(self.get_model()).where(self.get_model().id == id)
        result = await self.session.execute(stmt)
        if result.rowcount == 0:
            raise ObjectNotFoundException(f"Object with id {id} not found")
```

### Конкретная реализация репозитория
```python
from src.models.users import UsersModel
from src.schemas.users import User, UserCreate, UserUpdate

class UserRepository(BaseRepository):
    """Репозиторий для работы с пользователями"""
    
    def get_model(self):
        return UsersModel
    
    def get_schema(self):
        return User
    
    async def get_by_email(self, email: str):
        """Получить пользователя по email"""
        query = select(UsersModel).where(UsersModel.email == email)
        result = await self.session.execute(query)
        row = result.scalars().one_or_none()
        if not row:
            return None
        return User.model_validate(row)
    
    async def get_active_users(self):
        """Получить всех активных пользователей"""
        query = select(UsersModel).where(UsersModel.is_active == True)
        result = await self.session.execute(query)
        return [User.model_validate(row) for row in result.scalars().all()]
    
    async def search_users(self, search_term: str, limit: int = 10):
        """Поиск пользователей по имени или email"""
        query = (
            select(UsersModel)
            .where(
                or_(
                    UsersModel.name.ilike(f"%{search_term}%"),
                    UsersModel.email.ilike(f"%{search_term}%")
                )
            )
            .limit(limit)
        )
        result = await self.session.execute(query)
        return [User.model_validate(row) for row in result.scalars().all()]
```

## Продвинутые техники

### Репозиторий с фильтрацией
```python
from typing import Optional, Dict, Any
from sqlalchemy import and_, or_

class FilterableRepository(BaseRepository):
    """Репозиторий с поддержкой фильтрации"""
    
    async def get_filtered(
        self,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ):
        """Получить записи с фильтрацией"""
        query = select(self.get_model())
        
        # Применение фильтров
        if filters:
            conditions = []
            for field, value in filters.items():
                if hasattr(self.get_model(), field):
                    if isinstance(value, list):
                        conditions.append(getattr(self.get_model(), field).in_(value))
                    else:
                        conditions.append(getattr(self.get_model(), field) == value)
            if conditions:
                query = query.where(and_(*conditions))
        
        # Сортировка
        if order_by:
            if order_by.startswith('-'):
                order_field = getattr(self.get_model(), order_by[1:])
                query = query.order_by(order_field.desc())
            else:
                order_field = getattr(self.get_model(), order_by)
                query = query.order_by(order_field)
        
        # Пагинация
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
        
        result = await self.session.execute(query)
        return [self.get_schema().model_validate(row) for row in result.scalars().all()]
```

### Репозиторий с кэшированием
```python
import redis
import json
from typing import Optional

class CachedRepository(BaseRepository):
    """Репозиторий с кэшированием"""
    
    def __init__(self, session, redis_client: redis.Redis, cache_ttl: int = 3600):
        super().__init__(session)
        self.redis = redis_client
        self.cache_ttl = cache_ttl
    
    def _get_cache_key(self, method: str, **kwargs) -> str:
        """Генерация ключа кэша"""
        key_parts = [self.__class__.__name__, method]
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}:{v}")
        return ":".join(key_parts)
    
    async def get_by_id_cached(self, id: int):
        """Получить по ID с кэшированием"""
        cache_key = self._get_cache_key("get_by_id", id=id)
        
        # Попытка получить из кэша
        cached_data = self.redis.get(cache_key)
        if cached_data:
            return self.get_schema().model_validate(json.loads(cached_data))
        
        # Получение из БД
        result = await self.get_by_id(id)
        
        # Сохранение в кэш
        self.redis.setex(
            cache_key,
            self.cache_ttl,
            json.dumps(result.model_dump())
        )
        
        return result
    
    async def invalidate_cache(self, pattern: str = "*"):
        """Очистка кэша по паттерну"""
        keys = self.redis.keys(f"{self.__class__.__name__}:{pattern}")
        if keys:
            self.redis.delete(*keys)
```

### Репозиторий с транзакциями
```python
from contextlib import asynccontextmanager

class TransactionalRepository(BaseRepository):
    """Репозиторий с поддержкой транзакций"""
    
    @asynccontextmanager
    async def transaction(self):
        """Контекстный менеджер для транзакций"""
        try:
            yield self
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise
    
    async def bulk_create(self, data_list: list[BaseModel]):
        """Массовое создание записей в транзакции"""
        async with self.transaction():
            for data in data_list:
                await self.create(data)
    
    async def bulk_update(self, updates: list[tuple[int, BaseModel]]):
        """Массовое обновление записей в транзакции"""
        async with self.transaction():
            for id, data in updates:
                await self.update(id, data)
```

## Специализированные репозитории

### Репозиторий для связанных данных
```python
class HotelRepository(BaseRepository):
    """Репозиторий для отелей с связанными данными"""
    
    async def get_hotel_with_rooms(self, hotel_id: int):
        """Получить отель с номерами"""
        query = (
            select(HotelsModel)
            .options(joinedload(HotelsModel.rooms))
            .where(HotelsModel.id == hotel_id)
        )
        result = await self.session.execute(query)
        hotel = result.scalars().one_or_none()
        if not hotel:
            raise ObjectNotFoundException(f"Hotel with id {hotel_id} not found")
        return HotelWithRooms.model_validate(hotel)
    
    async def get_hotels_by_location(self, location: str):
        """Получить отели по местоположению"""
        query = (
            select(HotelsModel)
            .where(HotelsModel.location.ilike(f"%{location}%"))
            .order_by(HotelsModel.rating.desc())
        )
        result = await self.session.execute(query)
        return [Hotel.model_validate(row) for row in result.scalars().all()]
```

### Репозиторий для агрегации
```python
from sqlalchemy import func

class BookingRepository(BaseRepository):
    """Репозиторий для бронирований с агрегацией"""
    
    async def get_booking_stats(self, date_from, date_to):
        """Получить статистику бронирований"""
        query = (
            select(
                func.count(BookingsModel.id).label('total_bookings'),
                func.sum(BookingsModel.total_cost).label('total_revenue'),
                func.avg(BookingsModel.total_cost).label('avg_booking_value')
            )
            .where(
                and_(
                    BookingsModel.date_from >= date_from,
                    BookingsModel.date_to <= date_to
                )
            )
        )
        result = await self.session.execute(query)
        return result.first()
    
    async def get_popular_rooms(self, limit: int = 10):
        """Получить популярные номера"""
        query = (
            select(
                RoomsModel.id,
                RoomsModel.title,
                func.count(BookingsModel.id).label('booking_count')
            )
            .join(BookingsModel)
            .group_by(RoomsModel.id, RoomsModel.title)
            .order_by(func.count(BookingsModel.id).desc())
            .limit(limit)
        )
        result = await self.session.execute(query)
        return [dict(row) for row in result.all()]
```

## Интеграция с FastAPI

### Dependency Injection
```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

async def get_user_repository(session: AsyncSession = Depends(get_db_session)):
    """Получить репозиторий пользователей"""
    return UserRepository(session)

# Использование в endpoint
@app.get("/users/{user_id}")
async def get_user(
    user_id: int,
    user_repo: UserRepository = Depends(get_user_repository)
):
    return await user_repo.get_by_id(user_id)
```

### Менеджер репозиториев
```python
class RepositoryManager:
    """Менеджер для управления всеми репозиториями"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self._repositories = {}
    
    def get_repository(self, repo_class):
        """Получить репозиторий (singleton pattern)"""
        if repo_class not in self._repositories:
            self._repositories[repo_class] = repo_class(self.session)
        return self._repositories[repo_class]
    
    @property
    def users(self):
        return self.get_repository(UserRepository)
    
    @property
    def hotels(self):
        return self.get_repository(HotelRepository)
    
    @property
    def bookings(self):
        return self.get_repository(BookingRepository)

# Использование
async def get_repo_manager(session: AsyncSession = Depends(get_db_session)):
    return RepositoryManager(session)

@app.get("/users/{user_id}")
async def get_user(
    user_id: int,
    repo_manager: RepositoryManager = Depends(get_repo_manager)
):
    return await repo_manager.users.get_by_id(user_id)
```

## Тестирование репозиториев

### Моки для тестирования
```python
from unittest.mock import AsyncMock, Mock
import pytest

class MockUserRepository:
    """Мок репозитория для тестирования"""
    
    def __init__(self):
        self.users = {}
        self.next_id = 1
    
    async def get_by_id(self, id: int):
        if id not in self.users:
            raise ObjectNotFoundException(f"User with id {id} not found")
        return self.users[id]
    
    async def create(self, data: UserCreate):
        user = User(id=self.next_id, **data.model_dump())
        self.users[self.next_id] = user
        self.next_id += 1
        return user
    
    async def get_by_email(self, email: str):
        for user in self.users.values():
            if user.email == email:
                return user
        return None

@pytest.fixture
def mock_user_repository():
    return MockUserRepository()

def test_get_user_by_id(mock_user_repository):
    # Создание тестового пользователя
    user_data = UserCreate(name="John", email="john@example.com")
    user = await mock_user_repository.create(user_data)
    
    # Тестирование получения
    retrieved_user = await mock_user_repository.get_by_id(user.id)
    assert retrieved_user.name == "John"
    assert retrieved_user.email == "john@example.com"
```

### Интеграционные тесты
```python
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

@pytest.fixture
async def test_db():
    """Тестовая база данных"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    Base.metadata.create_all(engine)
    
    async_session = sessionmaker(engine, class_=AsyncSession)
    async with async_session() as session:
        yield session
    
    await engine.dispose()

@pytest.mark.asyncio
async def test_user_repository_integration(test_db):
    """Интеграционный тест репозитория пользователей"""
    repo = UserRepository(test_db)
    
    # Создание пользователя
    user_data = UserCreate(name="John", email="john@example.com")
    user = await repo.create(user_data)
    await test_db.commit()
    
    # Получение пользователя
    retrieved_user = await repo.get_by_id(user.id)
    assert retrieved_user.name == "John"
    assert retrieved_user.email == "john@example.com"
```

## Лучшие практики

### 1. Единообразие интерфейса
```python
# Хорошо - единообразный интерфейс
class BaseRepository(ABC):
    async def get_by_id(self, id: int): pass
    async def create(self, data: BaseModel): pass
    async def update(self, id: int, data: BaseModel): pass
    async def delete(self, id: int): pass

# Плохо - разные интерфейсы для разных репозиториев
class UserRepository:
    async def find_user(self, id: int): pass  # Другое название

class HotelRepository:
    async def get_hotel(self, id: int): pass  # Другое название
```

### 2. Обработка ошибок
```python
class BaseRepository(ABC):
    async def get_by_id(self, id: int):
        try:
            # ... получение данных
            return result
        except NoResultFound:
            raise ObjectNotFoundException(f"Object with id {id} not found")
        except IntegrityError as e:
            raise DataIntegrityError("Data integrity violation") from e
        except Exception as e:
            raise RepositoryError(f"Repository error: {str(e)}") from e
```

### 3. Логирование
```python
import logging

class BaseRepository(ABC):
    def __init__(self, session):
        self.session = session
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def create(self, data: BaseModel):
        self.logger.info(f"Creating new {self.__class__.__name__}")
        try:
            result = await self._create_impl(data)
            self.logger.info(f"Successfully created {self.__class__.__name__}")
            return result
        except Exception as e:
            self.logger.error(f"Failed to create {self.__class__.__name__}: {e}")
            raise
```

### 4. Валидация данных
```python
class BaseRepository(ABC):
    async def create(self, data: BaseModel):
        # Валидация перед сохранением
        if not self._validate_data(data):
            raise ValidationError("Invalid data provided")
        
        return await self._create_impl(data)
    
    def _validate_data(self, data: BaseModel) -> bool:
        """Валидация данных перед сохранением"""
        # Кастомная валидация
        return True
```

### 5. Кэширование стратегии
```python
class CachedRepository(BaseRepository):
    def __init__(self, session, cache_strategy="write_through"):
        super().__init__(session)
        self.cache_strategy = cache_strategy
    
    async def create(self, data: BaseModel):
        result = await super().create(data)
        
        if self.cache_strategy == "write_through":
            # Обновляем кэш сразу
            await self._update_cache(result)
        elif self.cache_strategy == "write_behind":
            # Обновляем кэш асинхронно
            asyncio.create_task(self._update_cache(result))
        
        return result
```

## Антипаттерны

### ❌ Плохо
```python
# Смешивание бизнес-логики с доступом к данным
class UserRepository:
    async def create_user_with_notification(self, data: UserCreate):
        user = await self.create(data)
        # Бизнес-логика в репозитории
        await send_welcome_email(user.email)
        return user

# Прямое использование SQL
class UserRepository:
    async def get_users(self):
        query = "SELECT * FROM users WHERE is_active = true"
        # Прямой SQL вместо ORM
        return await self.session.execute(query)
```

### ✅ Хорошо
```python
# Только доступ к данным
class UserRepository:
    async def create(self, data: UserCreate):
        return await self._create_impl(data)
    
    async def get_active_users(self):
        query = select(UsersModel).where(UsersModel.is_active == True)
        result = await self.session.execute(query)
        return [User.model_validate(row) for row in result.scalars().all()]

# Бизнес-логика в сервисном слое
class UserService:
    def __init__(self, user_repo: UserRepository, email_service: EmailService):
        self.user_repo = user_repo
        self.email_service = email_service
    
    async def create_user_with_notification(self, data: UserCreate):
        user = await self.user_repo.create(data)
        await self.email_service.send_welcome_email(user.email)
        return user
```
