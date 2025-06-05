import uvicorn
from fastapi import FastAPI, Query, Body

app = FastAPI()

hotels = [
    {"id": 1, "title": 'Sochi', "name": "Sochi"},
    {"id": 2, "title": "Dubai", "name": "Dubai"},
]


@app.get("/hotels")
def get_hotels(
        id: int | None = Query(None, description='Айдишник'),
        title: str | None = Query(None, description='Название отеля'),
):
    hotels_ = []
    for hotel in hotels:
        if id and hotel['id'] != id:
            continue
        if title and hotel['title'] != title:
            continue
        hotels_.append(hotel)
    return hotels_


@app.post("/hotels")
def create_hotel(title: str = Body(embed=True)):
    global hotels
    hotels.append({
        "id": hotels[-1]["id"] + 1,
        "title": title
    })
    return {"status": "OK"}


@app.put("/hotels/{hotel_id}")
def put_hotel(
        hotel_id: int,
        title: str = Body(),
        name: str = Body(),
):
    for hotel in hotels:
        if hotel['id'] == id:
            hotel['title'], hotel['name'] = title, name
    return {"status": "OK"}


@app.patch("/hotels/{hotel_id}")
def patch_hotel(
        hotel_id: int,
        title: str | None = Body(None),
        name: str | None = Body(None),
):
    for hotel in hotels:
        if hotel["id"] == id:
            if title:
                hotel["title"] = title
            elif name:
                hotel["name"] = name

    return {"status": "OK"}


@app.delete("/hotels/{hotel_id}")
def delete_hotel(id: int):
    global hotels
    hotels = [hotel for hotel in hotels if hotel['id'] != id]
    return {"status": "OK!"}


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
