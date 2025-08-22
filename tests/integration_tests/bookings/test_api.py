import pytest
from sqlalchemy import delete

from src.models import BookingsModel

bookings_count = 0


@pytest.mark.parametrize("room_id, date_from, date_to, status_code", [
    (1, "2024-08-01", "2024-08-10", 200),
    (1, "2024-08-02", "2024-08-11", 200),
    (1, "2024-08-03", "2024-08-12", 200),
    (1, "2024-08-04", "2024-08-13", 200),
    (1, "2024-08-05", "2024-08-14", 200),
    (1, "2024-08-06", "2024-08-15", 500),
    (1, "2024-08-17", "2024-08-25", 200),
])
async def test_create_booking(
        db,
        authenticated_ac,
        room_id,
        date_from,
        date_to,
        status_code
):
    # room_id = (await db.rooms.get_all())[0].id
    response = await authenticated_ac.post(
        "/bookings",
        json={
            "room_id": room_id,
            "date_from": date_from,
            "date_to": date_to,
        }
    )
    assert response.status_code == status_code
    if status_code == 200:
        res = response.json()
        assert isinstance(res, dict)
        assert res["status"] == "OK"
        assert "data" in res


@pytest.fixture(scope="function")
async def delete_all_bookings(check_test_mode, db):
    delete_stmt = delete(BookingsModel).returning(BookingsModel)
    res = await db.session.execute(delete_stmt)
    await db.session_commit()


@pytest.mark.parametrize("room_id, date_from, date_to, status_code, my_bookings", [
    (1, "2024-08-01", "2024-08-10", 200, 1),
    (1, "2024-08-11", "2024-08-14", 200, 2),
    (1, "2024-08-15", "2024-08-20", 200, 3),
])
async def test_add_and_get_my_bookings(
        delete_all_bookings,
        authenticated_ac,
        room_id,
        date_from,
        date_to,
        status_code,
        my_bookings,

):
    response_add_booking = await authenticated_ac.post(
        "/bookings",
        json={
            "room_id": room_id,
            "date_from": date_from,
            "date_to": date_to,
        }
    )
    assert response_add_booking.status_code == status_code

    response_my_bookings = await authenticated_ac.get(
        "/bookings/me",
    )
    assert response_my_bookings.status_code == 200
    global bookings_count
    if response_my_bookings.status_code == 200:
        bookings_count += 1
    assert bookings_count == my_bookings
