import pytest
from httpx import AsyncClient


@pytest.mark.parametrize("hotel_id, date_from, date_to, status_code", [
    (1, "2024-08-01", "2024-08-10", 200),
    (1, "2024-08-20", "2024-08-10", 422),
    (2, "2024-08-01", "2025-09-10", 200),
])
async def test_get_rooms(ac, hotel_id, date_from, date_to, status_code):
    response = await ac.get(
        f"/hotels/{hotel_id}/rooms",
        params={
            "date_from": date_from,
            "date_to": date_to,
        },
    )

    assert response.status_code == status_code


@pytest.mark.parametrize("hotel_id, room_id, status_code, detail", [
    (1, 1, 200, None),
    (1, 2, 200, None),
    ("str", "str", 422, None),
    (1, "str", 422, None),
    ("str", 2, 422, None),
    (2, 5, 404, "Номер не найден"),
    (4, 2, 404, "Отель не найден"),
])
async def test_get_room(ac, hotel_id, room_id, status_code, detail):
    response = await ac.get(
        f"/hotels/{hotel_id}/rooms/{room_id}",
        params={"hotel_id": hotel_id, "room_id": room_id}
    )

    assert response.status_code == status_code
    room = response.json()
    if status_code == 200:
        assert room.get("hotel_id") == hotel_id
        assert room.get("id") == room_id
    elif status_code == 404:
        assert room.get("detail") == detail


@pytest.mark.parametrize("hotel_id, title, description, price, quantity, facilities_ids, status_code", [
    (1, "Делюкс Плюс", "Лучший номер отеля.", 250, 4, [1, 2], 200),
    (5, "Делюкс Плюс", "Лучший номер отеля.", 250, 4, [], 404),
    (1, 546, "Лучший номер отеля.", 250, 4, [], 422),
    (1, "Делюкс Плюс", "Лучший номер отеля.", "str", 4, [], 422),
    (1, "Делюкс Плюс", "Лучший номер отеля.", 250, 4, [], 200),
])
async def test_create_room(ac, hotel_id, title, description, price, quantity, facilities_ids, status_code):
    response = await ac.post(
        f"/hotels/{hotel_id}/rooms",
        json={
          "title": title,
          "description": description,
          "price": price,
          "quantity": quantity,
          "facilities_ids": facilities_ids
        }
    )

    assert response.status_code == status_code
    hotel = response.json()
    if status_code == 200:
        assert hotel['status'] == "OK"
        assert hotel["data"]["title"] == title
        assert hotel["data"]["description"] == description
        for facility in hotel["data"]["facilities"]:
            assert facility["id"] in facilities_ids
            assert facility["title"]
