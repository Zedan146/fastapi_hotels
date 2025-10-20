# 🗺️ Data Mapper Pattern - Шпаргалка

## Что такое Data Mapper Pattern

Data Mapper Pattern - это паттерн проектирования, который обеспечивает разделение между объектами домена и логикой доступа к данным. Он инкапсулирует логику преобразования данных между различными представлениями (ORM модели, Pydantic схемы, DTO).

## Зачем нужен Data Mapper

### Преимущества:
- **Разделение ответственности** - отделяет логику преобразования данных от бизнес-логики
- **Гибкость** - легко изменять представления данных без изменения бизнес-логики
- **Тестируемость** - можно тестировать преобразования данных изолированно
- **Переиспользование** - мапперы можно использовать в разных частях приложения
- **Валидация** - централизованная валидация при преобразовании данных
- **Производительность** - оптимизация преобразований данных

## Базовая структура

### Абстрактный базовый маппер
```python
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Type, Any
from pydantic import BaseModel
from sqlalchemy.orm import DeclarativeBase

# Типы для generic маппера
DBModel = TypeVar("DBModel", bound=DeclarativeBase)
SchemaType = TypeVar("SchemaType", bound=BaseModel)

class DataMapper(ABC, Generic[DBModel, SchemaType]):
    """Базовый класс для всех мапперов данных"""
    
    # Должны быть определены в наследниках
    db_model: Type[DBModel] = None
    schema: Type[SchemaType] = None
    
    @classmethod
    @abstractmethod
    def map_to_domain_entity(cls, data: Any) -> SchemaType:
        """Преобразовать данные из ORM модели в доменную сущность"""
        pass
    
    @classmethod
    @abstractmethod
    def map_to_persistence_entity(cls, data: Any) -> DBModel:
        """Преобразовать данные из доменной сущности в ORM модель"""
        pass
    
    @classmethod
    def map_list_to_domain_entities(cls, data_list: list[Any]) -> list[SchemaType]:
        """Преобразовать список данных в доменные сущности"""
        return [cls.map_to_domain_entity(item) for item in data_list]
    
    @classmethod
    def map_list_to_persistence_entities(cls, data_list: list[Any]) -> list[DBModel]:
        """Преобразовать список данных в ORM модели"""
        return [cls.map_to_persistence_entity(item) for item in data_list]
```

### Конкретная реализация маппера
```python
from src.models.users import UsersModel
from src.schemas.users import User, UserCreate, UserUpdate

class UserDataMapper(DataMapper[UsersModel, User]):
    """Маппер для пользователей"""
    
    db_model = UsersModel
    schema = User
    
    @classmethod
    def map_to_domain_entity(cls, user_model: UsersModel) -> User:
        """Преобразовать ORM модель пользователя в доменную сущность"""
        return User(
            id=user_model.id,
            name=user_model.name,
            email=user_model.email,
            is_active=user_model.is_active,
            created_at=user_model.created_at,
            updated_at=user_model.updated_at
        )
    
    @classmethod
    def map_to_persistence_entity(cls, user_data: UserCreate) -> UsersModel:
        """Преобразовать доменную сущность в ORM модель"""
        return UsersModel(
            name=user_data.name,
            email=user_data.email,
            is_active=user_data.is_active
        )
    
    @classmethod
    def map_update_to_persistence_entity(
        cls, 
        user_model: UsersModel, 
        update_data: UserUpdate
    ) -> UsersModel:
        """Обновить ORM модель данными из доменной сущности"""
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(user_model, field, value)
        return user_model
```

## Сложные мапперы

### Маппер с вложенными объектами
```python
from src.models.hotels import HotelsModel
from src.models.rooms import RoomsModel
from src.schemas.hotels import Hotel, HotelWithRooms
from src.schemas.rooms import Room

class HotelDataMapper(DataMapper[HotelsModel, Hotel]):
    """Базовый маппер для отелей"""
    
    db_model = HotelsModel
    schema = Hotel
    
    @classmethod
    def map_to_domain_entity(cls, hotel_model: HotelsModel) -> Hotel:
        return Hotel(
            id=hotel_model.id,
            title=hotel_model.title,
            location=hotel_model.location,
            rating=hotel_model.rating,
            created_at=hotel_model.created_at
        )

class HotelWithRoomsDataMapper(DataMapper[HotelsModel, HotelWithRooms]):
    """Маппер для отелей с номерами"""
    
    db_model = HotelsModel
    schema = HotelWithRooms
    
    @classmethod
    def map_to_domain_entity(cls, hotel_model: HotelsModel) -> HotelWithRooms:
        # Преобразование отеля
        hotel_data = HotelDataMapper.map_to_domain_entity(hotel_model)
        
        # Преобразование номеров
        rooms = []
        if hasattr(hotel_model, 'rooms') and hotel_model.rooms:
            rooms = [RoomDataMapper.map_to_domain_entity(room) for room in hotel_model.rooms]
        
        return HotelWithRooms(
            id=hotel_data.id,
            title=hotel_data.title,
            location=hotel_data.location,
            rating=hotel_data.rating,
            created_at=hotel_data.created_at,
            rooms=rooms
        )
```

### Маппер с вычисляемыми полями
```python
from datetime import date, timedelta

class BookingDataMapper(DataMapper[BookingsModel, Booking]):
    """Маппер для бронирований с вычисляемыми полями"""
    
    db_model = BookingsModel
    schema = Booking
    
    @classmethod
    def map_to_domain_entity(cls, booking_model: BookingsModel) -> Booking:
        # Вычисление количества ночей
        nights = (booking_model.date_to - booking_model.date_from).days
        
        # Вычисление общей стоимости
        total_cost = booking_model.price_per_night * nights
        
        # Проверка, является ли бронирование активным
        is_active = booking_model.date_from > date.today()
        
        return Booking(
            id=booking_model.id,
            user_id=booking_model.user_id,
            room_id=booking_model.room_id,
            date_from=booking_model.date_from,
            date_to=booking_model.date_to,
            price_per_night=booking_model.price_per_night,
            nights=nights,
            total_cost=total_cost,
            is_active=is_active,
            created_at=booking_model.created_at
        )
```

### Маппер с валидацией
```python
from pydantic import ValidationError
import logging

class ValidatedDataMapper(DataMapper[DBModel, SchemaType]):
    """Маппер с валидацией данных"""
    
    @classmethod
    def map_to_domain_entity(cls, data: Any) -> SchemaType:
        """Преобразование с валидацией"""
        try:
            return cls.schema.model_validate(data, from_attributes=True)
        except ValidationError as e:
            logging.error(f"Validation error in {cls.__name__}: {e}")
            raise DataMappingException(f"Failed to map data to {cls.schema.__name__}: {e}")
    
    @classmethod
    def map_to_persistence_entity(cls, data: Any) -> DBModel:
        """Преобразование с валидацией"""
        try:
            if isinstance(data, BaseModel):
                return cls.db_model(**data.model_dump())
            else:
                return cls.db_model(**data)
        except Exception as e:
            logging.error(f"Mapping error in {cls.__name__}: {e}")
            raise DataMappingException(f"Failed to map data to {cls.db_model.__name__}: {e}")
```

## Специализированные мапперы

### Маппер для API ответов
```python
from typing import Optional
from src.schemas.api import APIResponse, PaginatedResponse

class APIResponseMapper:
    """Маппер для API ответов"""
    
    @staticmethod
    def map_success_response(data: Any, message: str = "Success") -> APIResponse:
        """Преобразовать данные в успешный API ответ"""
        return APIResponse(
            success=True,
            message=message,
            data=data
        )
    
    @staticmethod
    def map_error_response(error: str, status_code: int = 400) -> APIResponse:
        """Преобразовать ошибку в API ответ"""
        return APIResponse(
            success=False,
            message=error,
            data=None,
            status_code=status_code
        )
    
    @staticmethod
    def map_paginated_response(
        data: list[Any],
        page: int,
        per_page: int,
        total: int,
        message: str = "Success"
    ) -> PaginatedResponse:
        """Преобразовать данные в пагинированный ответ"""
        return PaginatedResponse(
            success=True,
            message=message,
            data=data,
            pagination={
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page
            }
        )
```

### Маппер для кэширования
```python
import json
from typing import Any, Dict

class CacheDataMapper:
    """Маппер для работы с кэшем"""
    
    @staticmethod
    def serialize_for_cache(data: Any) -> str:
        """Сериализовать данные для кэша"""
        if isinstance(data, BaseModel):
            return data.model_dump_json()
        elif isinstance(data, (list, dict)):
            return json.dumps(data, default=str)
        else:
            return json.dumps(data, default=str)
    
    @staticmethod
    def deserialize_from_cache(cached_data: str, target_type: Type[SchemaType]) -> SchemaType:
        """Десериализовать данные из кэша"""
        data_dict = json.loads(cached_data)
        return target_type.model_validate(data_dict)
    
    @staticmethod
    def create_cache_key(prefix: str, **kwargs) -> str:
        """Создать ключ кэша"""
        key_parts = [prefix]
        for k, v in sorted(kwargs.items()):
            if v is not None:
                key_parts.append(f"{k}:{v}")
        return ":".join(key_parts)
```

### Маппер для внешних API
```python
from typing import Dict, Any

class ExternalAPIMapper:
    """Маппер для работы с внешними API"""
    
    @staticmethod
    def map_to_external_format(data: BaseModel, api_version: str = "v1") -> Dict[str, Any]:
        """Преобразовать данные в формат внешнего API"""
        if api_version == "v1":
            return {
                "id": data.id,
                "name": data.name,
                "email": data.email,
                "created_at": data.created_at.isoformat()
            }
        elif api_version == "v2":
            return {
                "user_id": data.id,
                "full_name": data.name,
                "email_address": data.email,
                "registration_date": data.created_at.isoformat(),
                "status": "active" if data.is_active else "inactive"
            }
        else:
            raise ValueError(f"Unsupported API version: {api_version}")
    
    @staticmethod
    def map_from_external_format(external_data: Dict[str, Any], api_version: str = "v1") -> BaseModel:
        """Преобразовать данные из формата внешнего API"""
        if api_version == "v1":
            return UserCreate(
                name=external_data["name"],
                email=external_data["email"]
            )
        elif api_version == "v2":
            return UserCreate(
                name=external_data["full_name"],
                email=external_data["email_address"]
            )
        else:
            raise ValueError(f"Unsupported API version: {api_version}")
```

## Мапперы с конфигурацией

### Конфигурируемый маппер
```python
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class MappingConfig:
    """Конфигурация маппера"""
    include_relations: bool = False
    include_computed_fields: bool = True
    field_mappings: Dict[str, str] = None
    exclude_fields: set = None
    
    def __post_init__(self):
        if self.field_mappings is None:
            self.field_mappings = {}
        if self.exclude_fields is None:
            self.exclude_fields = set()

class ConfigurableDataMapper(DataMapper[DBModel, SchemaType]):
    """Маппер с конфигурацией"""
    
    @classmethod
    def map_to_domain_entity(
        cls, 
        data: Any, 
        config: Optional[MappingConfig] = None
    ) -> SchemaType:
        """Преобразование с конфигурацией"""
        if config is None:
            config = MappingConfig()
        
        # Применение маппинга полей
        if config.field_mappings:
            data = cls._apply_field_mappings(data, config.field_mappings)
        
        # Исключение полей
        if config.exclude_fields:
            data = cls._exclude_fields(data, config.exclude_fields)
        
        # Включение связанных данных
        if config.include_relations:
            data = cls._include_relations(data)
        
        return cls.schema.model_validate(data, from_attributes=True)
    
    @classmethod
    def _apply_field_mappings(cls, data: Any, mappings: Dict[str, str]) -> Any:
        """Применить маппинг полей"""
        # Реализация маппинга полей
        pass
    
    @classmethod
    def _exclude_fields(cls, data: Any, exclude_fields: set) -> Any:
        """Исключить поля"""
        # Реализация исключения полей
        pass
    
    @classmethod
    def _include_relations(cls, data: Any) -> Any:
        """Включить связанные данные"""
        # Реализация включения связанных данных
        pass
```

## Мапперы с кэшированием

### Кэшируемый маппер
```python
import hashlib
import json
from typing import Any, Optional

class CachedDataMapper(DataMapper[DBModel, SchemaType]):
    """Маппер с кэшированием преобразований"""
    
    def __init__(self, cache_client, ttl: int = 3600):
        self.cache = cache_client
        self.ttl = ttl
    
    def _get_cache_key(self, data: Any, operation: str) -> str:
        """Получить ключ кэша"""
        data_hash = hashlib.md5(
            json.dumps(data, default=str, sort_keys=True).encode()
        ).hexdigest()
        return f"mapper:{self.__class__.__name__}:{operation}:{data_hash}"
    
    async def map_to_domain_entity_cached(self, data: Any) -> SchemaType:
        """Преобразование с кэшированием"""
        cache_key = self._get_cache_key(data, "to_domain")
        
        # Попытка получить из кэша
        cached_result = await self.cache.get(cache_key)
        if cached_result:
            return self.schema.model_validate_json(cached_result)
        
        # Преобразование
        result = self.map_to_domain_entity(data)
        
        # Сохранение в кэш
        await self.cache.setex(
            cache_key,
            self.ttl,
            result.model_dump_json()
        )
        
        return result
    
    async def invalidate_cache(self, pattern: str = "*"):
        """Инвалидация кэша"""
        keys = await self.cache.keys(f"mapper:{self.__class__.__name__}:{pattern}")
        if keys:
            await self.cache.delete(*keys)
```

## Интеграция с репозиториями

### Использование в репозитории
```python
class UserRepository(BaseRepository):
    """Репозиторий с использованием маппера"""
    
    def __init__(self, session):
        super().__init__(session)
        self.mapper = UserDataMapper
    
    async def get_by_id(self, user_id: int) -> User:
        """Получить пользователя по ID"""
        query = select(UsersModel).where(UsersModel.id == user_id)
        result = await self.session.execute(query)
        user_model = result.scalars().one_or_none()
        
        if not user_model:
            raise ObjectNotFoundException(f"User with id {user_id} not found")
        
        return self.mapper.map_to_domain_entity(user_model)
    
    async def create(self, user_data: UserCreate) -> User:
        """Создать пользователя"""
        user_model = self.mapper.map_to_persistence_entity(user_data)
        
        self.session.add(user_model)
        await self.session.commit()
        await self.session.refresh(user_model)
        
        return self.mapper.map_to_domain_entity(user_model)
    
    async def get_all(self) -> list[User]:
        """Получить всех пользователей"""
        query = select(UsersModel)
        result = await self.session.execute(query)
        user_models = result.scalars().all()
        
        return self.mapper.map_list_to_domain_entities(user_models)
```

## Тестирование мапперов

### Unit тесты
```python
import pytest
from datetime import datetime
from src.models.users import UsersModel
from src.schemas.users import User, UserCreate
from src.repositories.mappers.mappers import UserDataMapper

def test_map_to_domain_entity():
    """Тест преобразования ORM модели в доменную сущность"""
    # Подготовка данных
    user_model = UsersModel(
        id=1,
        name="John Doe",
        email="john@example.com",
        is_active=True,
        created_at=datetime.now()
    )
    
    # Выполнение
    user = UserDataMapper.map_to_domain_entity(user_model)
    
    # Проверки
    assert user.id == 1
    assert user.name == "John Doe"
    assert user.email == "john@example.com"
    assert user.is_active is True

def test_map_to_persistence_entity():
    """Тест преобразования доменной сущности в ORM модель"""
    # Подготовка данных
    user_data = UserCreate(
        name="Jane Doe",
        email="jane@example.com",
        is_active=True
    )
    
    # Выполнение
    user_model = UserDataMapper.map_to_persistence_entity(user_data)
    
    # Проверки
    assert user_model.name == "Jane Doe"
    assert user_model.email == "jane@example.com"
    assert user_model.is_active is True
    assert user_model.id is None  # ID не должен быть установлен

def test_map_list_to_domain_entities():
    """Тест преобразования списка ORM моделей"""
    # Подготовка данных
    user_models = [
        UsersModel(id=1, name="User 1", email="user1@example.com"),
        UsersModel(id=2, name="User 2", email="user2@example.com")
    ]
    
    # Выполнение
    users = UserDataMapper.map_list_to_domain_entities(user_models)
    
    # Проверки
    assert len(users) == 2
    assert users[0].name == "User 1"
    assert users[1].name == "User 2"
```

### Интеграционные тесты
```python
@pytest.mark.asyncio
async def test_mapper_integration_with_repository(test_db):
    """Интеграционный тест маппера с репозиторием"""
    user_repo = UserRepository(test_db)
    
    # Создание пользователя
    user_data = UserCreate(name="Test User", email="test@example.com")
    user = await user_repo.create(user_data)
    
    # Проверка, что маппер работает корректно
    assert user.name == "Test User"
    assert user.email == "test@example.com"
    
    # Получение пользователя
    retrieved_user = await user_repo.get_by_id(user.id)
    assert retrieved_user.name == user.name
    assert retrieved_user.email == user.email
```

## Лучшие практики

### 1. Единообразие мапперов
```python
# Хорошо - единообразный интерфейс
class BaseDataMapper(ABC):
    @classmethod
    @abstractmethod
    def map_to_domain_entity(cls, data: Any) -> SchemaType:
        pass
    
    @classmethod
    @abstractmethod
    def map_to_persistence_entity(cls, data: Any) -> DBModel:
        pass

# Плохо - разные интерфейсы
class UserMapper:
    def to_domain(self, data): pass  # Другое название

class HotelMapper:
    def convert_to_domain(self, data): pass  # Другое название
```

### 2. Обработка ошибок
```python
class DataMapper(ABC):
    @classmethod
    def map_to_domain_entity(cls, data: Any) -> SchemaType:
        try:
            return cls.schema.model_validate(data, from_attributes=True)
        except ValidationError as e:
            raise DataMappingException(f"Failed to map data: {e}")
        except Exception as e:
            raise DataMappingException(f"Unexpected mapping error: {e}")
```

### 3. Логирование
```python
import logging

class DataMapper(ABC):
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @classmethod
    def map_to_domain_entity(cls, data: Any) -> SchemaType:
        cls.logger.debug(f"Mapping data to {cls.schema.__name__}")
        try:
            result = cls.schema.model_validate(data, from_attributes=True)
            cls.logger.debug("Mapping completed successfully")
            return result
        except Exception as e:
            cls.logger.error(f"Mapping failed: {e}")
            raise
```

### 4. Производительность
```python
class OptimizedDataMapper(DataMapper[DBModel, SchemaType]):
    """Оптимизированный маппер для больших объемов данных"""
    
    @classmethod
    def map_batch_to_domain_entities(cls, data_list: list[Any]) -> list[SchemaType]:
        """Пакетное преобразование для лучшей производительности"""
        # Предварительная валидация
        validated_data = []
        for data in data_list:
            try:
                validated_data.append(cls.schema.model_validate(data, from_attributes=True))
            except ValidationError as e:
                cls.logger.warning(f"Validation error in batch mapping: {e}")
                continue
        
        return validated_data
```

## Антипаттерны

### ❌ Плохо
```python
# Смешивание бизнес-логики с маппингом
class UserMapper:
    def map_to_domain_entity(self, user_model):
        user = User(
            id=user_model.id,
            name=user_model.name,
            email=user_model.email
        )
        # Бизнес-логика в маппере
        if user.email.endswith("@admin.com"):
            user.is_admin = True
        return user

# Прямое обращение к БД в маппере
class UserMapper:
    def map_to_domain_entity(self, user_model):
        # Прямое обращение к БД
        bookings = session.query(Booking).filter(Booking.user_id == user_model.id).all()
        return UserWithBookings(user_model, bookings)
```

### ✅ Хорошо
```python
# Только преобразование данных
class UserMapper:
    @classmethod
    def map_to_domain_entity(cls, user_model: UsersModel) -> User:
        return User(
            id=user_model.id,
            name=user_model.name,
            email=user_model.email,
            is_active=user_model.is_active
        )

# Бизнес-логика в сервисе
class UserService:
    def get_user_with_admin_status(self, user_id: int):
        user = self.user_repo.get_by_id(user_id)
        if user.email.endswith("@admin.com"):
            user.is_admin = True
        return user
```
