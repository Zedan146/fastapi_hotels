# 🌐 Nginx - Шпаргалка

## Что такое Nginx

Nginx (произносится как "engine x") - это высокопроизводительный веб-сервер и обратный прокси-сервер, который также может использоваться как балансировщик нагрузки, кэш и почтовый прокси.

## Зачем нужен Nginx

### Преимущества:
- **Высокая производительность** - асинхронная архитектура, низкое потребление памяти
- **Масштабируемость** - поддержка тысяч одновременных соединений
- **Гибкость** - множество модулей и конфигураций
- **Надежность** - стабильная работа под высокой нагрузкой
- **Безопасность** - встроенные механизмы защиты

## Установка Nginx

### Ubuntu/Debian
```bash
# Обновление пакетов
sudo apt update

# Установка Nginx
sudo apt install nginx

# Запуск сервиса
sudo systemctl start nginx
sudo systemctl enable nginx

# Проверка статуса
sudo systemctl status nginx

# Проверка версии
nginx -v
```

### CentOS/RHEL
```bash
# Установка EPEL репозитория
sudo yum install epel-release

# Установка Nginx
sudo yum install nginx

# Запуск сервиса
sudo systemctl start nginx
sudo systemctl enable nginx

# Проверка статуса
sudo systemctl status nginx
```

### macOS
```bash
# Установка через Homebrew
brew install nginx

# Запуск сервиса
brew services start nginx

# Или запуск вручную
sudo nginx
```

### Docker
```bash
# Запуск Nginx в Docker
docker run -d -p 80:80 --name nginx nginx

# Запуск с кастомной конфигурацией
docker run -d -p 80:80 -v /path/to/nginx.conf:/etc/nginx/nginx.conf nginx
```

## Основы конфигурации

### Структура конфигурации
```nginx
# Основная конфигурация
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log;
pid /run/nginx.pid;

# События
events {
    worker_connections 1024;
    use epoll;
    multi_accept on;
}

# HTTP блок
http {
    # Основные настройки
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    # Логирование
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';
    
    access_log /var/log/nginx/access.log main;
    
    # Настройки производительности
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    
    # Gzip сжатие
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
    
    # Включение конфигураций сайтов
    include /etc/nginx/conf.d/*.conf;
    include /etc/nginx/sites-enabled/*;
}
```

### Базовая конфигурация сервера
```nginx
server {
    listen 80;
    server_name example.com www.example.com;
    
    # Корневая директория
    root /var/www/html;
    index index.html index.htm index.php;
    
    # Логи
    access_log /var/log/nginx/example.com.access.log;
    error_log /var/log/nginx/example.com.error.log;
    
    # Основное местоположение
    location / {
        try_files $uri $uri/ =404;
    }
    
    # Обработка статических файлов
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Обработка PHP
    location ~ \.php$ {
        fastcgi_pass unix:/var/run/php/php7.4-fpm.sock;
        fastcgi_index index.php;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        include fastcgi_params;
    }
}
```

## Обратный прокси для FastAPI

### Базовая конфигурация прокси
```nginx
server {
    listen 80;
    server_name api.example.com;
    
    # Проксирование на FastAPI приложение
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Проксирование WebSocket (если используется)
    location /ws {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Продвинутая конфигурация прокси
```nginx
# Upstream для балансировки нагрузки
upstream fastapi_backend {
    server 127.0.0.1:8000 weight=3;
    server 127.0.0.1:8001 weight=2;
    server 127.0.0.1:8002 weight=1;
    
    # Health check
    keepalive 32;
}

server {
    listen 80;
    server_name api.example.com;
    
    # Ограничение размера запроса
    client_max_body_size 10M;
    
    # Таймауты
    proxy_connect_timeout 60s;
    proxy_send_timeout 60s;
    proxy_read_timeout 60s;
    
    # Буферизация
    proxy_buffering on;
    proxy_buffer_size 4k;
    proxy_buffers 8 4k;
    
    # Основное местоположение
    location / {
        proxy_pass http://fastapi_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Кэширование для GET запросов
        proxy_cache_valid 200 302 10m;
        proxy_cache_valid 404 1m;
    }
    
    # API документация (Swagger/ReDoc)
    location /docs {
        proxy_pass http://fastapi_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Статические файлы
    location /static/ {
        alias /var/www/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

## SSL/TLS конфигурация

### Самоподписанный сертификат
```bash
# Создание самоподписанного сертификата
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/ssl/private/nginx-selfsigned.key \
    -out /etc/ssl/certs/nginx-selfsigned.crt
```

### Конфигурация с SSL
```nginx
server {
    listen 443 ssl http2;
    server_name api.example.com;
    
    # SSL сертификаты
    ssl_certificate /etc/ssl/certs/nginx-selfsigned.crt;
    ssl_certificate_key /etc/ssl/private/nginx-selfsigned.key;
    
    # SSL настройки
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # HSTS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Проксирование на FastAPI
    location / {
        proxy_pass http://fastapi_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Редирект с HTTP на HTTPS
server {
    listen 80;
    server_name api.example.com;
    return 301 https://$server_name$request_uri;
}
```

### Let's Encrypt с Certbot
```bash
# Установка Certbot
sudo apt install certbot python3-certbot-nginx

# Получение сертификата
sudo certbot --nginx -d api.example.com

# Автоматическое обновление
sudo crontab -e
# Добавить строку:
# 0 12 * * * /usr/bin/certbot renew --quiet
```

### Конфигурация с Let's Encrypt
```nginx
server {
    listen 443 ssl http2;
    server_name api.example.com;
    
    # Let's Encrypt сертификаты
    ssl_certificate /etc/letsencrypt/live/api.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.example.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
    
    # Проксирование на FastAPI
    location / {
        proxy_pass http://fastapi_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Балансировка нагрузки

### Базовая балансировка
```nginx
# Upstream с несколькими серверами
upstream fastapi_cluster {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
    server 127.0.0.1:8003;
}

server {
    listen 80;
    server_name api.example.com;
    
    location / {
        proxy_pass http://fastapi_cluster;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Продвинутая балансировка
```nginx
upstream fastapi_cluster {
    # Weighted round-robin
    server 127.0.0.1:8000 weight=3 max_fails=3 fail_timeout=30s;
    server 127.0.0.1:8001 weight=2 max_fails=3 fail_timeout=30s;
    server 127.0.0.1:8002 weight=1 max_fails=3 fail_timeout=30s;
    
    # Backup сервер
    server 127.0.0.1:8003 backup;
    
    # Health check
    keepalive 32;
}

# IP Hash для sticky sessions
upstream fastapi_sticky {
    ip_hash;
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}

# Least connections
upstream fastapi_least_conn {
    least_conn;
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}
```

## Кэширование

### Кэширование статических файлов
```nginx
server {
    listen 80;
    server_name api.example.com;
    
    # Кэширование статических файлов
    location ~* \.(css|js|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        add_header Vary Accept-Encoding;
        
        # Gzip сжатие
        gzip_static on;
    }
    
    # Кэширование API ответов
    location /api/cache/ {
        proxy_pass http://fastapi_backend;
        proxy_cache api_cache;
        proxy_cache_valid 200 302 10m;
        proxy_cache_valid 404 1m;
        proxy_cache_use_stale error timeout updating http_500 http_502 http_503 http_504;
        proxy_cache_lock on;
        
        add_header X-Cache-Status $upstream_cache_status;
    }
}

# Кэш зона
http {
    proxy_cache_path /var/cache/nginx/api levels=1:2 keys_zone=api_cache:10m max_size=1g inactive=60m use_temp_path=off;
}
```

### Redis кэширование
```nginx
# Модуль для работы с Redis (требует компиляции с модулем)
upstream redis_backend {
    server 127.0.0.1:6379;
}

server {
    listen 80;
    server_name api.example.com;
    
    # Кэширование через Redis
    location /api/cached/ {
        # Проверка кэша в Redis
        access_by_lua_block {
            local redis = require "resty.redis"
            local red = redis:new()
            red:set_timeouts(1000, 1000, 1000)
            
            local ok, err = red:connect("127.0.0.1", 6379)
            if not ok then
                ngx.log(ngx.ERR, "failed to connect to redis: ", err)
                return
            end
            
            local key = "cache:" .. ngx.var.request_uri
            local res, err = red:get(key)
            if res and res ~= ngx.null then
                ngx.say(res)
                ngx.exit(200)
            end
        }
        
        # Если нет в кэше, проксируем на бэкенд
        proxy_pass http://fastapi_backend;
        
        # Сохранение в кэш
        header_filter_by_lua_block {
            if ngx.status == 200 then
                local redis = require "resty.redis"
                local red = redis:new()
                red:set_timeouts(1000, 1000, 1000)
                
                local ok, err = red:connect("127.0.0.1", 6379)
                if ok then
                    local key = "cache:" .. ngx.var.request_uri
                    red:setex(key, 300, ngx.arg[1]) -- 5 минут
                end
            end
        }
    }
}
```

## Безопасность

### Базовая защита
```nginx
server {
    listen 80;
    server_name api.example.com;
    
    # Скрытие версии Nginx
    server_tokens off;
    
    # Защита от DDoS
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req zone=api burst=20 nodelay;
    
    # Ограничение размера запроса
    client_max_body_size 10M;
    
    # Таймауты
    client_body_timeout 12;
    client_header_timeout 12;
    keepalive_timeout 15;
    send_timeout 10;
    
    # Заголовки безопасности
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
    
    # Блокировка подозрительных запросов
    location ~* \.(php|asp|aspx|jsp)$ {
        return 444;
    }
    
    # Блокировка ботов
    if ($http_user_agent ~* (bot|crawler|spider)) {
        return 403;
    }
    
    location / {
        proxy_pass http://fastapi_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Rate Limiting
```nginx
# Ограничение по IP
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=login:10m rate=1r/s;

# Ограничение по ключу (для API)
limit_req_zone $http_authorization zone=api_key:10m rate=100r/s;

server {
    listen 80;
    server_name api.example.com;
    
    # Общее ограничение
    limit_req zone=api burst=20 nodelay;
    
    # Ограничение для логина
    location /auth/login {
        limit_req zone=login burst=5 nodelay;
        proxy_pass http://fastapi_backend;
    }
    
    # Ограничение по API ключу
    location /api/ {
        limit_req zone=api_key burst=50 nodelay;
        proxy_pass http://fastapi_backend;
    }
}
```

### Блокировка по IP
```nginx
# Черный список IP
geo $blocked_ip {
    default 0;
    192.168.1.0/24 1;  # Блокировка подсети
    10.0.0.1 1;        # Блокировка конкретного IP
}

server {
    listen 80;
    server_name api.example.com;
    
    # Блокировка заблокированных IP
    if ($blocked_ip) {
        return 403;
    }
    
    location / {
        proxy_pass http://fastapi_backend;
    }
}
```

## Мониторинг и логирование

### Расширенное логирование
```nginx
# Кастомный формат лога
log_format detailed '$remote_addr - $remote_user [$time_local] '
                   '"$request" $status $body_bytes_sent '
                   '"$http_referer" "$http_user_agent" '
                   '$request_time $upstream_response_time '
                   '$upstream_addr $upstream_status';

# Логирование в JSON
log_format json_combined escape=json
    '{'
        '"time_local":"$time_local",'
        '"remote_addr":"$remote_addr",'
        '"remote_user":"$remote_user",'
        '"request":"$request",'
        '"status": "$status",'
        '"body_bytes_sent":"$body_bytes_sent",'
        '"request_time":"$request_time",'
        '"http_referrer":"$http_referer",'
        '"http_user_agent":"$http_user_agent"'
    '}';

server {
    listen 80;
    server_name api.example.com;
    
    # Детальные логи
    access_log /var/log/nginx/api.detailed.log detailed;
    access_log /var/log/nginx/api.json.log json_combined;
    
    # Логи ошибок
    error_log /var/log/nginx/api.error.log warn;
    
    location / {
        proxy_pass http://fastapi_backend;
    }
}
```

### Метрики и мониторинг
```nginx
# Endpoint для метрик (требует модуль nginx-module-vts)
server {
    listen 80;
    server_name metrics.example.com;
    
    location /nginx_status {
        stub_status on;
        access_log off;
        allow 127.0.0.1;
        deny all;
    }
    
    location /metrics {
        vhost_traffic_status_display;
        vhost_traffic_status_display_format json;
    }
}
```

## Оптимизация производительности

### Настройки производительности
```nginx
# Основные настройки
worker_processes auto;
worker_cpu_affinity auto;
worker_rlimit_nofile 65535;

events {
    worker_connections 4096;
    use epoll;
    multi_accept on;
}

http {
    # Основные настройки
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    keepalive_requests 1000;
    
    # Буферизация
    client_body_buffer_size 128k;
    client_header_buffer_size 1k;
    large_client_header_buffers 4 4k;
    client_max_body_size 10m;
    
    # Gzip сжатие
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;
    
    # Кэширование файлов
    open_file_cache max=1000 inactive=20s;
    open_file_cache_valid 30s;
    open_file_cache_min_uses 2;
    open_file_cache_errors on;
}
```

### Кэширование и сжатие
```nginx
server {
    listen 80;
    server_name api.example.com;
    
    # Кэширование статических файлов
    location ~* \.(css|js|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        add_header Vary Accept-Encoding;
        
        # Gzip сжатие
        gzip_static on;
        
        # Кэширование в браузере
        etag on;
        if_modified_since exact;
    }
    
    # Кэширование API ответов
    location /api/cache/ {
        proxy_pass http://fastapi_backend;
        proxy_cache api_cache;
        proxy_cache_valid 200 302 10m;
        proxy_cache_valid 404 1m;
        proxy_cache_use_stale error timeout updating;
        proxy_cache_lock on;
        
        # Заголовки кэша
        add_header X-Cache-Status $upstream_cache_status;
        add_header X-Cache-Date $upstream_http_date;
    }
}
```

## Docker конфигурация

### Dockerfile для Nginx
```dockerfile
FROM nginx:alpine

# Копирование конфигурации
COPY nginx.conf /etc/nginx/nginx.conf
COPY conf.d/ /etc/nginx/conf.d/

# Создание директорий
RUN mkdir -p /var/log/nginx /var/cache/nginx

# Установка дополнительных модулей
RUN apk add --no-cache nginx-mod-http-headers-more

# Открытие портов
EXPOSE 80 443

# Запуск
CMD ["nginx", "-g", "daemon off;"]
```

### Docker Compose с Nginx
```yaml
version: '3.8'

services:
  nginx:
    build: .
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl
      - ./logs:/var/log/nginx
    depends_on:
      - fastapi
    networks:
      - app-network

  fastapi:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/hotels
    depends_on:
      - db
      - redis
    networks:
      - app-network

  db:
    image: postgres:13
    environment:
      POSTGRES_DB: hotels
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - app-network

  redis:
    image: redis:6
    networks:
      - app-network

networks:
  app-network:
    driver: bridge

volumes:
  postgres_data:
```

## Команды и управление

### Основные команды
```bash
# Проверка конфигурации
nginx -t

# Перезагрузка конфигурации
nginx -s reload

# Остановка
nginx -s stop

# Graceful остановка
nginx -s quit

# Перезапуск
systemctl restart nginx

# Проверка статуса
systemctl status nginx

# Просмотр логов
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### Отладка
```bash
# Проверка конфигурации с подробным выводом
nginx -T

# Проверка процессов
ps aux | grep nginx

# Проверка портов
netstat -tlnp | grep nginx

# Тест конфигурации
nginx -t -c /path/to/nginx.conf

# Проверка модулей
nginx -V
```

## Лучшие практики

### 1. Безопасность
```nginx
# Скрытие версии
server_tokens off;

# Заголовки безопасности
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header X-Content-Type-Options "nosniff" always;

# Ограничение методов
if ($request_method !~ ^(GET|HEAD|POST)$ ) {
    return 405;
}
```

### 2. Производительность
```nginx
# Оптимизация worker процессов
worker_processes auto;
worker_cpu_affinity auto;

# Оптимизация событий
events {
    worker_connections 4096;
    use epoll;
    multi_accept on;
}

# Кэширование
open_file_cache max=1000 inactive=20s;
open_file_cache_valid 30s;
```

### 3. Мониторинг
```nginx
# Логирование в JSON
log_format json_combined escape=json
    '{"time":"$time_local","remote_addr":"$remote_addr","request":"$request","status":"$status"}';

# Endpoint для мониторинга
location /nginx_status {
    stub_status on;
    access_log off;
    allow 127.0.0.1;
    deny all;
}
```

## Troubleshooting

### Частые проблемы

#### 1. 502 Bad Gateway
```bash
# Проверка бэкенда
curl http://127.0.0.1:8000/health

# Проверка логов
tail -f /var/log/nginx/error.log

# Проверка конфигурации
nginx -t
```

#### 2. 413 Request Entity Too Large
```nginx
# Увеличение лимита
client_max_body_size 10M;
```

#### 3. 504 Gateway Timeout
```nginx
# Увеличение таймаутов
proxy_connect_timeout 60s;
proxy_send_timeout 60s;
proxy_read_timeout 60s;
```

#### 4. Проблемы с SSL
```bash
# Проверка сертификата
openssl x509 -in /etc/ssl/certs/cert.pem -text -noout

# Проверка SSL
openssl s_client -connect api.example.com:443
```

---

**Помните**: Nginx - это мощный инструмент. Начните с простой конфигурации и постепенно добавляйте сложность по мере необходимости.
