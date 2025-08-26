import pytest


@pytest.mark.parametrize("date_from, date_to, status_code", [
    ("2024-08-01", "2024-08-10", 200),
    ("2024-08-20", "2024-08-10", 422),
    ("2024-08-01", "2025-09-10", 200),
])
async def test_get_hotels(ac, date_from, date_to, status_code):
    response = await ac.get(
        "/hotels",
        params={
            "date_from": date_from,
            "date_to": date_to,
        },
    )

    assert response.status_code == status_code


@pytest.mark.parametrize("hotel_id, status_code", [
    (1, 200),
    (2, 200),
    (6, 404),
])
async def test_get_hotel(ac, hotel_id, status_code):
    response = await ac.get(f"/hotels/{hotel_id}", params={"hotel_id": hotel_id})

    assert response.status_code == status_code
    hotel = response.json()
    if status_code == 200:
        assert hotel["title"]
        assert hotel["location"]
