import pytest

from tests.conftest import get_db_null_pool


@pytest.mark.parametrize(
    "room_id, date_from, date_to, status_code",
    [
        (1, "2024-08-01", "2024-08-10", 200),
        (1, "2024-08-02", "2024-08-11", 200),
        (1, "2024-08-03", "2024-08-12", 200),
        (1, "2024-08-04", "2024-08-13", 200),
        (1, "2024-08-05", "2024-08-14", 200),
        (1, "2024-08-06", "2024-08-15", 409),
        (1, "2024-08-17", "2024-08-25", 200),
    ],
)
async def test_create_booking(db, authenticated_ac, room_id, date_from, date_to, status_code):
    response = await authenticated_ac.post(
        "/bookings",
        json={
            "room_id": room_id,
            "date_from": date_from,
            "date_to": date_to,
        },
    )
    assert response.status_code == status_code
    if status_code == 200:
        res = response.json()
        assert isinstance(res, dict)
        assert res["status"] == "OK"
        assert "data" in res


@pytest.fixture(scope="module")
async def delete_all_bookings():
    async for _db in get_db_null_pool():
        await _db.bookings.delete()
        await _db.session_commit()


@pytest.mark.parametrize(
    "room_id, date_from, date_to, my_bookings",
    [
        (1, "2024-08-01", "2024-08-10", 1),
        (1, "2024-08-11", "2024-08-14", 2),
        (1, "2024-08-15", "2024-08-20", 3),
    ],
)
async def test_add_and_get_my_bookings(
    room_id, date_from, date_to, my_bookings, authenticated_ac, delete_all_bookings
):
    response_add_booking = await authenticated_ac.post(
        "/bookings",
        json={
            "room_id": room_id,
            "date_from": date_from,
            "date_to": date_to,
        },
    )
    assert response_add_booking.status_code == 200

    response_my_bookings = await authenticated_ac.get(
        "/bookings/me",
    )
    assert response_my_bookings.status_code == 200
    assert len(response_my_bookings.json()) == my_bookings
