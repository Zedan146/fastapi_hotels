async def test_get_facilities(ac):
    response = await ac.get("/facilities")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


async def test_create_facility(ac):
    facility_title = "WI-FI"
    response = await ac.post("/facilities", json={"title": facility_title})
    res = response.json()

    assert response.status_code == 200
    assert isinstance(res, dict)
    assert res["data"]["title"] == facility_title
