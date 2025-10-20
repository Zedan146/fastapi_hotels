# 🔴 Redis - Шпаргалка

## Основы Redis

Redis (Remote Dictionary Server) - это in-memory структура данных, используемая как база данных, кэш и брокер сообщений.

### Установка
```bash
# Ubuntu/Debian
sudo apt-get install redis-server

# macOS
brew install redis

# Docker
docker run -d -p 6379:6379 redis:alpine

# Python клиент
pip install redis
```

## Подключение

### Базовое подключение
```python
import redis

# Синхронное подключение
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Асинхронное подключение
import aioredis

async def get_redis():
    redis = await aioredis.from_url("redis://localhost:6379")
    return redis
```

### Настройка подключения
```python
import redis
from redis.connection import ConnectionPool

# Пул соединений
pool = ConnectionPool(
    host='localhost',
    port=6379,
    db=0,
    max_connections=20,
    decode_responses=True
)

r = redis.Redis(connection_pool=pool)
```

## Строки (Strings)

### Базовые операции
```python
# Установка значения
r.set("key", "value")

# Получение значения
value = r.get("key")

# Установка с TTL (время жизни)
r.setex("key", 3600, "value")  # 3600 секунд

# Установка только если ключ не существует
r.setnx("key", "value")

# Увеличение/уменьшение числового значения
r.incr("counter")
r.incrby("counter", 5)
r.decr("counter")
r.decrby("counter", 3)
```

### Массовые операции
```python
# Установка нескольких значений
r.mset({"key1": "value1", "key2": "value2"})

# Получение нескольких значений
values = r.mget(["key1", "key2"])

# Удаление ключей
r.delete("key1", "key2")
```

## Списки (Lists)

### Базовые операции
```python
# Добавление в начало/конец списка
r.lpush("mylist", "item1", "item2")
r.rpush("mylist", "item3", "item4")

# Получение элементов
items = r.lrange("mylist", 0, -1)  # все элементы
first_item = r.lindex("mylist", 0)  # первый элемент

# Удаление элементов
r.lpop("mylist")  # удалить и вернуть первый элемент
r.rpop("mylist")  # удалить и вернуть последний элемент

# Длина списка
length = r.llen("mylist")
```

### Блокирующие операции
```python
# Блокирующее получение из списка
item = r.blpop("mylist", timeout=10)  # ждать до 10 секунд

# Блокирующее добавление в список
r.brpoplpush("source", "destination", timeout=5)
```

## Множества (Sets)

### Базовые операции
```python
# Добавление элементов
r.sadd("myset", "member1", "member2", "member3")

# Проверка принадлежности
is_member = r.sismember("myset", "member1")

# Получение всех элементов
members = r.smembers("myset")

# Удаление элементов
r.srem("myset", "member1")

# Размер множества
size = r.scard("myset")
```

### Операции над множествами
```python
# Объединение множеств
r.sunion("set1", "set2")

# Пересечение множеств
r.sinter("set1", "set2")

# Разность множеств
r.sdiff("set1", "set2")

# Сохранение результата операции
r.sunionstore("result", "set1", "set2")
```

## Хэши (Hashes)

### Базовые операции
```python
# Установка полей хэша
r.hset("user:1", mapping={"name": "John", "age": "30", "email": "john@example.com"})

# Получение значения поля
name = r.hget("user:1", "name")

# Получение всех полей
user_data = r.hgetall("user:1")

# Получение нескольких полей
fields = r.hmget("user:1", "name", "age")

# Проверка существования поля
exists = r.hexists("user:1", "name")

# Удаление полей
r.hdel("user:1", "age")

# Увеличение числового поля
r.hincrby("user:1", "age", 1)
```

## Отсортированные множества (Sorted Sets)

### Базовые операции
```python
# Добавление элементов с оценками
r.zadd("leaderboard", {"player1": 100, "player2": 200, "player3": 150})

# Получение элементов по рангу
top_players = r.zrevrange("leaderboard", 0, 2, withscores=True)

# Получение элементов по оценке
players_100_200 = r.zrangebyscore("leaderboard", 100, 200)

# Получение ранга элемента
rank = r.zrank("leaderboard", "player1")

# Увеличение оценки
r.zincrby("leaderboard", 50, "player1")

# Количество элементов
count = r.zcard("leaderboard")
```

## Кэширование

### Простое кэширование
```python
import json
import time

def cache_result(key, func, *args, **kwargs):
    """Кэширование результата функции"""
    cached = r.get(key)
    if cached:
        return json.loads(cached)
    
    result = func(*args, **kwargs)
    r.setex(key, 3600, json.dumps(result))  # кэш на час
    return result

# Использование
def expensive_calculation(n):
    time.sleep(2)  # имитация тяжелой операции
    return n * n

result = cache_result("calc:10", expensive_calculation, 10)
```

### Кэширование с версионированием
```python
def cache_with_version(key, version, func, *args, **kwargs):
    """Кэширование с версионированием"""
    versioned_key = f"{key}:v{version}"
    cached = r.get(versioned_key)
    if cached:
        return json.loads(cached)
    
    result = func(*args, **kwargs)
    r.setex(versioned_key, 3600, json.dumps(result))
    return result
```

### Кэширование с TTL
```python
def smart_cache(key, func, *args, ttl=3600, **kwargs):
    """Умное кэширование с TTL"""
    cached = r.get(key)
    if cached:
        return json.loads(cached)
    
    result = func(*args, **kwargs)
    r.setex(key, ttl, json.dumps(result))
    return result
```

## Паттерны кэширования

### Cache-Aside (Lazy Loading)
```python
def get_user(user_id):
    # Попытка получить из кэша
    cached_user = r.get(f"user:{user_id}")
    if cached_user:
        return json.loads(cached_user)
    
    # Загрузка из базы данных
    user = database.get_user(user_id)
    
    # Сохранение в кэш
    r.setex(f"user:{user_id}", 3600, json.dumps(user))
    return user
```

### Write-Through
```python
def update_user(user_id, user_data):
    # Обновление в базе данных
    user = database.update_user(user_id, user_data)
    
    # Обновление кэша
    r.setex(f"user:{user_id}", 3600, json.dumps(user))
    return user
```

### Write-Behind (Write-Back)
```python
def update_user_async(user_id, user_data):
    # Обновление кэша немедленно
    r.setex(f"user:{user_id}", 3600, json.dumps(user_data))
    
    # Асинхронное обновление базы данных
    # (реализуется через очереди задач)
    queue_async_update(user_id, user_data)
```

## Сессии и аутентификация

### Хранение сессий
```python
import uuid
import json

def create_session(user_id):
    session_id = str(uuid.uuid4())
    session_data = {
        "user_id": user_id,
        "created_at": time.time(),
        "last_activity": time.time()
    }
    
    r.setex(f"session:{session_id}", 3600, json.dumps(session_data))
    return session_id

def get_session(session_id):
    session_data = r.get(f"session:{session_id}")
    if session_data:
        return json.loads(session_data)
    return None

def update_session_activity(session_id):
    session_data = get_session(session_id)
    if session_data:
        session_data["last_activity"] = time.time()
        r.setex(f"session:{session_id}", 3600, json.dumps(session_data))
```

### JWT токены в Redis
```python
def blacklist_token(jti, expire_time):
    """Добавление токена в черный список"""
    r.setex(f"blacklist:{jti}", expire_time, "1")

def is_token_blacklisted(jti):
    """Проверка, находится ли токен в черном списке"""
    return r.exists(f"blacklist:{jti}")
```

## Очереди и Pub/Sub

### Простые очереди
```python
def enqueue_task(queue_name, task_data):
    """Добавление задачи в очередь"""
    r.lpush(queue_name, json.dumps(task_data))

def dequeue_task(queue_name, timeout=0):
    """Получение задачи из очереди"""
    result = r.brpop(queue_name, timeout)
    if result:
        return json.loads(result[1])
    return None

# Использование
enqueue_task("email_queue", {"to": "user@example.com", "subject": "Welcome"})
task = dequeue_task("email_queue", timeout=10)
```

### Pub/Sub
```python
import threading

def publisher():
    """Издатель"""
    for i in range(10):
        r.publish("notifications", f"Message {i}")
        time.sleep(1)

def subscriber():
    """Подписчик"""
    pubsub = r.pubsub()
    pubsub.subscribe("notifications")
    
    for message in pubsub.listen():
        if message["type"] == "message":
            print(f"Received: {message['data']}")

# Запуск в отдельных потоках
threading.Thread(target=publisher).start()
threading.Thread(target=subscriber).start()
```

## Мониторинг и отладка

### Информация о Redis
```python
# Информация о сервере
info = r.info()
print(f"Used memory: {info['used_memory_human']}")
print(f"Connected clients: {info['connected_clients']}")

# Список всех ключей
keys = r.keys("*")
print(f"Total keys: {len(keys)}")

# Информация о конкретном ключе
key_info = r.memory_usage("mykey")
print(f"Memory usage: {key_info} bytes")
```

### Мониторинг производительности
```python
import time

def monitor_redis_operations():
    """Мониторинг операций Redis"""
    start_time = time.time()
    
    # Ваши операции Redis
    r.set("test", "value")
    r.get("test")
    
    end_time = time.time()
    print(f"Operations took: {end_time - start_time:.4f} seconds")
```

## Лучшие практики

### 1. Используйте правильные структуры данных
```python
# Для простых значений
r.set("user:1:name", "John")

# Для объектов
r.hset("user:1", mapping={"name": "John", "age": "30"})

# Для списков
r.lpush("user:1:posts", "post1", "post2")

# Для множеств
r.sadd("user:1:tags", "python", "redis", "fastapi")
```

### 2. Настройте TTL правильно
```python
# Короткий TTL для часто изменяющихся данных
r.setex("current_price", 60, "100.50")  # 1 минута

# Длинный TTL для стабильных данных
r.setex("user_profile", 86400, user_data)  # 24 часа
```

### 3. Используйте пайплайны для массовых операций
```python
# Неэффективно
for i in range(1000):
    r.set(f"key:{i}", f"value:{i}")

# Эффективно
pipe = r.pipeline()
for i in range(1000):
    pipe.set(f"key:{i}", f"value:{i}")
pipe.execute()
```

### 4. Обрабатывайте ошибки
```python
import redis.exceptions

try:
    r.set("key", "value")
except redis.exceptions.ConnectionError:
    print("Redis connection failed")
except redis.exceptions.RedisError as e:
    print(f"Redis error: {e}")
```

### 5. Используйте транзакции для атомарности
```python
# Транзакция
pipe = r.pipeline()
pipe.multi()
pipe.set("key1", "value1")
pipe.set("key2", "value2")
pipe.execute()
```

## Конфигурация для продакшена

### Настройки безопасности
```bash
# redis.conf
bind 127.0.0.1
requirepass your_strong_password
rename-command FLUSHDB ""
rename-command FLUSHALL ""
```

### Настройки производительности
```bash
# redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

### Мониторинг
```python
# Проверка здоровья Redis
def redis_health_check():
    try:
        r.ping()
        return True
    except:
        return False
```
