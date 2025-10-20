# 🏗️ Service Layer Pattern - Шпаргалка

## Что такое Service Layer Pattern

Service Layer Pattern - это архитектурный паттерн, который инкапсулирует бизнес-логику приложения в отдельном слое, отделяя её от контроллеров (API endpoints) и слоя доступа к данным (репозиториев).

## Зачем нужен Service Layer

### Преимущества:
- **Разделение ответственности** - бизнес-логика отделена от API и данных
- **Переиспользование** - сервисы можно использовать в разных контроллерах
- **Тестируемость** - легко тестировать бизнес-логику изолированно
- **Транзакции** - управление транзакциями на уровне бизнес-операций
- **Валидация** - централизованная валидация бизнес-правил
- **Кэширование** - кэширование на уровне бизнес-операций

## Базовая структура

### Базовый сервис
```python
from abc import ABC, abstractmethod
from typing import Any, Optional
from src.utils.db_manager import DBManager

class BaseService(ABC):
    """Базовый класс для всех сервисов"""
    
    def __init__(self, db: Optional[DBManager] = None):
        self.db = db
    
    async def _validate_business_rules(self, data: Any) -> bool:
        """Валидация бизнес-правил"""
        return True
    
    async def _execute_in_transaction(self, operation):
        """Выполнение операции в транзакции"""
        if self.db:
            async with self.db.transaction():
                return await operation()
        return await operation()
```

### Конкретная реализация сервиса
```python
from datetime import date
from typing import Optional
from src.schemas.hotels import Hotel, HotelAdd, HotelUpdate
from src.exceptions import (
    ObjectNotFoundException,
    ObjectAlreadyExistsException,
    ValidationException
)

class HotelService(BaseService):
    """Сервис для работы с отелями"""
    
    async def get_hotel(self, hotel_id: int) -> Hotel:
        """Получить отель по ID"""
        try:
            return await self.db.hotels.get_one(id=hotel_id)
        except ObjectNotFoundException:
            raise ObjectNotFoundException(f"Hotel with id {hotel_id} not found")
    
    async def get_hotels_by_criteria(
        self,
        location: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        limit: int = 10,
        offset: int = 0
    ) -> list[Hotel]:
        """Получить отели по критериям"""
        # Валидация дат
        if date_from and date_to and date_from >= date_to:
            raise ValidationException("Date from must be before date to")
        
        return await self.db.hotels.get_hotels_by_criteria(
            location=location,
            date_from=date_from,
            date_to=date_to,
            limit=limit,
            offset=offset
        )
    
    async def create_hotel(self, hotel_data: HotelAdd) -> Hotel:
        """Создать новый отель"""
        # Валидация бизнес-правил
        await self._validate_hotel_creation(hotel_data)
        
        # Проверка на существование
        existing_hotel = await self.db.hotels.get_one_or_none(
            title=hotel_data.title,
            location=hotel_data.location
        )
        if existing_hotel:
            raise ObjectAlreadyExistsException("Hotel with this title and location already exists")
        
        # Создание отеля
        hotel = await self.db.hotels.add(hotel_data)
        await self.db.session_commit()
        
        return hotel
    
    async def update_hotel(self, hotel_id: int, hotel_data: HotelUpdate) -> Hotel:
        """Обновить отель"""
        # Проверка существования
        await self.get_hotel(hotel_id)
        
        # Валидация бизнес-правил
        await self._validate_hotel_update(hotel_id, hotel_data)
        
        # Обновление
        hotel = await self.db.hotels.edit(hotel_data, id=hotel_id)
        await self.db.session_commit()
        
        return hotel
    
    async def delete_hotel(self, hotel_id: int) -> None:
        """Удалить отель"""
        # Проверка существования
        hotel = await self.get_hotel(hotel_id)
        
        # Проверка на наличие активных бронирований
        active_bookings = await self.db.bookings.get_active_bookings_for_hotel(hotel_id)
        if active_bookings:
            raise ValidationException("Cannot delete hotel with active bookings")
        
        # Удаление
        await self.db.hotels.delete(id=hotel_id)
        await self.db.session_commit()
    
    async def _validate_hotel_creation(self, hotel_data: HotelAdd) -> None:
        """Валидация при создании отеля"""
        if not hotel_data.title or len(hotel_data.title.strip()) < 2:
            raise ValidationException("Hotel title must be at least 2 characters")
        
        if not hotel_data.location or len(hotel_data.location.strip()) < 5:
            raise ValidationException("Hotel location must be at least 5 characters")
    
    async def _validate_hotel_update(self, hotel_id: int, hotel_data: HotelUpdate) -> None:
        """Валидация при обновлении отеля"""
        if hotel_data.title and len(hotel_data.title.strip()) < 2:
            raise ValidationException("Hotel title must be at least 2 characters")
        
        if hotel_data.location and len(hotel_data.location.strip()) < 5:
            raise ValidationException("Hotel location must be at least 5 characters")
```

## Сложные бизнес-операции

### Сервис с транзакциями
```python
class BookingService(BaseService):
    """Сервис для работы с бронированиями"""
    
    async def create_booking(
        self,
        user_id: int,
        room_id: int,
        date_from: date,
        date_to: date
    ) -> Booking:
        """Создать бронирование с проверками"""
        
        async def _booking_operation():
            # Проверка существования пользователя
            user = await self.db.users.get_one(id=user_id)
            
            # Проверка существования номера
            room = await self.db.rooms.get_one(id=room_id)
            
            # Валидация дат
            await self._validate_booking_dates(date_from, date_to)
            
            # Проверка доступности номера
            await self._check_room_availability(room_id, date_from, date_to)
            
            # Расчет стоимости
            total_cost = await self._calculate_booking_cost(room, date_from, date_to)
            
            # Создание бронирования
            booking_data = BookingCreate(
                user_id=user_id,
                room_id=room_id,
                date_from=date_from,
                date_to=date_to,
                total_cost=total_cost
            )
            
            booking = await self.db.bookings.add(booking_data)
            
            # Отправка уведомления (асинхронно)
            await self._send_booking_notification(booking)
            
            return booking
        
        return await self._execute_in_transaction(_booking_operation)
    
    async def cancel_booking(self, booking_id: int, user_id: int) -> None:
        """Отменить бронирование"""
        
        async def _cancellation_operation():
            # Получение бронирования
            booking = await self.db.bookings.get_one(id=booking_id)
            
            # Проверка прав доступа
            if booking.user_id != user_id:
                raise PermissionError("You can only cancel your own bookings")
            
            # Проверка возможности отмены
            await self._validate_cancellation(booking)
            
            # Отмена бронирования
            await self.db.bookings.cancel(booking_id)
            
            # Возврат средств
            await self._process_refund(booking)
            
            # Уведомление об отмене
            await self._send_cancellation_notification(booking)
        
        await self._execute_in_transaction(_cancellation_operation)
```

### Сервис с кэшированием
```python
import redis
import json
from typing import Optional

class CachedHotelService(HotelService):
    """Сервис отелей с кэшированием"""
    
    def __init__(self, db: DBManager, redis_client: redis.Redis):
        super().__init__(db)
        self.redis = redis_client
        self.cache_ttl = 3600  # 1 час
    
    async def get_hotel(self, hotel_id: int) -> Hotel:
        """Получить отель с кэшированием"""
        cache_key = f"hotel:{hotel_id}"
        
        # Попытка получить из кэша
        cached_data = await self.redis.get(cache_key)
        if cached_data:
            return Hotel.model_validate_json(cached_data)
        
        # Получение из БД
        hotel = await super().get_hotel(hotel_id)
        
        # Сохранение в кэш
        await self.redis.setex(
            cache_key,
            self.cache_ttl,
            hotel.model_dump_json()
        )
        
        return hotel
    
    async def get_hotels_by_criteria(
        self,
        location: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        limit: int = 10,
        offset: int = 0
    ) -> list[Hotel]:
        """Получить отели с кэшированием"""
        cache_key = f"hotels:search:{location}:{date_from}:{date_to}:{limit}:{offset}"
        
        # Попытка получить из кэша
        cached_data = await self.redis.get(cache_key)
        if cached_data:
            hotels_data = json.loads(cached_data)
            return [Hotel.model_validate(hotel) for hotel in hotels_data]
        
        # Получение из БД
        hotels = await super().get_hotels_by_criteria(
            location, date_from, date_to, limit, offset
        )
        
        # Сохранение в кэш
        hotels_data = [hotel.model_dump() for hotel in hotels]
        await self.redis.setex(
            cache_key,
            self.cache_ttl,
            json.dumps(hotels_data)
        )
        
        return hotels
    
    async def create_hotel(self, hotel_data: HotelAdd) -> Hotel:
        """Создать отель с инвалидацией кэша"""
        hotel = await super().create_hotel(hotel_data)
        
        # Инвалидация кэша поиска
        await self._invalidate_search_cache()
        
        return hotel
    
    async def _invalidate_search_cache(self):
        """Инвалидация кэша поиска"""
        pattern = "hotels:search:*"
        keys = await self.redis.keys(pattern)
        if keys:
            await self.redis.delete(*keys)
```

## Сервисы с внешними интеграциями

### Сервис с внешними API
```python
import httpx
from typing import Optional

class PaymentService(BaseService):
    """Сервис для работы с платежами"""
    
    def __init__(self, db: DBManager, payment_api_url: str, api_key: str):
        super().__init__(db)
        self.payment_api_url = payment_api_url
        self.api_key = api_key
    
    async def process_payment(
        self,
        booking_id: int,
        amount: float,
        payment_method: str
    ) -> PaymentResult:
        """Обработать платеж"""
        
        async with httpx.AsyncClient() as client:
            payment_data = {
                "booking_id": booking_id,
                "amount": amount,
                "payment_method": payment_method,
                "api_key": self.api_key
            }
            
            response = await client.post(
                f"{self.payment_api_url}/payments",
                json=payment_data,
                timeout=30.0
            )
            
            if response.status_code == 200:
                payment_result = PaymentResult.model_validate(response.json())
                
                # Сохранение результата платежа
                await self._save_payment_result(booking_id, payment_result)
                
                return payment_result
            else:
                raise PaymentException(f"Payment failed: {response.text}")
    
    async def refund_payment(self, payment_id: str, amount: float) -> RefundResult:
        """Возврат платежа"""
        
        async with httpx.AsyncClient() as client:
            refund_data = {
                "payment_id": payment_id,
                "amount": amount,
                "api_key": self.api_key
            }
            
            response = await client.post(
                f"{self.payment_api_url}/refunds",
                json=refund_data,
                timeout=30.0
            )
            
            if response.status_code == 200:
                return RefundResult.model_validate(response.json())
            else:
                raise PaymentException(f"Refund failed: {response.text}")
```

### Сервис с уведомлениями
```python
from typing import List
import asyncio

class NotificationService(BaseService):
    """Сервис для отправки уведомлений"""
    
    def __init__(self, db: DBManager, email_service, sms_service):
        super().__init__(db)
        self.email_service = email_service
        self.sms_service = sms_service
    
    async def send_booking_confirmation(self, booking: Booking) -> None:
        """Отправить подтверждение бронирования"""
        user = await self.db.users.get_one(id=booking.user_id)
        
        # Подготовка данных для уведомления
        notification_data = {
            "user_name": user.name,
            "hotel_name": booking.hotel.title,
            "room_type": booking.room.title,
            "check_in": booking.date_from,
            "check_out": booking.date_to,
            "total_cost": booking.total_cost
        }
        
        # Отправка email
        await self.email_service.send_booking_confirmation(
            user.email,
            notification_data
        )
        
        # Отправка SMS (если указан телефон)
        if user.phone:
            await self.sms_service.send_booking_confirmation(
                user.phone,
                notification_data
            )
    
    async def send_bulk_notifications(
        self,
        notifications: List[NotificationData]
    ) -> None:
        """Отправить массовые уведомления"""
        
        async def send_notification(notification):
            try:
                if notification.type == "email":
                    await self.email_service.send(notification)
                elif notification.type == "sms":
                    await self.sms_service.send(notification)
            except Exception as e:
                # Логирование ошибки, но не прерывание процесса
                self.logger.error(f"Failed to send notification: {e}")
        
        # Параллельная отправка уведомлений
        tasks = [send_notification(notif) for notif in notifications]
        await asyncio.gather(*tasks, return_exceptions=True)
```

## Сервисы с фоновыми задачами

### Сервис с Celery
```python
from celery import Celery
from typing import Optional

class BackgroundTaskService(BaseService):
    """Сервис для фоновых задач"""
    
    def __init__(self, db: DBManager, celery_app: Celery):
        super().__init__(db)
        self.celery = celery_app
    
    async def schedule_booking_reminder(
        self,
        booking_id: int,
        reminder_time: datetime
    ) -> str:
        """Запланировать напоминание о бронировании"""
        
        # Сохранение задачи в БД
        task_data = TaskData(
            booking_id=booking_id,
            task_type="booking_reminder",
            scheduled_time=reminder_time,
            status="scheduled"
        )
        task = await self.db.tasks.add(task_data)
        await self.db.session_commit()
        
        # Запуск Celery задачи
        celery_task = self.celery.send_task(
            "send_booking_reminder",
            args=[booking_id],
            eta=reminder_time
        )
        
        # Обновление ID задачи Celery
        await self.db.tasks.update(
            task.id,
            TaskUpdate(celery_task_id=celery_task.id)
        )
        await self.db.session_commit()
        
        return celery_task.id
    
    async def process_booking_analytics(self, date_from: date, date_to: date) -> None:
        """Обработать аналитику бронирований"""
        
        # Запуск фоновой задачи
        self.celery.send_task(
            "process_booking_analytics",
            args=[date_from.isoformat(), date_to.isoformat()]
        )
```

## Интеграция с FastAPI

### Dependency Injection для сервисов
```python
from fastapi import Depends
from src.api.dependencies import DBDep

def get_hotel_service(db: DBDep) -> HotelService:
    """Получить сервис отелей"""
    return HotelService(db)

def get_booking_service(db: DBDep) -> BookingService:
    """Получить сервис бронирований"""
    return BookingService(db)

# Использование в endpoints
@app.get("/hotels/{hotel_id}")
async def get_hotel(
    hotel_id: int,
    hotel_service: HotelService = Depends(get_hotel_service)
):
    return await hotel_service.get_hotel(hotel_id)

@app.post("/bookings")
async def create_booking(
    booking_data: BookingCreate,
    booking_service: BookingService = Depends(get_booking_service)
):
    return await booking_service.create_booking(booking_data)
```

### Сервисный менеджер
```python
class ServiceManager:
    """Менеджер для управления всеми сервисами"""
    
    def __init__(self, db: DBManager):
        self.db = db
        self._services = {}
    
    def get_service(self, service_class):
        """Получить сервис (singleton pattern)"""
        if service_class not in self._services:
            self._services[service_class] = service_class(self.db)
        return self._services[service_class]
    
    @property
    def hotels(self) -> HotelService:
        return self.get_service(HotelService)
    
    @property
    def bookings(self) -> BookingService:
        return self.get_service(BookingService)
    
    @property
    def users(self) -> UserService:
        return self.get_service(UserService)

# Использование
async def get_service_manager(db: DBDep) -> ServiceManager:
    return ServiceManager(db)

@app.get("/hotels/{hotel_id}")
async def get_hotel(
    hotel_id: int,
    services: ServiceManager = Depends(get_service_manager)
):
    return await services.hotels.get_hotel(hotel_id)
```

## Тестирование сервисов

### Unit тесты
```python
import pytest
from unittest.mock import AsyncMock, Mock
from src.services.hotels import HotelService
from src.schemas.hotels import HotelAdd

@pytest.fixture
def mock_db_manager():
    """Мок менеджера БД"""
    db = Mock()
    db.hotels = Mock()
    db.session_commit = AsyncMock()
    return db

@pytest.fixture
def hotel_service(mock_db_manager):
    """Сервис отелей с мок БД"""
    return HotelService(mock_db_manager)

@pytest.mark.asyncio
async def test_create_hotel_success(hotel_service, mock_db_manager):
    """Тест успешного создания отеля"""
    # Подготовка данных
    hotel_data = HotelAdd(title="Test Hotel", location="Test Location")
    expected_hotel = Hotel(id=1, title="Test Hotel", location="Test Location")
    
    # Настройка моков
    mock_db_manager.hotels.get_one_or_none.return_value = None
    mock_db_manager.hotels.add.return_value = expected_hotel
    
    # Выполнение
    result = await hotel_service.create_hotel(hotel_data)
    
    # Проверки
    assert result == expected_hotel
    mock_db_manager.hotels.get_one_or_none.assert_called_once_with(
        title="Test Hotel",
        location="Test Location"
    )
    mock_db_manager.hotels.add.assert_called_once_with(hotel_data)
    mock_db_manager.session_commit.assert_called_once()

@pytest.mark.asyncio
async def test_create_hotel_already_exists(hotel_service, mock_db_manager):
    """Тест создания отеля, который уже существует"""
    # Подготовка данных
    hotel_data = HotelAdd(title="Test Hotel", location="Test Location")
    existing_hotel = Hotel(id=1, title="Test Hotel", location="Test Location")
    
    # Настройка моков
    mock_db_manager.hotels.get_one_or_none.return_value = existing_hotel
    
    # Выполнение и проверка исключения
    with pytest.raises(ObjectAlreadyExistsException):
        await hotel_service.create_hotel(hotel_data)
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
async def test_hotel_service_integration(test_db):
    """Интеграционный тест сервиса отелей"""
    db_manager = DBManager(test_db)
    hotel_service = HotelService(db_manager)
    
    # Создание отеля
    hotel_data = HotelAdd(title="Test Hotel", location="Test Location")
    hotel = await hotel_service.create_hotel(hotel_data)
    
    # Проверка создания
    assert hotel.title == "Test Hotel"
    assert hotel.location == "Test Location"
    
    # Получение отеля
    retrieved_hotel = await hotel_service.get_hotel(hotel.id)
    assert retrieved_hotel.title == "Test Hotel"
```

## Лучшие практики

### 1. Единая структура сервисов
```python
class BaseService(ABC):
    """Базовый сервис с общими методами"""
    
    def __init__(self, db: DBManager):
        self.db = db
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def _validate_business_rules(self, data: Any) -> None:
        """Валидация бизнес-правил"""
        pass
    
    async def _execute_in_transaction(self, operation):
        """Выполнение в транзакции"""
        pass
    
    def _log_operation(self, operation: str, **kwargs):
        """Логирование операций"""
        self.logger.info(f"{operation}: {kwargs}")
```

### 2. Обработка ошибок
```python
class HotelService(BaseService):
    async def create_hotel(self, hotel_data: HotelAdd) -> Hotel:
        try:
            self._log_operation("create_hotel", title=hotel_data.title)
            
            # Валидация
            await self._validate_hotel_creation(hotel_data)
            
            # Бизнес-логика
            hotel = await self._create_hotel_impl(hotel_data)
            
            self._log_operation("create_hotel_success", hotel_id=hotel.id)
            return hotel
            
        except ValidationException as e:
            self.logger.warning(f"Validation error in create_hotel: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error in create_hotel: {e}")
            raise ServiceException(f"Failed to create hotel: {str(e)}") from e
```

### 3. Кэширование
```python
class CachedService(BaseService):
    """Сервис с кэшированием"""
    
    def __init__(self, db: DBManager, cache_client):
        super().__init__(db)
        self.cache = cache_client
        self.cache_ttl = 3600
    
    async def _get_cached_or_compute(
        self,
        cache_key: str,
        compute_func,
        *args,
        **kwargs
    ):
        """Получить из кэша или вычислить"""
        cached = await self.cache.get(cache_key)
        if cached:
            return json.loads(cached)
        
        result = await compute_func(*args, **kwargs)
        await self.cache.setex(
            cache_key,
            self.cache_ttl,
            json.dumps(result)
        )
        return result
```

### 4. Мониторинг и метрики
```python
import time
from functools import wraps

def monitor_service_method(func):
    """Декоратор для мониторинга методов сервиса"""
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        start_time = time.time()
        try:
            result = await func(self, *args, **kwargs)
            execution_time = time.time() - start_time
            
            # Логирование метрик
            self.logger.info(
                f"Service method {func.__name__} completed",
                extra={
                    "method": func.__name__,
                    "execution_time": execution_time,
                    "success": True
                }
            )
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(
                f"Service method {func.__name__} failed",
                extra={
                    "method": func.__name__,
                    "execution_time": execution_time,
                    "success": False,
                    "error": str(e)
                }
            )
            raise
    return wrapper

class HotelService(BaseService):
    @monitor_service_method
    async def create_hotel(self, hotel_data: HotelAdd) -> Hotel:
        # ... реализация
        pass
```

## Антипаттерны

### ❌ Плохо
```python
# Смешивание ответственности
class HotelService(BaseService):
    async def create_hotel_with_email(self, hotel_data: HotelAdd):
        # Создание отеля
        hotel = await self.db.hotels.add(hotel_data)
        
        # Отправка email (не должно быть в сервисе отелей)
        await self.email_service.send_hotel_created_email(hotel)
        
        return hotel

# Прямая работа с HTTP в сервисе
class HotelService(BaseService):
    async def create_hotel(self, hotel_data: HotelAdd):
        # Прямая работа с HTTP запросами
        response = requests.post("https://api.example.com/hotels", json=hotel_data.dict())
        return response.json()
```

### ✅ Хорошо
```python
# Разделение ответственности
class HotelService(BaseService):
    async def create_hotel(self, hotel_data: HotelAdd) -> Hotel:
        return await self.db.hotels.add(hotel_data)

class HotelNotificationService(BaseService):
    async def send_hotel_created_notification(self, hotel: Hotel):
        await self.email_service.send_hotel_created_email(hotel)

# Использование в контроллере
@app.post("/hotels")
async def create_hotel(
    hotel_data: HotelAdd,
    hotel_service: HotelService = Depends(get_hotel_service),
    notification_service: HotelNotificationService = Depends(get_notification_service)
):
    hotel = await hotel_service.create_hotel(hotel_data)
    await notification_service.send_hotel_created_notification(hotel)
    return hotel
```
