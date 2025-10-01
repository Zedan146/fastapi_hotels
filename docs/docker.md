# Docker
## Основные команды

docker run --name booking_back -p 7777:8000 --network=myNetwork booking_image

### Образы(images)
Создание образа    
`docker build -t <имя-образа> .`

Показать список всех образов        
`docker images`

Удалить образ       
`docker rmi <имя-образа>`

### Контейнеры
Создание контейнера     
`docker run <имя-образа>`

Параметры:

- `-d` - запуск в фоновом режиме
- `-p 1234:5432` - прокидывание портов
- `--name my-container` - задание имени контейнера
- `-v /my/dir:/container/dir` - прокидывание вольюмов
- `--network my-network>` - запуск контейнера внутри Docker сети

Показать список всех запущенных контейнеров        
`docker ps`

Показать список всех контейнеров        
`docker ps -a`

Удалить контейнер       
`docker rm <имя-контейнера>`

Удалить запущенный контейнер        
`docker rm -f <имя-контейнера>`

### Docker сети
Создать Docker сеть     
`docker network create <имя-сети>`

## Docker Compose
Создание образов
```
docker compose build
```

Поднятие всех контейнеров       
`docker compose up`

Поднятие всех контейнеров + сборка образов      
`docker compose up --build`

Поднятие всех контейнеров с кастомным названием файла       
`docker compose -f docker-compose-custom.yml up`


## Команды для проекта
### Создание Docker сети
`docker network create myNetwork`

### База данных
```
docker run --name booking_db \
    -p 6432:5432 \                                          
    -e POSTGRES_USER=abcde \    
    -e POSTGRES_PASSWORD=abdasd8as78d678asdasdjlcde \
    -e POSTGRES_DB=booking \
    --network=myNetwork \
    --volume pg-booking-data:/var/lib/postgresql/data \
    -d postgres:16
```

### Redis
```
docker run --name booking_cache \
    -p 7379:6379 \
    --network=myNetwork \
    -d redis
```

### Celery
```
docker run --name booking_celery_worker \
    --network=myNetwork \
    booking_image \
    celery --app=src.tasks.celery_app:celery_instance worker -l INFO
```

### Celery beat
```
docker run --name booking_celery_beat \
    --network=myNetwork \
    booking_image \
    celery --app=src.tasks.celery_app:celery_instance beat -l INFO
```

### Nginx
Без SSL (https)        
```
docker run --name booking_nginx \
    --volume ./nginx.conf:/etc/nginx/nginx.conf \
    --network=myNetwork \
    --rm -p 80:80 nginx
```

С SSL (https)        
```
docker run --name booking_nginx \
    --volume ./nginx.conf:/etc/nginx/nginx.conf \
    --volume /etc/letsencrypt:/etc/letsencrypt \
    --volume /var/lib/letsencrypt:/var/lib/letsencrypt \
    --network=myNetwork \
    --rm -p 80:80 -p 443:443 -d nginx
```