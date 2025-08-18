import json

import pytest
from httpx import AsyncClient

from src.api.dependencies import get_db
from src.config import settings
from src.database import engine_null_pool, Base, async_session_maker_null_pool
from src.main import app
from src.models import *
from src.schemas.hotels import HotelAdd
from src.schemas.rooms import RoomAdd
from src.utils.db_manager import DBManager


async def get_db_null_pool():
    async with DBManager(session_factory=async_session_maker_null_pool) as db:
        yield db


@pytest.fixture(scope="function")
async def db() -> DBManager:
    async for db in get_db_null_pool():
        yield db

app.dependency_overrides[get_db] = get_db_null_pool


@pytest.fixture(scope="session")
async def ac() -> AsyncClient:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="session", autouse=True)
def check_test_mode():
    assert settings.MODE == "TEST"


@pytest.fixture(scope="session", autouse=True)
async def setup_database(check_test_mode):
    async with engine_null_pool.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture(scope="session", autouse=True)
async def add_data_in_database(setup_database):
    with open("tests/mock_hotels.json", "r") as file_hotels:
        hotels_data = json.load(file_hotels)
    with open("tests/mock_rooms.json", "r") as file_rooms:
        rooms_data = json.load(file_rooms)

    hotels = [HotelAdd.model_validate(hotel) for hotel in hotels_data]
    rooms = [RoomAdd.model_validate(room) for room in rooms_data]

    async with DBManager(session_factory=async_session_maker_null_pool) as db_:
        await db_.hotels.add_bulk(hotels)
        await db_.rooms.add_bulk(rooms)
        await db_.session_commit()


@pytest.fixture(scope="session", autouse=True)
async def register_user(add_data_in_database, ac):
    await ac.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "1234",
            "first_name": "Name",
            "last_name": "Name",
            "username": "username"
        }
    )
