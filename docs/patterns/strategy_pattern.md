# 🎯 Strategy Pattern - Шпаргалка

## Что такое Strategy Pattern

Strategy Pattern - это паттерн проектирования, который определяет семейство алгоритмов, инкапсулирует каждый из них и делает их взаимозаменяемыми. Strategy позволяет изменять алгоритм независимо от клиентов, которые его используют.

## Зачем нужен Strategy Pattern

### Преимущества:
- **Гибкость** - можно легко переключаться между алгоритмами
- **Расширяемость** - легко добавлять новые алгоритмы
- **Разделение ответственности** - каждый алгоритм в отдельном классе
- **Тестируемость** - можно тестировать алгоритмы изолированно
- **Соответствие принципу открытости/закрытости** - открыт для расширения, закрыт для модификации

## Базовая структура

### Абстрактная стратегия
```python
from abc import ABC, abstractmethod
from typing import Any, Dict

class PaymentStrategy(ABC):
    """Абстрактная стратегия для обработки платежей"""
    
    @abstractmethod
    def process_payment(self, amount: float, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Обработать платеж"""
        pass
    
    @abstractmethod
    def validate_payment_data(self, payment_data: Dict[str, Any]) -> bool:
        """Валидировать данные платежа"""
        pass

class NotificationStrategy(ABC):
    """Абстрактная стратегия для отправки уведомлений"""
    
    @abstractmethod
    async def send_notification(self, recipient: str, message: str, **kwargs) -> bool:
        """Отправить уведомление"""
        pass
```

### Конкретные стратегии
```python
import httpx
from typing import Dict, Any

class CreditCardPaymentStrategy(PaymentStrategy):
    """Стратегия для обработки платежей кредитными картами"""
    
    def process_payment(self, amount: float, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        card_number = payment_data.get('card_number')
        expiry_date = payment_data.get('expiry_date')
        cvv = payment_data.get('cvv')
        
        # Логика обработки кредитной карты
        return {
            'status': 'success',
            'transaction_id': f'cc_{card_number[-4:]}',
            'amount': amount,
            'method': 'credit_card'
        }
    
    def validate_payment_data(self, payment_data: Dict[str, Any]) -> bool:
        required_fields = ['card_number', 'expiry_date', 'cvv']
        return all(field in payment_data for field in required_fields)

class PayPalPaymentStrategy(PaymentStrategy):
    """Стратегия для обработки платежей через PayPal"""
    
    def process_payment(self, amount: float, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        paypal_token = payment_data.get('paypal_token')
        
        # Логика обработки PayPal
        return {
            'status': 'success',
            'transaction_id': f'pp_{paypal_token[:8]}',
            'amount': amount,
            'method': 'paypal'
        }
    
    def validate_payment_data(self, payment_data: Dict[str, Any]) -> bool:
        return 'paypal_token' in payment_data

class BankTransferPaymentStrategy(PaymentStrategy):
    """Стратегия для обработки банковских переводов"""
    
    def process_payment(self, amount: float, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        account_number = payment_data.get('account_number')
        routing_number = payment_data.get('routing_number')
        
        # Логика обработки банковского перевода
        return {
            'status': 'pending',
            'transaction_id': f'bt_{account_number[-4:]}',
            'amount': amount,
            'method': 'bank_transfer'
        }
    
    def validate_payment_data(self, payment_data: Dict[str, Any]) -> bool:
        required_fields = ['account_number', 'routing_number']
        return all(field in payment_data for field in required_fields)
```

### Контекст
```python
class PaymentProcessor:
    """Контекст для обработки платежей"""
    
    def __init__(self, strategy: PaymentStrategy):
        self._strategy = strategy
    
    def set_strategy(self, strategy: PaymentStrategy):
        """Изменить стратегию"""
        self._strategy = strategy
    
    def process_payment(self, amount: float, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Обработать платеж используя текущую стратегию"""
        if not self._strategy.validate_payment_data(payment_data):
            raise ValueError("Invalid payment data")
        
        return self._strategy.process_payment(amount, payment_data)

# Использование
payment_processor = PaymentProcessor(CreditCardPaymentStrategy())

# Обработка платежа кредитной картой
result = payment_processor.process_payment(
    100.0,
    {'card_number': '1234567890123456', 'expiry_date': '12/25', 'cvv': '123'}
)

# Переключение на PayPal
payment_processor.set_strategy(PayPalPaymentStrategy())
result = payment_processor.process_payment(
    100.0,
    {'paypal_token': 'abc123def456'}
)
```

## Strategy Pattern в FastAPI проекте

### Стратегии для уведомлений
```python
from abc import ABC, abstractmethod
from typing import Dict, Any
import smtplib
import httpx

class EmailNotificationStrategy(NotificationStrategy):
    """Стратегия отправки email уведомлений"""
    
    def __init__(self, smtp_host: str, smtp_port: int, username: str, password: str):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
    
    async def send_notification(self, recipient: str, message: str, **kwargs) -> bool:
        try:
            # Логика отправки email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                
                subject = kwargs.get('subject', 'Notification')
                body = f"Subject: {subject}\n\n{message}"
                
                server.sendmail(self.username, recipient, body)
                return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False

class SMSNotificationStrategy(NotificationStrategy):
    """Стратегия отправки SMS уведомлений"""
    
    def __init__(self, api_key: str, api_url: str):
        self.api_key = api_key
        self.api_url = api_url
    
    async def send_notification(self, recipient: str, message: str, **kwargs) -> bool:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_url}/send",
                    json={
                        'to': recipient,
                        'message': message,
                        'api_key': self.api_key
                    }
                )
                return response.status_code == 200
        except Exception as e:
            print(f"Failed to send SMS: {e}")
            return False

class PushNotificationStrategy(NotificationStrategy):
    """Стратегия отправки push уведомлений"""
    
    def __init__(self, firebase_key: str):
        self.firebase_key = firebase_key
    
    async def send_notification(self, recipient: str, message: str, **kwargs) -> bool:
        try:
            # Логика отправки push уведомления
            device_token = recipient
            title = kwargs.get('title', 'Notification')
            
            # Здесь была бы интеграция с Firebase
            print(f"Push notification sent to {device_token}: {title} - {message}")
            return True
        except Exception as e:
            print(f"Failed to send push notification: {e}")
            return False
```

### Сервис уведомлений с стратегиями
```python
class NotificationService:
    """Сервис уведомлений с поддержкой различных стратегий"""
    
    def __init__(self):
        self._strategies: Dict[str, NotificationStrategy] = {}
        self._default_strategy = None
    
    def register_strategy(self, name: str, strategy: NotificationStrategy, is_default: bool = False):
        """Зарегистрировать стратегию"""
        self._strategies[name] = strategy
        if is_default:
            self._default_strategy = strategy
    
    def get_strategy(self, name: str) -> NotificationStrategy:
        """Получить стратегию по имени"""
        if name not in self._strategies:
            raise ValueError(f"Unknown strategy: {name}")
        return self._strategies[name]
    
    async def send_notification(
        self, 
        recipient: str, 
        message: str, 
        strategy_name: str = None,
        **kwargs
    ) -> bool:
        """Отправить уведомление"""
        if strategy_name:
            strategy = self.get_strategy(strategy_name)
        elif self._default_strategy:
            strategy = self._default_strategy
        else:
            raise ValueError("No strategy specified")
        
        return await strategy.send_notification(recipient, message, **kwargs)

# Использование в FastAPI
notification_service = NotificationService()

# Регистрация стратегий
notification_service.register_strategy(
    'email', 
    EmailNotificationStrategy('smtp.gmail.com', 587, 'user@gmail.com', 'password'),
    is_default=True
)
notification_service.register_strategy(
    'sms', 
    SMSNotificationStrategy('api_key', 'https://api.sms-provider.com')
)
notification_service.register_strategy(
    'push', 
    PushNotificationStrategy('firebase_key')
)

@app.post("/notifications/send")
async def send_notification(
    recipient: str,
    message: str,
    strategy: str = "email",
    **kwargs
):
    success = await notification_service.send_notification(
        recipient, message, strategy, **kwargs
    )
    return {"success": success}
```

## Стратегии для валидации

### Стратегии валидации данных
```python
from abc import ABC, abstractmethod
from typing import Dict, Any, List
import re

class ValidationStrategy(ABC):
    """Абстрактная стратегия валидации"""
    
    @abstractmethod
    def validate(self, data: Dict[str, Any]) -> List[str]:
        """Валидировать данные и вернуть список ошибок"""
        pass

class UserValidationStrategy(ValidationStrategy):
    """Стратегия валидации пользователей"""
    
    def validate(self, data: Dict[str, Any]) -> List[str]:
        errors = []
        
        # Валидация имени
        name = data.get('name', '')
        if not name or len(name.strip()) < 2:
            errors.append("Name must be at least 2 characters")
        
        # Валидация email
        email = data.get('email', '')
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            errors.append("Invalid email format")
        
        # Валидация возраста
        age = data.get('age')
        if age is not None and (not isinstance(age, int) or age < 0 or age > 150):
            errors.append("Age must be between 0 and 150")
        
        return errors

class HotelValidationStrategy(ValidationStrategy):
    """Стратегия валидации отелей"""
    
    def validate(self, data: Dict[str, Any]) -> List[str]:
        errors = []
        
        # Валидация названия
        title = data.get('title', '')
        if not title or len(title.strip()) < 3:
            errors.append("Hotel title must be at least 3 characters")
        
        # Валидация местоположения
        location = data.get('location', '')
        if not location or len(location.strip()) < 5:
            errors.append("Hotel location must be at least 5 characters")
        
        # Валидация рейтинга
        rating = data.get('rating')
        if rating is not None and (not isinstance(rating, (int, float)) or rating < 1 or rating > 5):
            errors.append("Rating must be between 1 and 5")
        
        return errors

class BookingValidationStrategy(ValidationStrategy):
    """Стратегия валидации бронирований"""
    
    def validate(self, data: Dict[str, Any]) -> List[str]:
        errors = []
        
        # Валидация дат
        date_from = data.get('date_from')
        date_to = data.get('date_to')
        
        if date_from and date_to and date_from >= date_to:
            errors.append("Check-in date must be before check-out date")
        
        # Валидация количества гостей
        guests = data.get('guests')
        if guests is not None and (not isinstance(guests, int) or guests < 1 or guests > 10):
            errors.append("Number of guests must be between 1 and 10")
        
        return errors
```

### Валидатор с стратегиями
```python
class DataValidator:
    """Валидатор данных с поддержкой стратегий"""
    
    def __init__(self):
        self._strategies: Dict[str, ValidationStrategy] = {}
    
    def register_strategy(self, data_type: str, strategy: ValidationStrategy):
        """Зарегистрировать стратегию валидации"""
        self._strategies[data_type] = strategy
    
    def validate(self, data_type: str, data: Dict[str, Any]) -> List[str]:
        """Валидировать данные"""
        if data_type not in self._strategies:
            raise ValueError(f"Unknown data type: {data_type}")
        
        return self._strategies[data_type].validate(data)

# Использование
validator = DataValidator()
validator.register_strategy('user', UserValidationStrategy())
validator.register_strategy('hotel', HotelValidationStrategy())
validator.register_strategy('booking', BookingValidationStrategy())

# Валидация пользователя
user_errors = validator.validate('user', {
    'name': 'John',
    'email': 'john@example.com',
    'age': 25
})

# Валидация отеля
hotel_errors = validator.validate('hotel', {
    'title': 'Grand Hotel',
    'location': 'New York',
    'rating': 4.5
})
```

## Стратегии для кэширования

### Стратегии кэширования
```python
from abc import ABC, abstractmethod
from typing import Any, Optional
import json
import pickle

class CacheStrategy(ABC):
    """Абстрактная стратегия кэширования"""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Получить значение из кэша"""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Сохранить значение в кэш"""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Удалить значение из кэша"""
        pass

class RedisCacheStrategy(CacheStrategy):
    """Стратегия кэширования с Redis"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
    
    async def get(self, key: str) -> Optional[Any]:
        try:
            data = await self.redis.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            print(f"Redis get error: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        try:
            data = json.dumps(value, default=str)
            await self.redis.setex(key, ttl, data)
            return True
        except Exception as e:
            print(f"Redis set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        try:
            await self.redis.delete(key)
            return True
        except Exception as e:
            print(f"Redis delete error: {e}")
            return False

class MemoryCacheStrategy(CacheStrategy):
    """Стратегия кэширования в памяти"""
    
    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._ttl: Dict[str, float] = {}
    
    async def get(self, key: str) -> Optional[Any]:
        if key in self._cache:
            if key in self._ttl and self._ttl[key] > time.time():
                return self._cache[key]
            else:
                # TTL истек
                del self._cache[key]
                del self._ttl[key]
        return None
    
    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        self._cache[key] = value
        self._ttl[key] = time.time() + ttl
        return True
    
    async def delete(self, key: str) -> bool:
        if key in self._cache:
            del self._cache[key]
            if key in self._ttl:
                del self._ttl[key]
            return True
        return False

class FileCacheStrategy(CacheStrategy):
    """Стратегия кэширования в файлы"""
    
    def __init__(self, cache_dir: str):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    async def get(self, key: str) -> Optional[Any]:
        file_path = os.path.join(self.cache_dir, f"{key}.cache")
        try:
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    return pickle.load(f)
        except Exception as e:
            print(f"File cache get error: {e}")
        return None
    
    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        file_path = os.path.join(self.cache_dir, f"{key}.cache")
        try:
            with open(file_path, 'wb') as f:
                pickle.dump(value, f)
            return True
        except Exception as e:
            print(f"File cache set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        file_path = os.path.join(self.cache_dir, f"{key}.cache")
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
        except Exception as e:
            print(f"File cache delete error: {e}")
        return False
```

### Кэш-менеджер с стратегиями
```python
class CacheManager:
    """Менеджер кэша с поддержкой различных стратегий"""
    
    def __init__(self):
        self._strategies: Dict[str, CacheStrategy] = {}
        self._default_strategy = None
    
    def register_strategy(self, name: str, strategy: CacheStrategy, is_default: bool = False):
        """Зарегистрировать стратегию кэширования"""
        self._strategies[name] = strategy
        if is_default:
            self._default_strategy = strategy
    
    def get_strategy(self, name: str) -> CacheStrategy:
        """Получить стратегию по имени"""
        if name not in self._strategies:
            raise ValueError(f"Unknown cache strategy: {name}")
        return self._strategies[name]
    
    async def get(self, key: str, strategy_name: str = None) -> Optional[Any]:
        """Получить значение из кэша"""
        strategy = self._get_strategy(strategy_name)
        return await strategy.get(key)
    
    async def set(self, key: str, value: Any, ttl: int = 3600, strategy_name: str = None) -> bool:
        """Сохранить значение в кэш"""
        strategy = self._get_strategy(strategy_name)
        return await strategy.set(key, value, ttl)
    
    async def delete(self, key: str, strategy_name: str = None) -> bool:
        """Удалить значение из кэша"""
        strategy = self._get_strategy(strategy_name)
        return await strategy.delete(key)
    
    def _get_strategy(self, strategy_name: str = None) -> CacheStrategy:
        """Получить стратегию"""
        if strategy_name:
            return self.get_strategy(strategy_name)
        elif self._default_strategy:
            return self._default_strategy
        else:
            raise ValueError("No cache strategy specified")
```

## Стратегии для аутентификации

### Стратегии аутентификации
```python
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import jwt
import hashlib

class AuthenticationStrategy(ABC):
    """Абстрактная стратегия аутентификации"""
    
    @abstractmethod
    async def authenticate(self, credentials: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Аутентифицировать пользователя"""
        pass
    
    @abstractmethod
    def generate_token(self, user_data: Dict[str, Any]) -> str:
        """Сгенерировать токен"""
        pass

class JWTStrategy(AuthenticationStrategy):
    """Стратегия аутентификации через JWT"""
    
    def __init__(self, secret_key: str, algorithm: str = 'HS256'):
        self.secret_key = secret_key
        self.algorithm = algorithm
    
    async def authenticate(self, credentials: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        token = credentials.get('token')
        if not token:
            return None
        
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return {
                'user_id': payload.get('user_id'),
                'email': payload.get('email'),
                'exp': payload.get('exp')
            }
        except jwt.InvalidTokenError:
            return None
    
    def generate_token(self, user_data: Dict[str, Any]) -> str:
        payload = {
            'user_id': user_data['id'],
            'email': user_data['email'],
            'exp': time.time() + 3600  # 1 час
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

class APIKeyStrategy(AuthenticationStrategy):
    """Стратегия аутентификации через API ключ"""
    
    def __init__(self, api_keys: Dict[str, Dict[str, Any]]):
        self.api_keys = api_keys
    
    async def authenticate(self, credentials: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        api_key = credentials.get('api_key')
        if not api_key or api_key not in self.api_keys:
            return None
        
        return self.api_keys[api_key]
    
    def generate_token(self, user_data: Dict[str, Any]) -> str:
        # Для API ключей токен не генерируется
        return user_data.get('api_key', '')

class BasicAuthStrategy(AuthenticationStrategy):
    """Стратегия базовой аутентификации"""
    
    def __init__(self, users: Dict[str, str]):  # username -> password_hash
        self.users = users
    
    async def authenticate(self, credentials: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        username = credentials.get('username')
        password = credentials.get('password')
        
        if not username or not password:
            return None
        
        if username in self.users:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            if self.users[username] == password_hash:
                return {'username': username}
        
        return None
    
    def generate_token(self, user_data: Dict[str, Any]) -> str:
        # Для базовой аутентификации токен не генерируется
        return f"Basic {user_data['username']}"
```

## Тестирование стратегий

### Unit тесты
```python
import pytest
from unittest.mock import Mock, patch

def test_payment_strategies():
    """Тест стратегий платежей"""
    # Тест кредитной карты
    cc_strategy = CreditCardPaymentStrategy()
    payment_data = {
        'card_number': '1234567890123456',
        'expiry_date': '12/25',
        'cvv': '123'
    }
    
    assert cc_strategy.validate_payment_data(payment_data) == True
    
    result = cc_strategy.process_payment(100.0, payment_data)
    assert result['status'] == 'success'
    assert result['method'] == 'credit_card'
    
    # Тест PayPal
    pp_strategy = PayPalPaymentStrategy()
    paypal_data = {'paypal_token': 'abc123'}
    
    assert pp_strategy.validate_payment_data(paypal_data) == True
    
    result = pp_strategy.process_payment(100.0, paypal_data)
    assert result['status'] == 'success'
    assert result['method'] == 'paypal'

def test_notification_strategies():
    """Тест стратегий уведомлений"""
    # Мок для email стратегии
    email_strategy = EmailNotificationStrategy('localhost', 587, 'user', 'pass')
    
    with patch('smtplib.SMTP') as mock_smtp:
        mock_server = Mock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        result = await email_strategy.send_notification('test@example.com', 'Test message')
        assert result == True
        mock_server.sendmail.assert_called_once()

def test_validation_strategies():
    """Тест стратегий валидации"""
    user_strategy = UserValidationStrategy()
    
    # Валидные данные
    valid_data = {
        'name': 'John Doe',
        'email': 'john@example.com',
        'age': 25
    }
    errors = user_strategy.validate(valid_data)
    assert len(errors) == 0
    
    # Невалидные данные
    invalid_data = {
        'name': 'J',
        'email': 'invalid-email',
        'age': -5
    }
    errors = user_strategy.validate(invalid_data)
    assert len(errors) > 0
    assert "Name must be at least 2 characters" in errors
    assert "Invalid email format" in errors
    assert "Age must be between 0 and 150" in errors
```

### Интеграционные тесты
```python
@pytest.mark.asyncio
async def test_payment_processor_integration():
    """Интеграционный тест процессора платежей"""
    processor = PaymentProcessor(CreditCardPaymentStrategy())
    
    # Тест успешного платежа
    result = processor.process_payment(100.0, {
        'card_number': '1234567890123456',
        'expiry_date': '12/25',
        'cvv': '123'
    })
    
    assert result['status'] == 'success'
    assert result['amount'] == 100.0
    
    # Тест переключения стратегии
    processor.set_strategy(PayPalPaymentStrategy())
    
    result = processor.process_payment(100.0, {
        'paypal_token': 'abc123'
    })
    
    assert result['status'] == 'success'
    assert result['method'] == 'paypal'

@pytest.mark.asyncio
async def test_notification_service_integration():
    """Интеграционный тест сервиса уведомлений"""
    service = NotificationService()
    
    # Регистрация мок стратегий
    mock_email = Mock(spec=NotificationStrategy)
    mock_email.send_notification.return_value = True
    
    mock_sms = Mock(spec=NotificationStrategy)
    mock_sms.send_notification.return_value = True
    
    service.register_strategy('email', mock_email, is_default=True)
    service.register_strategy('sms', mock_sms)
    
    # Тест отправки email
    result = await service.send_notification('test@example.com', 'Test message')
    assert result == True
    mock_email.send_notification.assert_called_once()
    
    # Тест отправки SMS
    result = await service.send_notification('+1234567890', 'Test SMS', strategy_name='sms')
    assert result == True
    mock_sms.send_notification.assert_called_once()
```

## Лучшие практики

### 1. Использование протоколов
```python
from typing import Protocol

class PaymentStrategyProtocol(Protocol):
    def process_payment(self, amount: float, payment_data: Dict[str, Any]) -> Dict[str, Any]: ...
    def validate_payment_data(self, payment_data: Dict[str, Any]) -> bool: ...

# Хорошо - использование протокола
def process_payment_with_strategy(strategy: PaymentStrategyProtocol, amount: float, data: Dict[str, Any]):
    return strategy.process_payment(amount, data)
```

### 2. Фабрика стратегий
```python
class StrategyFactory:
    """Фабрика для создания стратегий"""
    
    @staticmethod
    def create_payment_strategy(strategy_type: str) -> PaymentStrategy:
        strategies = {
            'credit_card': CreditCardPaymentStrategy,
            'paypal': PayPalPaymentStrategy,
            'bank_transfer': BankTransferPaymentStrategy
        }
        
        if strategy_type not in strategies:
            raise ValueError(f"Unknown payment strategy: {strategy_type}")
        
        return strategies[strategy_type]()
```

### 3. Конфигурация стратегий
```python
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class StrategyConfig:
    type: str
    parameters: Dict[str, Any]

class ConfigurableStrategyFactory:
    """Фабрика стратегий с конфигурацией"""
    
    def create_strategy(self, config: StrategyConfig) -> Any:
        if config.type == 'payment':
            return self._create_payment_strategy(config.parameters)
        elif config.type == 'notification':
            return self._create_notification_strategy(config.parameters)
        else:
            raise ValueError(f"Unknown strategy type: {config.type}")
    
    def _create_payment_strategy(self, params: Dict[str, Any]):
        strategy_type = params['strategy_type']
        if strategy_type == 'credit_card':
            return CreditCardPaymentStrategy()
        # ... другие стратегии
    
    def _create_notification_strategy(self, params: Dict[str, Any]):
        strategy_type = params['strategy_type']
        if strategy_type == 'email':
            return EmailNotificationStrategy(**params['email_config'])
        # ... другие стратегии
```

## Антипаттерны

### ❌ Плохо
```python
# Слишком много if-else вместо стратегий
class BadPaymentProcessor:
    def process_payment(self, payment_type: str, amount: float, data: dict):
        if payment_type == 'credit_card':
            # Логика кредитной карты
            pass
        elif payment_type == 'paypal':
            # Логика PayPal
            pass
        elif payment_type == 'bank_transfer':
            # Логика банковского перевода
            pass
        # ... много условий

# Смешивание ответственности
class BadStrategy:
    def process_payment(self, amount: float, data: dict):
        # Обработка платежа
        result = self._process_payment_impl(amount, data)
        
        # Отправка уведомления (не должно быть в стратегии платежа)
        self._send_notification(result)
        
        return result
```

### ✅ Хорошо
```python
# Использование стратегий
class GoodPaymentProcessor:
    def __init__(self, strategy: PaymentStrategy):
        self.strategy = strategy
    
    def process_payment(self, amount: float, data: dict):
        return self.strategy.process_payment(amount, data)

# Разделение ответственности
class PaymentStrategy:
    def process_payment(self, amount: float, data: dict):
        # Только обработка платежа
        pass

class NotificationStrategy:
    def send_notification(self, message: str):
        # Только отправка уведомлений
        pass
```
