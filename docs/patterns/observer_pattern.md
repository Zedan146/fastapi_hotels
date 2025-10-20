# 👁️ Observer Pattern - Шпаргалка

## Что такое Observer Pattern

Observer Pattern - это паттерн проектирования, который определяет зависимость "один ко многим" между объектами. Когда один объект (Subject) изменяет свое состояние, все зависимые объекты (Observers) уведомляются и обновляются автоматически.

## Зачем нужен Observer Pattern

### Преимущества:
- **Слабая связанность** - Subject и Observer не знают друг о друге напрямую
- **Динамические отношения** - можно добавлять и удалять наблюдателей во время выполнения
- **Расширяемость** - легко добавлять новые типы наблюдателей
- **Реактивность** - автоматическое обновление при изменении состояния
- **Разделение ответственности** - Subject фокусируется на данных, Observer - на представлении

## Базовая структура

### Абстрактные классы
```python
from abc import ABC, abstractmethod
from typing import List, Any
import asyncio

class Observer(ABC):
    """Абстрактный наблюдатель"""
    
    @abstractmethod
    async def update(self, subject: 'Subject', event_data: Any = None):
        """Обновить наблюдателя при изменении субъекта"""
        pass

class Subject(ABC):
    """Абстрактный субъект"""
    
    def __init__(self):
        self._observers: List[Observer] = []
    
    def attach(self, observer: Observer):
        """Добавить наблюдателя"""
        if observer not in self._observers:
            self._observers.append(observer)
    
    def detach(self, observer: Observer):
        """Удалить наблюдателя"""
        if observer in self._observers:
            self._observers.remove(observer)
    
    async def notify(self, event_data: Any = None):
        """Уведомить всех наблюдателей"""
        tasks = []
        for observer in self._observers:
            task = asyncio.create_task(observer.update(self, event_data))
            tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
```

### Конкретные реализации
```python
from typing import Dict, Any, Optional
from datetime import datetime

class Hotel(Subject):
    """Отель как субъект для наблюдателей"""
    
    def __init__(self, hotel_id: int, name: str, location: str):
        super().__init__()
        self.hotel_id = hotel_id
        self.name = name
        self.location = location
        self.rating: Optional[float] = None
        self.price_range: Optional[tuple] = None
        self.availability: bool = True
    
    async def update_rating(self, new_rating: float):
        """Обновить рейтинг отеля"""
        old_rating = self.rating
        self.rating = new_rating
        
        event_data = {
            'event_type': 'rating_updated',
            'hotel_id': self.hotel_id,
            'old_rating': old_rating,
            'new_rating': new_rating,
            'timestamp': datetime.now()
        }
        
        await self.notify(event_data)
    
    async def update_availability(self, is_available: bool):
        """Обновить доступность отеля"""
        old_availability = self.availability
        self.availability = is_available
        
        event_data = {
            'event_type': 'availability_updated',
            'hotel_id': self.hotel_id,
            'old_availability': old_availability,
            'new_availability': is_available,
            'timestamp': datetime.now()
        }
        
        await self.notify(event_data)
    
    async def update_price_range(self, new_price_range: tuple):
        """Обновить ценовой диапазон"""
        old_price_range = self.price_range
        self.price_range = new_price_range
        
        event_data = {
            'event_type': 'price_updated',
            'hotel_id': self.hotel_id,
            'old_price_range': old_price_range,
            'new_price_range': new_price_range,
            'timestamp': datetime.now()
        }
        
        await self.notify(event_data)

class EmailNotificationObserver(Observer):
    """Наблюдатель для отправки email уведомлений"""
    
    def __init__(self, email_service):
        self.email_service = email_service
        self.subscribed_events = ['rating_updated', 'availability_updated']
    
    async def update(self, subject: Hotel, event_data: Any = None):
        if event_data and event_data.get('event_type') in self.subscribed_events:
            await self._send_email_notification(subject, event_data)
    
    async def _send_email_notification(self, hotel: Hotel, event_data: Dict[str, Any]):
        """Отправить email уведомление"""
        event_type = event_data['event_type']
        
        if event_type == 'rating_updated':
            subject = f"Hotel {hotel.name} rating updated"
            body = f"The rating for {hotel.name} has been updated to {event_data['new_rating']}"
        elif event_type == 'availability_updated':
            subject = f"Hotel {hotel.name} availability changed"
            body = f"The availability for {hotel.name} is now {event_data['new_availability']}"
        else:
            return
        
        # Отправка email (здесь была бы реальная логика)
        print(f"Email sent: {subject} - {body}")

class LoggingObserver(Observer):
    """Наблюдатель для логирования событий"""
    
    def __init__(self, logger):
        self.logger = logger
    
    async def update(self, subject: Hotel, event_data: Any = None):
        if event_data:
            self.logger.info(f"Hotel event: {event_data}")
    
    async def _log_event(self, hotel: Hotel, event_data: Dict[str, Any]):
        """Логировать событие"""
        self.logger.info(
            f"Hotel {hotel.name} (ID: {hotel.hotel_id}) - "
            f"Event: {event_data['event_type']} at {event_data['timestamp']}"
        )

class CacheUpdateObserver(Observer):
    """Наблюдатель для обновления кэша"""
    
    def __init__(self, cache_service):
        self.cache_service = cache_service
    
    async def update(self, subject: Hotel, event_data: Any = None):
        if event_data:
            # Инвалидация кэша при изменении данных
            cache_key = f"hotel:{subject.hotel_id}"
            await self.cache_service.invalidate(cache_key)
            
            # Обновление кэша новыми данными
            await self.cache_service.set(cache_key, {
                'hotel_id': subject.hotel_id,
                'name': subject.name,
                'location': subject.location,
                'rating': subject.rating,
                'availability': subject.availability,
                'price_range': subject.price_range
            })
```

## Observer Pattern в FastAPI проекте

### Система событий для бронирований
```python
from enum import Enum
from typing import Dict, Any, List
from dataclasses import dataclass

class BookingEventType(Enum):
    CREATED = "booking_created"
    CANCELLED = "booking_cancelled"
    MODIFIED = "booking_modified"
    CONFIRMED = "booking_confirmed"
    CHECKED_IN = "booking_checked_in"
    CHECKED_OUT = "booking_checked_out"

@dataclass
class BookingEvent:
    event_type: BookingEventType
    booking_id: int
    user_id: int
    hotel_id: int
    room_id: int
    timestamp: datetime
    data: Dict[str, Any]

class Booking(Subject):
    """Бронирование как субъект"""
    
    def __init__(self, booking_id: int, user_id: int, hotel_id: int, room_id: int):
        super().__init__()
        self.booking_id = booking_id
        self.user_id = user_id
        self.hotel_id = hotel_id
        self.room_id = room_id
        self.status = "pending"
        self.check_in_date = None
        self.check_out_date = None
        self.total_cost = 0
    
    async def create(self, check_in_date, check_out_date, total_cost):
        """Создать бронирование"""
        self.check_in_date = check_in_date
        self.check_out_date = check_out_date
        self.total_cost = total_cost
        self.status = "created"
        
        event = BookingEvent(
            event_type=BookingEventType.CREATED,
            booking_id=self.booking_id,
            user_id=self.user_id,
            hotel_id=self.hotel_id,
            room_id=self.room_id,
            timestamp=datetime.now(),
            data={
                'check_in_date': check_in_date.isoformat(),
                'check_out_date': check_out_date.isoformat(),
                'total_cost': total_cost
            }
        )
        
        await self.notify(event)
    
    async def cancel(self, reason: str = None):
        """Отменить бронирование"""
        old_status = self.status
        self.status = "cancelled"
        
        event = BookingEvent(
            event_type=BookingEventType.CANCELLED,
            booking_id=self.booking_id,
            user_id=self.user_id,
            hotel_id=self.hotel_id,
            room_id=self.room_id,
            timestamp=datetime.now(),
            data={
                'old_status': old_status,
                'new_status': self.status,
                'reason': reason
            }
        )
        
        await self.notify(event)
    
    async def confirm(self):
        """Подтвердить бронирование"""
        old_status = self.status
        self.status = "confirmed"
        
        event = BookingEvent(
            event_type=BookingEventType.CONFIRMED,
            booking_id=self.booking_id,
            user_id=self.user_id,
            hotel_id=self.hotel_id,
            room_id=self.room_id,
            timestamp=datetime.now(),
            data={
                'old_status': old_status,
                'new_status': self.status
            }
        )
        
        await self.notify(event)
```

### Наблюдатели для бронирований
```python
class BookingEmailObserver(Observer):
    """Наблюдатель для отправки email при событиях бронирования"""
    
    def __init__(self, email_service, user_service):
        self.email_service = email_service
        self.user_service = user_service
    
    async def update(self, subject: Booking, event_data: BookingEvent = None):
        if not event_data:
            return
        
        # Получение данных пользователя
        user = await self.user_service.get_user(event_data.user_id)
        if not user:
            return
        
        # Отправка email в зависимости от типа события
        if event_data.event_type == BookingEventType.CREATED:
            await self._send_booking_confirmation(user.email, event_data)
        elif event_data.event_type == BookingEventType.CANCELLED:
            await self._send_cancellation_notification(user.email, event_data)
        elif event_data.event_type == BookingEventType.CONFIRMED:
            await self._send_confirmation_notification(user.email, event_data)
    
    async def _send_booking_confirmation(self, email: str, event: BookingEvent):
        subject = "Booking Confirmation"
        body = f"""
        Your booking has been created successfully!
        
        Booking ID: {event.booking_id}
        Check-in: {event.data['check_in_date']}
        Check-out: {event.data['check_out_date']}
        Total Cost: ${event.data['total_cost']}
        """
        await self.email_service.send_email(email, subject, body)
    
    async def _send_cancellation_notification(self, email: str, event: BookingEvent):
        subject = "Booking Cancelled"
        body = f"""
        Your booking has been cancelled.
        
        Booking ID: {event.booking_id}
        Reason: {event.data.get('reason', 'No reason provided')}
        """
        await self.email_service.send_email(email, subject, body)

class BookingAnalyticsObserver(Observer):
    """Наблюдатель для аналитики бронирований"""
    
    def __init__(self, analytics_service):
        self.analytics_service = analytics_service
    
    async def update(self, subject: Booking, event_data: BookingEvent = None):
        if not event_data:
            return
        
        # Отправка данных в аналитику
        await self.analytics_service.track_booking_event(event_data)
    
    async def _track_event(self, event: BookingEvent):
        """Отслеживание события в аналитике"""
        analytics_data = {
            'event_type': event.event_type.value,
            'booking_id': event.booking_id,
            'user_id': event.user_id,
            'hotel_id': event.hotel_id,
            'room_id': event.room_id,
            'timestamp': event.timestamp.isoformat(),
            'metadata': event.data
        }
        
        await self.analytics_service.track('booking_event', analytics_data)

class BookingInventoryObserver(Observer):
    """Наблюдатель для управления инвентарем"""
    
    def __init__(self, inventory_service):
        self.inventory_service = inventory_service
    
    async def update(self, subject: Booking, event_data: BookingEvent = None):
        if not event_data:
            return
        
        if event_data.event_type == BookingEventType.CREATED:
            await self._reserve_room(event_data)
        elif event_data.event_type == BookingEventType.CANCELLED:
            await self._release_room(event_data)
        elif event_data.event_type == BookingEventType.CHECKED_IN:
            await self._mark_room_occupied(event_data)
        elif event_data.event_type == BookingEventType.CHECKED_OUT:
            await self._mark_room_available(event_data)
    
    async def _reserve_room(self, event: BookingEvent):
        """Зарезервировать номер"""
        await self.inventory_service.reserve_room(
            event.room_id,
            event.data['check_in_date'],
            event.data['check_out_date']
        )
    
    async def _release_room(self, event: BookingEvent):
        """Освободить номер"""
        await self.inventory_service.release_room(event.room_id)
    
    async def _mark_room_occupied(self, event: BookingEvent):
        """Пометить номер как занятый"""
        await self.inventory_service.mark_room_occupied(event.room_id)
    
    async def _mark_room_available(self, event: BookingEvent):
        """Пометить номер как доступный"""
        await self.inventory_service.mark_room_available(event.room_id)
```

## Event Bus с Observer Pattern

### Централизованная система событий
```python
from typing import Dict, List, Callable, Any
import asyncio
from collections import defaultdict

class EventBus:
    """Централизованная шина событий"""
    
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self._middleware: List[Callable] = []
    
    def subscribe(self, event_type: str, handler: Callable):
        """Подписаться на событие"""
        self._subscribers[event_type].append(handler)
    
    def unsubscribe(self, event_type: str, handler: Callable):
        """Отписаться от события"""
        if handler in self._subscribers[event_type]:
            self._subscribers[event_type].remove(handler)
    
    def add_middleware(self, middleware: Callable):
        """Добавить middleware для обработки событий"""
        self._middleware.append(middleware)
    
    async def publish(self, event_type: str, event_data: Any = None):
        """Опубликовать событие"""
        # Применение middleware
        processed_data = event_data
        for middleware in self._middleware:
            processed_data = await middleware(event_type, processed_data)
        
        # Уведомление подписчиков
        handlers = self._subscribers.get(event_type, [])
        if handlers:
            tasks = []
            for handler in handlers:
                task = asyncio.create_task(handler(processed_data))
                tasks.append(task)
            
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def publish_async(self, event_type: str, event_data: Any = None):
        """Асинхронная публикация события (не блокирующая)"""
        asyncio.create_task(self.publish(event_type, event_data))

# Глобальная шина событий
event_bus = EventBus()

# Middleware для логирования
async def logging_middleware(event_type: str, event_data: Any):
    print(f"Event published: {event_type} - {event_data}")
    return event_data

# Middleware для валидации
async def validation_middleware(event_type: str, event_data: Any):
    if not event_data:
        raise ValueError(f"Event data is required for {event_type}")
    return event_data

# Добавление middleware
event_bus.add_middleware(logging_middleware)
event_bus.add_middleware(validation_middleware)
```

### Использование Event Bus в FastAPI
```python
from fastapi import FastAPI, Depends

app = FastAPI()

# Регистрация обработчиков событий
async def handle_booking_created(event_data):
    print(f"Booking created: {event_data}")

async def handle_booking_cancelled(event_data):
    print(f"Booking cancelled: {event_data}")

async def handle_hotel_updated(event_data):
    print(f"Hotel updated: {event_data}")

# Подписка на события
event_bus.subscribe("booking.created", handle_booking_created)
event_bus.subscribe("booking.cancelled", handle_booking_cancelled)
event_bus.subscribe("hotel.updated", handle_hotel_updated)

@app.post("/bookings")
async def create_booking(booking_data: dict):
    # Создание бронирования
    booking = await booking_service.create_booking(booking_data)
    
    # Публикация события
    await event_bus.publish("booking.created", {
        'booking_id': booking.id,
        'user_id': booking.user_id,
        'hotel_id': booking.hotel_id,
        'created_at': booking.created_at.isoformat()
    })
    
    return booking

@app.delete("/bookings/{booking_id}")
async def cancel_booking(booking_id: int):
    # Отмена бронирования
    await booking_service.cancel_booking(booking_id)
    
    # Публикация события
    await event_bus.publish("booking.cancelled", {
        'booking_id': booking_id,
        'cancelled_at': datetime.now().isoformat()
    })
    
    return {"message": "Booking cancelled"}
```

## Observer Pattern с Celery

### Асинхронная обработка событий
```python
from celery import Celery
from typing import Dict, Any

celery_app = Celery('hotels')

class CeleryEventObserver(Observer):
    """Наблюдатель для отправки событий в Celery"""
    
    def __init__(self, celery_app: Celery):
        self.celery_app = celery_app
    
    async def update(self, subject: Any, event_data: Any = None):
        if event_data:
            # Отправка задачи в Celery
            self.celery_app.send_task(
                'process_event',
                args=[event_data],
                queue='events'
            )

# Celery задачи
@celery_app.task
def process_event(event_data: Dict[str, Any]):
    """Обработка события в фоновом режиме"""
    event_type = event_data.get('event_type')
    
    if event_type == 'booking_created':
        send_booking_notifications.delay(event_data)
        update_analytics.delay(event_data)
    elif event_type == 'hotel_updated':
        update_search_index.delay(event_data)
        invalidate_cache.delay(event_data)

@celery_app.task
def send_booking_notifications(event_data: Dict[str, Any]):
    """Отправка уведомлений о бронировании"""
    # Логика отправки уведомлений
    pass

@celery_app.task
def update_analytics(event_data: Dict[str, Any]):
    """Обновление аналитики"""
    # Логика обновления аналитики
    pass

@celery_app.task
def update_search_index(event_data: Dict[str, Any]):
    """Обновление поискового индекса"""
    # Логика обновления индекса
    pass

@celery_app.task
def invalidate_cache(event_data: Dict[str, Any]):
    """Инвалидация кэша"""
    # Логика инвалидации кэша
    pass
```

## Тестирование Observer Pattern

### Unit тесты
```python
import pytest
from unittest.mock import Mock, AsyncMock

@pytest.mark.asyncio
async def test_hotel_observer_notification():
    """Тест уведомления наблюдателей отеля"""
    # Создание отеля
    hotel = Hotel(1, "Test Hotel", "Test Location")
    
    # Создание мок наблюдателей
    email_observer = Mock(spec=Observer)
    email_observer.update = AsyncMock()
    
    logging_observer = Mock(spec=Observer)
    logging_observer.update = AsyncMock()
    
    # Подписка наблюдателей
    hotel.attach(email_observer)
    hotel.attach(logging_observer)
    
    # Обновление рейтинга
    await hotel.update_rating(4.5)
    
    # Проверка, что наблюдатели были уведомлены
    assert email_observer.update.call_count == 1
    assert logging_observer.update.call_count == 1
    
    # Проверка данных события
    call_args = email_observer.update.call_args
    event_data = call_args[0][1]  # Второй аргумент
    assert event_data['event_type'] == 'rating_updated'
    assert event_data['new_rating'] == 4.5

@pytest.mark.asyncio
async def test_booking_observer_chain():
    """Тест цепочки наблюдателей для бронирования"""
    # Создание бронирования
    booking = Booking(1, 100, 200, 300)
    
    # Создание мок наблюдателей
    email_observer = Mock(spec=Observer)
    email_observer.update = AsyncMock()
    
    analytics_observer = Mock(spec=Observer)
    analytics_observer.update = AsyncMock()
    
    inventory_observer = Mock(spec=Observer)
    inventory_observer.update = AsyncMock()
    
    # Подписка наблюдателей
    booking.attach(email_observer)
    booking.attach(analytics_observer)
    booking.attach(inventory_observer)
    
    # Создание бронирования
    await booking.create(
        check_in_date=datetime(2024, 1, 1),
        check_out_date=datetime(2024, 1, 5),
        total_cost=500.0
    )
    
    # Проверка, что все наблюдатели были уведомлены
    assert email_observer.update.call_count == 1
    assert analytics_observer.update.call_count == 1
    assert inventory_observer.update.call_count == 1

def test_event_bus_subscription():
    """Тест подписки на события в Event Bus"""
    event_bus = EventBus()
    
    # Создание обработчиков
    handler1 = Mock()
    handler2 = Mock()
    
    # Подписка на события
    event_bus.subscribe("test.event", handler1)
    event_bus.subscribe("test.event", handler2)
    
    # Проверка подписки
    assert len(event_bus._subscribers["test.event"]) == 2
    assert handler1 in event_bus._subscribers["test.event"]
    assert handler2 in event_bus._subscribers["test.event"]
    
    # Отписка
    event_bus.unsubscribe("test.event", handler1)
    assert len(event_bus._subscribers["test.event"]) == 1
    assert handler1 not in event_bus._subscribers["test.event"]
    assert handler2 in event_bus._subscribers["test.event"]

@pytest.mark.asyncio
async def test_event_bus_publishing():
    """Тест публикации событий в Event Bus"""
    event_bus = EventBus()
    
    # Создание обработчиков
    handler1 = AsyncMock()
    handler2 = AsyncMock()
    
    # Подписка на события
    event_bus.subscribe("test.event", handler1)
    event_bus.subscribe("test.event", handler2)
    
    # Публикация события
    test_data = {"message": "test"}
    await event_bus.publish("test.event", test_data)
    
    # Проверка, что обработчики были вызваны
    handler1.assert_called_once_with(test_data)
    handler2.assert_called_once_with(test_data)
```

### Интеграционные тесты
```python
@pytest.mark.asyncio
async def test_full_booking_workflow():
    """Интеграционный тест полного процесса бронирования"""
    # Создание сервисов
    email_service = Mock()
    analytics_service = Mock()
    inventory_service = Mock()
    
    # Создание наблюдателей
    email_observer = BookingEmailObserver(email_service, Mock())
    analytics_observer = BookingAnalyticsObserver(analytics_service)
    inventory_observer = BookingInventoryObserver(inventory_service)
    
    # Создание бронирования
    booking = Booking(1, 100, 200, 300)
    
    # Подписка наблюдателей
    booking.attach(email_observer)
    booking.attach(analytics_observer)
    booking.attach(inventory_observer)
    
    # Создание бронирования
    await booking.create(
        check_in_date=datetime(2024, 1, 1),
        check_out_date=datetime(2024, 1, 5),
        total_cost=500.0
    )
    
    # Проверка, что все сервисы были вызваны
    # (здесь были бы проверки вызовов методов сервисов)
    pass
```

## Лучшие практики

### 1. Использование протоколов
```python
from typing import Protocol

class ObserverProtocol(Protocol):
    async def update(self, subject: Any, event_data: Any = None) -> None: ...

class SubjectProtocol(Protocol):
    def attach(self, observer: ObserverProtocol) -> None: ...
    def detach(self, observer: ObserverProtocol) -> None: ...
    async def notify(self, event_data: Any = None) -> None: ...
```

### 2. Обработка ошибок в наблюдателях
```python
class SafeObserver(Observer):
    """Безопасный наблюдатель с обработкой ошибок"""
    
    def __init__(self, wrapped_observer: Observer, logger):
        self.wrapped_observer = wrapped_observer
        self.logger = logger
    
    async def update(self, subject: Any, event_data: Any = None):
        try:
            await self.wrapped_observer.update(subject, event_data)
        except Exception as e:
            self.logger.error(f"Observer error: {e}", exc_info=True)
```

### 3. Фильтрация событий
```python
class FilteredObserver(Observer):
    """Наблюдатель с фильтрацией событий"""
    
    def __init__(self, wrapped_observer: Observer, event_types: List[str]):
        self.wrapped_observer = wrapped_observer
        self.event_types = event_types
    
    async def update(self, subject: Any, event_data: Any = None):
        if event_data and event_data.get('event_type') in self.event_types:
            await self.wrapped_observer.update(subject, event_data)
```

### 4. Асинхронная обработка
```python
class AsyncEventBus(EventBus):
    """Асинхронная шина событий"""
    
    async def publish_async(self, event_type: str, event_data: Any = None):
        """Неблокирующая публикация событий"""
        asyncio.create_task(self.publish(event_type, event_data))
```

## Антипаттерны

### ❌ Плохо
```python
# Прямая связанность
class Hotel:
    def update_rating(self, rating):
        self.rating = rating
        # Прямой вызов сервисов
        email_service.send_notification()
        cache_service.invalidate()
        analytics_service.track()

# Слишком много наблюдателей
class Hotel:
    def __init__(self):
        self.email_observer = EmailObserver()
        self.sms_observer = SMSObserver()
        self.push_observer = PushObserver()
        self.logging_observer = LoggingObserver()
        self.cache_observer = CacheObserver()
        # ... 20+ наблюдателей
```

### ✅ Хорошо
```python
# Использование Observer Pattern
class Hotel(Subject):
    def update_rating(self, rating):
        self.rating = rating
        self.notify({'event_type': 'rating_updated', 'rating': rating})

# Группировка связанных наблюдателей
class NotificationObserver(Observer):
    def __init__(self):
        self.email_service = EmailService()
        self.sms_service = SMSService()
        self.push_service = PushService()
    
    async def update(self, subject, event_data):
        # Координированная отправка уведомлений
        pass
```
