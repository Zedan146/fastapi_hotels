# 🚀 GitLab CI/CD - Шпаргалка

## Что такое GitLab CI/CD

GitLab CI/CD - это встроенная система непрерывной интеграции и непрерывного развертывания, которая автоматизирует процесс сборки, тестирования и развертывания приложений.

## Зачем нужен CI/CD

### Преимущества:
- **Автоматизация** - автоматическая сборка, тестирование и развертывание
- **Качество кода** - автоматические проверки линтера и тестов
- **Быстрая обратная связь** - немедленное уведомление о проблемах
- **Консистентность** - одинаковые процессы для всех разработчиков
- **Безопасность** - автоматическое развертывание без ручного вмешательства

## Основы GitLab CI/CD

### Структура .gitlab-ci.yml
```yaml
# Определение стадий
stages:
  - build
  - test
  - deploy

# Переменные
variables:
  DOCKER_IMAGE: "my-app"
  DOCKER_TAG: "latest"

# Кэширование
cache:
  paths:
    - .venv/
    - node_modules/

# Глобальные настройки
default:
  image: python:3.11
  before_script:
    - echo "Starting job"

# Определение джобов
job_name:
  stage: build
  script:
    - echo "Building application"
  only:
    - main
```

## Установка и настройка

### 1. Установка GitLab Runner

#### На Ubuntu/Debian:
```bash
# Добавление репозитория
curl -L "https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.deb.sh" | sudo bash

# Установка
sudo apt-get install gitlab-runner

# Запуск сервиса
sudo systemctl start gitlab-runner
sudo systemctl enable gitlab-runner
```

#### На CentOS/RHEL:
```bash
# Добавление репозитория
curl -L "https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.rpm.sh" | sudo bash

# Установка
sudo yum install gitlab-runner

# Запуск сервиса
sudo systemctl start gitlab-runner
sudo systemctl enable gitlab-runner
```

#### На macOS:
```bash
# Установка через Homebrew
brew install gitlab-runner

# Запуск
brew services start gitlab-runner
```

### 2. Регистрация Runner

```bash
# Регистрация runner
sudo gitlab-runner register

# Введите URL GitLab
Please enter the gitlab-ci coordinator URL (e.g. https://gitlab.com/):
https://gitlab.com/

# Введите токен регистрации
Please enter the gitlab-ci token for this runner:
<your-registration-token>

# Введите описание
Please enter the gitlab-ci description for this runner:
my-runner

# Введите теги
Please enter the gitlab-ci tags for this runner (comma separated):
docker,linux

# Выберите executor
Please enter the executor: ssh, docker+machine, docker-ssh+machine, kubernetes, docker, parallels, virtualbox, docker-ssh, shell:
docker

# Выберите Docker image по умолчанию
Please enter the Docker image (e.g. ruby:2.6):
python:3.11
```

### 3. Проверка статуса Runner

```bash
# Проверка статуса
sudo gitlab-runner status

# Список зарегистрированных runners
sudo gitlab-runner list

# Проверка конфигурации
sudo gitlab-runner verify
```

## Конфигурация проекта

### Базовый .gitlab-ci.yml
```yaml
# Версия GitLab CI
version: '3'

# Определение стадий
stages:
  - build
  - test
  - security
  - deploy

# Переменные
variables:
  DOCKER_DRIVER: overlay2
  DOCKER_TLS_CERTDIR: "/certs"
  DOCKER_IMAGE: "fastapi-hotels"
  DOCKER_TAG: "$CI_COMMIT_SHORT_SHA"

# Кэширование
cache:
  key: "$CI_COMMIT_REF_SLUG"
  paths:
    - .venv/
    - .pytest_cache/
    - node_modules/

# Глобальные настройки
default:
  image: python:3.11
  before_script:
    - python -m pip install --upgrade pip
    - pip install -r requirements.txt

# Стадия сборки
build:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  before_script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
  script:
    - docker build -t $CI_REGISTRY_IMAGE:$DOCKER_TAG .
    - docker push $CI_REGISTRY_IMAGE:$DOCKER_TAG
  only:
    - main
    - develop

# Стадия тестирования
test:
  stage: test
  services:
    - postgres:13
    - redis:6
  variables:
    POSTGRES_DB: test_db
    POSTGRES_USER: test_user
    POSTGRES_PASSWORD: test_password
    REDIS_URL: redis://redis:6379/0
  script:
    - pytest tests/ -v --cov=src --cov-report=xml
  coverage: '/TOTAL.*\s+(\d+%)$/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
    paths:
      - coverage.xml
    expire_in: 1 week

# Стадия безопасности
security:
  stage: security
  script:
    - pip install safety bandit
    - safety check
    - bandit -r src/ -f json -o bandit-report.json
  artifacts:
    reports:
      security: bandit-report.json
    expire_in: 1 week

# Стадия развертывания
deploy:
  stage: deploy
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker-compose -f docker-compose-ci.yml up -d
    - docker exec booking_nginx nginx -s reload
  only:
    - main
  when: manual
```

## Продвинутые конфигурации

### Многоэтапный пайплайн
```yaml
stages:
  - prepare
  - build
  - test
  - security
  - deploy-staging
  - deploy-production

# Подготовка окружения
prepare:
  stage: prepare
  script:
    - echo "Preparing environment"
    - mkdir -p artifacts
  artifacts:
    paths:
      - artifacts/
    expire_in: 1 hour

# Сборка для разных платформ
build-linux:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker build -t $DOCKER_IMAGE:linux-$CI_COMMIT_SHORT_SHA .
  only:
    - main

build-windows:
  stage: build
  image: mcr.microsoft.com/windows/servercore:ltsc2019
  script:
    - echo "Building for Windows"
  only:
    - main

# Параллельные тесты
test-unit:
  stage: test
  script:
    - pytest tests/unit/ -v
  parallel: 2

test-integration:
  stage: test
  services:
    - postgres:13
    - redis:6
  script:
    - pytest tests/integration/ -v
  parallel: 3

# Условное развертывание
deploy-staging:
  stage: deploy-staging
  script:
    - echo "Deploying to staging"
    - docker-compose -f docker-compose-staging.yml up -d
  environment:
    name: staging
    url: https://staging.example.com
  only:
    - develop

deploy-production:
  stage: deploy-production
  script:
    - echo "Deploying to production"
    - docker-compose -f docker-compose-prod.yml up -d
  environment:
    name: production
    url: https://example.com
  only:
    - main
  when: manual
```

### Конфигурация с матрицей
```yaml
# Тестирование на разных версиях Python
test-matrix:
  stage: test
  image: python:$PYTHON_VERSION
  variables:
    PYTHON_VERSION: ["3.9", "3.10", "3.11", "3.12"]
  script:
    - python --version
    - pip install -r requirements.txt
    - pytest tests/ -v
  parallel:
    matrix:
      - PYTHON_VERSION: ["3.9", "3.10", "3.11", "3.12"]
```

### Конфигурация с кэшированием
```yaml
# Кэширование зависимостей
cache-pip:
  stage: build
  script:
    - pip install -r requirements.txt
  cache:
    key: pip-$CI_COMMIT_REF_SLUG
    paths:
      - .venv/
    policy: pull-push

# Кэширование Docker слоев
cache-docker:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker build --cache-from $CI_REGISTRY_IMAGE:latest -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
  cache:
    key: docker-$CI_COMMIT_REF_SLUG
    paths:
      - .docker-cache/
    policy: pull-push
```

## Переменные окружения

### Глобальные переменные
```yaml
variables:
  # Системные переменные
  CI: "true"
  GIT_STRATEGY: "clone"
  GIT_DEPTH: "0"
  
  # Пользовательские переменные
  DOCKER_IMAGE: "fastapi-hotels"
  DATABASE_URL: "postgresql://user:pass@localhost/db"
  REDIS_URL: "redis://localhost:6379/0"
  
  # Переменные для тестирования
  TEST_DATABASE_URL: "postgresql://test:test@localhost/test_db"
  TEST_REDIS_URL: "redis://localhost:6379/1"
```

### Переменные по стадиям
```yaml
build:
  stage: build
  variables:
    BUILD_ENV: "production"
    DOCKER_TAG: "latest"
  script:
    - echo "Building for $BUILD_ENV"

test:
  stage: test
  variables:
    TEST_ENV: "testing"
    PYTEST_ARGS: "-v --cov"
  script:
    - echo "Testing in $TEST_ENV"
    - pytest $PYTEST_ARGS
```

### Секретные переменные
```yaml
# В GitLab UI: Settings > CI/CD > Variables
# Добавьте переменные с типом "Variable" или "File"

deploy:
  stage: deploy
  script:
    - echo "Deploying with secret: $SECRET_KEY"
    - echo "Using certificate: $SSL_CERTIFICATE"
  only:
    - main
```

## Артефакты и отчеты

### Сохранение артефактов
```yaml
build:
  stage: build
  script:
    - make build
    - make test
  artifacts:
    paths:
      - dist/
      - coverage.xml
      - test-results/
    reports:
      junit: test-results/junit.xml
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
    expire_in: 1 week
    when: always

# Использование артефактов в других джобах
deploy:
  stage: deploy
  dependencies:
    - build
  script:
    - ls -la dist/  # Артефакты доступны
    - cp dist/app.tar.gz /deploy/
```

### Отчеты о покрытии
```yaml
test:
  stage: test
  script:
    - pytest --cov=src --cov-report=xml --cov-report=html
  coverage: '/TOTAL.*\s+(\d+%)$/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
    paths:
      - htmlcov/
    expire_in: 1 week
```

## Уведомления и интеграции

### Уведомления в Slack
```yaml
# В GitLab UI: Settings > Integrations > Slack
# Или через webhook

notify-slack:
  stage: deploy
  script:
    - echo "Deployment completed"
  after_script:
    - |
      curl -X POST -H 'Content-type: application/json' \
      --data '{"text":"Deployment to production completed!"}' \
      $SLACK_WEBHOOK_URL
  only:
    - main
```

### Уведомления по email
```yaml
# В GitLab UI: Settings > CI/CD > General pipelines
# Настройте уведомления по email

# Или через script
notify-email:
  stage: deploy
  script:
    - |
      if [ "$CI_PIPELINE_STATUS" = "success" ]; then
        echo "Pipeline succeeded" | mail -s "CI Success" admin@example.com
      else
        echo "Pipeline failed" | mail -s "CI Failed" admin@example.com
      fi
```

## Мониторинг и отладка

### Логирование
```yaml
debug-job:
  stage: test
  script:
    - echo "Starting debug job"
    - echo "CI_COMMIT_SHA: $CI_COMMIT_SHA"
    - echo "CI_COMMIT_REF_NAME: $CI_COMMIT_REF_NAME"
    - echo "CI_PIPELINE_ID: $CI_PIPELINE_ID"
    - echo "CI_JOB_ID: $CI_JOB_ID"
    - echo "CI_RUNNER_DESCRIPTION: $CI_RUNNER_DESCRIPTION"
    - env | grep CI_
```

### Отладка Docker
```yaml
debug-docker:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker version
    - docker info
    - docker images
    - docker ps -a
```

### Проверка состояния
```yaml
health-check:
  stage: deploy
  script:
    - echo "Checking application health"
    - curl -f http://localhost:8000/health || exit 1
    - echo "Application is healthy"
```

## Лучшие практики

### 1. Оптимизация производительности
```yaml
# Используйте кэширование
cache:
  key: "$CI_COMMIT_REF_SLUG"
  paths:
    - .venv/
    - node_modules/
    - .pytest_cache/

# Параллельные джобы
test:
  stage: test
  parallel: 4
  script:
    - pytest tests/ -n 4

# Условное выполнение
deploy:
  stage: deploy
  script:
    - echo "Deploying"
  only:
    - main
  when: manual
```

### 2. Безопасность
```yaml
# Используйте секретные переменные
deploy:
  script:
    - echo "Using secret: $SECRET_KEY"
  only:
    - main

# Ограничьте доступ
deploy-production:
  stage: deploy
  script:
    - echo "Deploying to production"
  only:
    - main
  when: manual
  allow_failure: false
```

### 3. Обработка ошибок
```yaml
# Настройка retry
test:
  stage: test
  script:
    - pytest tests/
  retry:
    max: 2
    when:
      - runner_system_failure
      - stuck_or_timeout_failure

# Условное выполнение
deploy:
  stage: deploy
  script:
    - echo "Deploying"
  when: on_success
  allow_failure: false
```

### 4. Документация
```yaml
# Добавляйте описания к джобам
build:
  stage: build
  script:
    - echo "Building application"
  description: "Build Docker image for the application"

test:
  stage: test
  script:
    - pytest tests/
  description: "Run unit and integration tests"
```

## Troubleshooting

### Частые проблемы

#### 1. Runner не запускается
```bash
# Проверка статуса
sudo gitlab-runner status

# Перезапуск
sudo systemctl restart gitlab-runner

# Проверка логов
sudo journalctl -u gitlab-runner -f
```

#### 2. Проблемы с Docker
```yaml
# Добавьте привилегированный режим
build:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  variables:
    DOCKER_TLS_CERTDIR: "/certs"
    DOCKER_DRIVER: overlay2
  script:
    - docker build -t myapp .
```

#### 3. Проблемы с кэшем
```yaml
# Очистка кэша
clear-cache:
  stage: build
  script:
    - echo "Clearing cache"
  cache:
    key: "$CI_COMMIT_REF_SLUG"
    paths:
      - .venv/
    policy: pull
```

#### 4. Таймауты
```yaml
# Увеличение таймаута
long-running-job:
  stage: test
  script:
    - pytest tests/ --timeout=300
  timeout: 1h
```

## Команды GitLab Runner

### Управление Runner
```bash
# Регистрация
gitlab-runner register

# Список runners
gitlab-runner list

# Проверка конфигурации
gitlab-runner verify

# Запуск в debug режиме
gitlab-runner run --debug

# Остановка
gitlab-runner stop

# Запуск
gitlab-runner start

# Перезапуск
gitlab-runner restart
```

### Управление джобами
```bash
# Запуск конкретного джоба
gitlab-runner exec docker test

# Запуск с переменными
gitlab-runner exec docker test --env VAR1=value1 --env VAR2=value2

# Запуск с кастомным image
gitlab-runner exec docker test --docker-image python:3.11
```

## Интеграция с проектом

### Конфигурация для FastAPI Hotels
```yaml
# .gitlab-ci.yml для проекта
stages:
  - build
  - lint-format
  - migrations
  - test
  - deploy

variables:
  DOCKER_IMAGE: "booking-api-image"
  DOCKER_TAG: "latest"

build-job:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  before_script:
    - cp ${ENV} .env
    - cp ${TEST_ENV} .env-test
  script:
    - docker build -t $DOCKER_IMAGE:$DOCKER_TAG .
  only:
    - main
    - develop

lint:
  stage: lint-format
  image: $DOCKER_IMAGE:$DOCKER_TAG
  script:
    - ruff check
  only:
    - main
    - develop

format:
  stage: lint-format
  image: $DOCKER_IMAGE:$DOCKER_TAG
  script:
    - ruff format --check
  only:
    - main
    - develop

migrations:
  stage: migrations
  image: $DOCKER_IMAGE:$DOCKER_TAG
  services:
    - postgres:13
  variables:
    POSTGRES_DB: test_db
    POSTGRES_USER: test_user
    POSTGRES_PASSWORD: test_password
  script:
    - alembic upgrade head
  only:
    - main
    - develop

tests:
  stage: test
  image: $DOCKER_IMAGE:$DOCKER_TAG
  services:
    - postgres:13
    - redis:6
  variables:
    POSTGRES_DB: test_db
    POSTGRES_USER: test_user
    POSTGRES_PASSWORD: test_password
    REDIS_URL: redis://redis:6379/0
  script:
    - pytest -s -v --cov=src --cov-report=xml
  coverage: '/TOTAL.*\s+(\d+%)$/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
    paths:
      - coverage.xml
    expire_in: 1 week
  only:
    - main
    - develop

deploy-job:
  stage: deploy
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker-compose -f docker-compose-ci.yml up -d
    - docker exec booking_nginx nginx -s reload
  only:
    - main
  when: manual
```

## Мониторинг пайплайнов

### Метрики и аналитика
```yaml
# Добавление метрик
collect-metrics:
  stage: test
  script:
    - echo "Collecting metrics"
    - echo "test_duration=$(date +%s)" >> metrics.txt
    - echo "test_count=$(find tests/ -name '*.py' | wc -l)" >> metrics.txt
  artifacts:
    reports:
      metrics: metrics.txt
```

### Уведомления о статусе
```yaml
# Уведомление о успехе
notify-success:
  stage: deploy
  script:
    - echo "Deployment successful"
  when: on_success
  only:
    - main

# Уведомление о неудаче
notify-failure:
  stage: deploy
  script:
    - echo "Deployment failed"
  when: on_failure
  only:
    - main
```

---

