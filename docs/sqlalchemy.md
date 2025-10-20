# 🗄️ SQLAlchemy - Шпаргалка

## Основы SQLAlchemy

SQLAlchemy - мощная ORM (Object-Relational Mapping) библиотека для Python, которая позволяет работать с базами данных через объекты Python.

### Установка
```bash
pip install sqlalchemy asyncpg  # для PostgreSQL
pip install sqlalchemy psycopg2-binary  # альтернатива для PostgreSQL
```

## Подключение к базе данных

### Синхронное подключение
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Создание движка
engine = create_engine("postgresql://user:password@localhost/dbname")

# Создание сессии
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Получение сессии
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### Асинхронное подключение
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Асинхронный движок
engine = create_async_engine("postgresql+asyncpg://user:password@localhost/dbname")

# Асинхронная сессия
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_async_db():
    async with AsyncSessionLocal() as session:
        yield session
```

## Модели (Models)

### Базовые модели
```python
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

### Современный стиль (SQLAlchemy 2.0)
```python
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
```

### Связи между таблицами

#### Один ко многим (One-to-Many)
```python
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    
    # Связь с постами
    posts: Mapped[list["Post"]] = relationship("Post", back_populates="author")

class Post(Base):
    __tablename__ = "posts"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str] = mapped_column(Text)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    
    # Обратная связь
    author: Mapped["User"] = relationship("User", back_populates="posts")
```

#### Многие ко многим (Many-to-Many)
```python
from sqlalchemy import Table

# Промежуточная таблица
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("role_id", Integer, ForeignKey("roles.id"))
)

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    
    roles: Mapped[list["Role"]] = relationship("Role", secondary=user_roles, back_populates="users")

class Role(Base):
    __tablename__ = "roles"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    
    users: Mapped[list["User"]] = relationship("User", secondary=user_roles, back_populates="roles")
```

## CRUD операции

### Создание (Create)
```python
# Синхронно
def create_user(db: Session, user_data: dict):
    user = User(**user_data)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# Асинхронно
async def create_user_async(db: AsyncSession, user_data: dict):
    user = User(**user_data)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
```

### Чтение (Read)
```python
# Получение всех записей
def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()

# Получение по ID
def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

# Фильтрация
def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

# Асинхронные версии
async def get_users_async(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(User).offset(skip).limit(limit))
    return result.scalars().all()

async def get_user_async(db: AsyncSession, user_id: int):
    result = await db.execute(select(User).filter(User.id == user_id))
    return result.scalar_one_or_none()
```

### Обновление (Update)
```python
# Полное обновление
def update_user(db: Session, user_id: int, user_data: dict):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        for key, value in user_data.items():
            setattr(user, key, value)
        db.commit()
        db.refresh(user)
    return user

# Частичное обновление
def patch_user(db: Session, user_id: int, **kwargs):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        db.commit()
        db.refresh(user)
    return user
```

### Удаление (Delete)
```python
def delete_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
        return True
    return False
```

## Запросы (Queries)

### Базовые запросы
```python
from sqlalchemy import select, and_, or_, not_

# SELECT
users = db.query(User).all()

# SELECT с условиями
active_users = db.query(User).filter(User.is_active == True).all()

# SELECT с множественными условиями
users = db.query(User).filter(
    and_(User.is_active == True, User.created_at > datetime.now() - timedelta(days=30))
).all()

# Современный стиль (SQLAlchemy 2.0)
stmt = select(User).where(User.is_active == True)
result = await db.execute(stmt)
users = result.scalars().all()
```

### Сортировка и пагинация
```python
# Сортировка
users = db.query(User).order_by(User.created_at.desc()).all()

# Пагинация
def get_users_paginated(db: Session, page: int = 1, per_page: int = 10):
    offset = (page - 1) * per_page
    return db.query(User).offset(offset).limit(per_page).all()

# Асинхронная пагинация
async def get_users_paginated_async(db: AsyncSession, page: int = 1, per_page: int = 10):
    offset = (page - 1) * per_page
    stmt = select(User).offset(offset).limit(per_page)
    result = await db.execute(stmt)
    return result.scalars().all()
```

### Связи и JOIN
```python
# JOIN с загрузкой связанных данных
users_with_posts = db.query(User).join(Post).all()

# Eager loading (загрузка связанных данных)
from sqlalchemy.orm import joinedload, selectinload

users = db.query(User).options(joinedload(User.posts)).all()

# Асинхронный JOIN
async def get_users_with_posts(db: AsyncSession):
    stmt = select(User).options(joinedload(User.posts))
    result = await db.execute(stmt)
    return result.scalars().all()
```

### Агрегатные функции
```python
from sqlalchemy import func

# Подсчет
user_count = db.query(func.count(User.id)).scalar()

# Группировка
from sqlalchemy import group_by

user_stats = db.query(
    User.is_active,
    func.count(User.id).label('count')
).group_by(User.is_active).all()
```

## Транзакции

### Автоматические транзакции
```python
def create_user_with_profile(db: Session, user_data: dict, profile_data: dict):
    try:
        # Создание пользователя
        user = User(**user_data)
        db.add(user)
        db.flush()  # Получаем ID без коммита
        
        # Создание профиля
        profile = Profile(user_id=user.id, **profile_data)
        db.add(profile)
        
        db.commit()
        return user
    except Exception as e:
        db.rollback()
        raise e
```

### Ручные транзакции
```python
from sqlalchemy import text

def transfer_money(db: Session, from_user_id: int, to_user_id: int, amount: float):
    try:
        # Снятие денег
        db.execute(
            text("UPDATE accounts SET balance = balance - :amount WHERE user_id = :user_id"),
            {"amount": amount, "user_id": from_user_id}
        )
        
        # Зачисление денег
        db.execute(
            text("UPDATE accounts SET balance = balance + :amount WHERE user_id = :user_id"),
            {"amount": amount, "user_id": to_user_id}
        )
        
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
```

## Миграции с Alembic

### Установка и настройка
```bash
pip install alembic
alembic init alembic
```

### Создание миграции
```bash
# Автоматическое создание
alembic revision --autogenerate -m "Add users table"

# Ручное создание
alembic revision -m "Add users table"
```

### Применение миграций
```bash
# Применить все миграции
alembic upgrade head

# Применить конкретную миграцию
alembic upgrade +1

# Откат миграции
alembic downgrade -1
```

### Пример миграции
```python
"""Add users table

Revision ID: abc123
Revises: 
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'abc123'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

def downgrade():
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
```

## Лучшие практики

### 1. Используйте сессии правильно
```python
# Хорошо
def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

# Плохо - не закрываете сессию
def bad_get_user(user_id: int):
    db = SessionLocal()
    return db.query(User).filter(User.id == user_id).first()
```

### 2. Обрабатывайте исключения
```python
def safe_create_user(db: Session, user_data: dict):
    try:
        user = User(**user_data)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except IntegrityError:
        db.rollback()
        raise ValueError("User with this email already exists")
    except Exception as e:
        db.rollback()
        raise e
```

### 3. Используйте индексы
```python
class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
```

### 4. Оптимизируйте запросы
```python
# Плохо - N+1 проблема
users = db.query(User).all()
for user in users:
    print(user.posts)  # Каждый раз новый запрос

# Хорошо - eager loading
users = db.query(User).options(joinedload(User.posts)).all()
for user in users:
    print(user.posts)  # Данные уже загружены
```

### 5. Используйте connection pooling
```python
from sqlalchemy.pool import QueuePool

engine = create_engine(
    "postgresql://user:password@localhost/dbname",
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)
```

## Отладка и профилирование

### Логирование SQL запросов
```python
import logging

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
```

### Профилирование запросов
```python
from sqlalchemy import event
import time

@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    context._query_start_time = time.time()

@event.listens_for(Engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.time() - context._query_start_time
    if total > 0.1:  # Логируем медленные запросы
        print(f"Slow query: {total:.2f}s - {statement}")
```
