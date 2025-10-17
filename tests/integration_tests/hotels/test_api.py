import pytest


@pytest.mark.parametrize(
    "date_from, date_to, status_code",
    [
        ("2024-08-01", "2024-08-10", 200),
        ("2024-08-20", "2024-08-10", 422),
        ("2024-08-01", "2025-09-10", 200),
    ],
)
async def test_get_hotels(ac, date_from, date_to, status_code):
    response = await ac.get(
        "/hotels",
        params={
            "date_from": date_from,
            "date_to": date_to,
        },
    )

    assert response.status_code == status_code


@pytest.mark.parametrize(
    "hotel_id, status_code",
    [
        (1, 200),
        (2, 200),
        (6, 404),
    ],
)
async def test_get_hotel(ac, hotel_id, status_code):
    response = await ac.get(f"/hotels/{hotel_id}", params={"hotel_id": hotel_id})

    assert response.status_code == status_code
    hotel = response.json()
    if status_code == 200:
        assert hotel["title"]
        assert hotel["location"]


@pytest.mark.parametrize(
    "title, location, status_code",
    [
        ("Отель Бирсон", "Сочи, ул. Матросова, 13", 200),
        (12321, "Сочи, ул. Матросова, 13", 422),
        ("Отель Бирсон", 3123, 422),
        ("Аль-Халиф", "Дубай, ул. Кан, 3", 200),
    ],
)
async def test_create_hotel(ac, title, location, status_code):
    response = await ac.post(
        "/hotels",
        json={
            "title": title,
            "location": location,
        },
    )

    assert response.status_code == status_code
    hotel = response.json()
    if status_code == 200:
        assert hotel["status"] == "OK"
        assert "location" in hotel["data"]
        assert "title" in hotel["data"]
        assert hotel["data"]["title"] == title
        assert hotel["data"]["location"] == location


@pytest.mark.parametrize(
    "hotel_id, title, location, status_code",
    [
        (1, "test_title", "test_location", 200),
        (2, None, "test_location", 422),
        (3, "test_title", None, 422),
        (10, "test_title", "test_location", 404),
        (10, None, None, 422),
    ],
)
async def test_edit_hotel(ac, hotel_id, title, location, status_code):
    json_data = {}
    if title:
        json_data["title"] = title
    if location:
        json_data["location"] = location

    response = await ac.put(f"/hotels/{hotel_id}", json=json_data)

    assert response.status_code == status_code
    hotel = response.json()
    if status_code == 200:
        assert hotel["status"] == "OK"
    if status_code == 422:
        if not title:
            assert "title" in hotel["detail"][0]["loc"]
            if not location:
                assert "location" in hotel["detail"][1]["loc"]
        elif not location:
            assert "location" in hotel["detail"][0]["loc"]


@pytest.mark.parametrize(
    "hotel_id, update_data, status_code",
    [
        (1, {"title": "test_title", "location": "test_location"}, 200),
        (2, {"title": "test_title"}, 200),
        (3, {"location": "test_location"}, 200),
        (10, {"title": "test_title", "location": "test_location"}, 404),
        (10, {}, 404),
        (3, {}, 400),
    ],
)
async def test_edit_hotel_partially(ac, hotel_id, update_data, status_code, original_hotel_data):
    response = await ac.patch(f"/hotels/{hotel_id}", json=update_data)

    assert response.status_code == status_code
    hotel = response.json()
    if status_code == 200:
        assert hotel["status"] == "OK"
        get_hotel = await ac.get(f"/hotels/{hotel_id}")
        assert get_hotel.status_code == 200
        json_get_hotel = get_hotel.json()

        if update_data.get("title"):
            assert json_get_hotel["title"] == update_data["title"]
        else:
            assert json_get_hotel["title"] == original_hotel_data["title"]

        if update_data.get("location"):
            assert json_get_hotel["location"] == update_data["location"]
        else:
            assert json_get_hotel["location"] == original_hotel_data["location"]


@pytest.mark.parametrize(
    "hotel_id, status_code",
    [
        (4, 200),
        (5, 200),
        (5, 404),
    ],
)
async def test_delete_hotels(ac, hotel_id, status_code):
    response = await ac.delete(f"/hotels/{hotel_id}")

    assert response.status_code == status_code
