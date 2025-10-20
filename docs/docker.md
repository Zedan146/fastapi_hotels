# 🐳 Docker - Шпаргалка

## Основы Docker

Docker - это платформа для контейнеризации приложений, которая позволяет упаковать приложение и все его зависимости в легковесный, переносимый контейнер.

### Установка Docker
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install docker.io docker-compose

# macOS
brew install docker docker-compose

# Windows
# Скачать Docker Desktop с официального сайта
```

## Основные команды

### Работа с образами
```bash
# Поиск образов
docker search nginx

# Скачивание образа
docker pull nginx:latest

# Просмотр локальных образов
docker images

# Удаление образа
docker rmi nginx:latest

# Удаление всех неиспользуемых образов
docker image prune -a
```

### Работа с контейнерами
```bash
# Запуск контейнера
docker run -d -p 8080:80 --name my-nginx nginx

# Просмотр запущенных контейнеров
docker ps

# Просмотр всех контейнеров
docker ps -a

# Остановка контейнера
docker stop my-nginx

# Запуск остановленного контейнера
docker start my-nginx

# Перезапуск контейнера
docker restart my-nginx

# Удаление контейнера
docker rm my-nginx

# Удаление всех остановленных контейнеров
docker container prune
```

### Интерактивная работа
```bash
# Запуск интерактивного контейнера
docker run -it ubuntu:latest /bin/bash

# Выполнение команды в запущенном контейнере
docker exec -it my-nginx /bin/bash

# Просмотр логов
docker logs my-nginx

# Следить за логами в реальном времени
docker logs -f my-nginx
```

## Dockerfile

### Базовый Dockerfile
```dockerfile
# Базовый образ
FROM python:3.11-slim

# Установка рабочей директории
WORKDIR /app

# Копирование файлов зависимостей
COPY requirements.txt .

# Установка зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY . .

# Открытие порта
EXPOSE 8000

# Команда запуска
CMD ["python", "main.py"]
```

### Оптимизированный Dockerfile
```dockerfile
# Многоэтапная сборка
FROM python:3.11-slim as builder

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Создание виртуального окружения
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Финальный образ
FROM python:3.11-slim

# Копирование виртуального окружения
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Создание пользователя
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Установка рабочей директории
WORKDIR /app

# Копирование приложения
COPY --chown=appuser:appuser . .

# Переключение на непривилегированного пользователя
USER appuser

# Открытие порта
EXPOSE 8000

# Команда запуска
CMD ["python", "main.py"]
```

### Dockerfile для FastAPI
```dockerfile
FROM python:3.11-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Установка рабочей директории
WORKDIR /app

# Копирование и установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY . .

# Создание пользователя
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

# Открытие порта
EXPOSE 8000

# Команда запуска
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Docker Compose

### Базовый docker-compose.yml
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/mydb
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: mydb
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

### Расширенный docker-compose.yml
```yaml
version: '3.8'

services:
  # Веб-приложение
  web:
    build: 
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/hotels_db
      - REDIS_URL=redis://redis:6379/0
      - MODE=PROD
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    networks:
      - app-network

  # База данных
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: hotels_db
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_INITDB_ARGS: "--encoding=UTF-8"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d hotels_db"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped
    networks:
      - app-network

  # Redis
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    restart: unless-stopped
    networks:
      - app-network

  # Celery Worker
  celery-worker:
    build: .
    command: celery -A src.tasks.celery_app:celery_instance worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/hotels_db
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    networks:
      - app-network

  # Celery Beat
  celery-beat:
    build: .
    command: celery -A src.tasks.celery_app:celery_instance beat --loglevel=info
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/hotels_db
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    networks:
      - app-network

  # Nginx
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - web
    restart: unless-stopped
    networks:
      - app-network

volumes:
  postgres_data:
  redis_data:

networks:
  app-network:
    driver: bridge
```

## Переменные окружения

### .env файл
```bash
# База данных
DATABASE_URL=postgresql://user:password@localhost:5432/hotels_db
DB_HOST=localhost
DB_PORT=5432
DB_USER=user
DB_PASS=password
DB_NAME=hotels_db

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_HOST=localhost
REDIS_PORT=6379

# Приложение
MODE=LOCAL
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-password
```

### Использование в docker-compose.yml
```yaml
services:
  web:
    build: .
    env_file:
      - .env
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
```

## Сети и volumes

### Создание сети
```bash
# Создание пользовательской сети
docker network create my-network

# Просмотр сетей
docker network ls

# Удаление сети
docker network rm my-network
```

### Работа с volumes
```bash
# Создание volume
docker volume create my-volume

# Просмотр volumes
docker volume ls

# Удаление volume
docker volume rm my-volume

# Просмотр информации о volume
docker volume inspect my-volume
```

### Mount bind
```yaml
services:
  web:
    build: .
    volumes:
      # Bind mount
      - ./src:/app/src
      # Named volume
      - app_data:/app/data
      # Anonymous volume
      - /app/tmp

volumes:
  app_data:
```

## Мониторинг и логирование

### Просмотр логов
```bash
# Логи конкретного сервиса
docker-compose logs web

# Логи в реальном времени
docker-compose logs -f web

# Логи с временными метками
docker-compose logs -t web

# Логи за последние 100 строк
docker-compose logs --tail=100 web
```

### Мониторинг ресурсов
```bash
# Статистика использования ресурсов
docker stats

# Статистика конкретного контейнера
docker stats my-container

# Информация о контейнере
docker inspect my-container
```

## Отладка и разработка

### Отладка контейнера
```bash
# Запуск с отладкой
docker run -it --rm python:3.11-slim /bin/bash

# Выполнение команд в запущенном контейнере
docker exec -it my-container /bin/bash

# Копирование файлов
docker cp my-container:/app/data ./local-data
docker cp ./local-file my-container:/app/
```

### Hot reload для разработки
```yaml
services:
  web:
    build: .
    volumes:
      - ./src:/app/src  # Монтирование исходного кода
    environment:
      - RELOAD=true
    command: uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

## Безопасность

### Запуск с непривилегированным пользователем
```dockerfile
# Создание пользователя
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Переключение на непривилегированного пользователя
USER appuser
```

### Ограничение ресурсов
```yaml
services:
  web:
    build: .
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
```

### Секреты
```yaml
services:
  web:
    build: .
    secrets:
      - db_password
    environment:
      - DB_PASSWORD_FILE=/run/secrets/db_password

secrets:
  db_password:
    file: ./secrets/db_password.txt
```

## Производственное развертывание

### Docker Swarm
```bash
# Инициализация Swarm
docker swarm init

# Развертывание стека
docker stack deploy -c docker-compose.yml my-stack

# Просмотр сервисов
docker service ls

# Масштабирование сервиса
docker service scale my-stack_web=3
```

### Kubernetes
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fastapi-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: fastapi-app
  template:
    metadata:
      labels:
        app: fastapi-app
    spec:
      containers:
      - name: fastapi
        image: myapp:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
---
apiVersion: v1
kind: Service
metadata:
  name: fastapi-service
spec:
  selector:
    app: fastapi-app
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

## Лучшие практики

### 1. Оптимизация размера образа
```dockerfile
# Использование .dockerignore
# .dockerignore
__pycache__
*.pyc
.git
.env
*.log

# Многоэтапная сборка
FROM python:3.11-slim as builder
# ... установка зависимостей

FROM python:3.11-slim
COPY --from=builder /opt/venv /opt/venv
# ... копирование приложения
```

### 2. Кэширование слоев
```dockerfile
# Копирование зависимостей перед исходным кодом
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .  # Исходный код копируется последним
```

### 3. Health checks
```dockerfile
# Health check в Dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
```

### 4. Логирование
```yaml
services:
  web:
    build: .
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### 5. Backup и восстановление
```bash
# Backup базы данных
docker exec postgres_container pg_dump -U user database_name > backup.sql

# Восстановление
docker exec -i postgres_container psql -U user database_name < backup.sql

# Backup volume
docker run --rm -v postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz -C /data .
```