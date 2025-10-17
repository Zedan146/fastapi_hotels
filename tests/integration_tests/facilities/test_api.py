import pytest


async def test_get_facilities(ac):
    response = await ac.get("/facilities")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.parametrize(
    "facility_title, status_code",
    [
        ("WI-FI", 409),
        ("", 422),
        ("Балкон", 200),
        ("Балкон", 409),
    ],
)
async def test_create_facility(ac, facility_title: str, status_code: int):
    response = await ac.post("/facilities", json={"title": facility_title})
    res = response.json()

    assert response.status_code == status_code
    assert isinstance(res, dict)
    if status_code == 200:
        assert res["data"]["title"] == facility_title
