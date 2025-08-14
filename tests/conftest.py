import json

import pytest
from httpx import AsyncClient
from sqlalchemy import insert

from src.config import settings
from src.database import engine_null_pool, Base
from src.main import app
from src.models import *


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
        async with engine_null_pool.begin() as conn:
            await conn.execute(insert(HotelsModel), hotels_data)

    with open("tests/mock_rooms.json", "r") as file_rooms:
        rooms_data = json.load(file_rooms)
        async with engine_null_pool.begin() as conn:
            await conn.execute(insert(RoomsModel), rooms_data)


@pytest.fixture(scope="session", autouse=True)
async def register_user(add_data_in_database):
    async with AsyncClient(app=app, base_url="http://test") as ac:
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
