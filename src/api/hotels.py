from fastapi import Query, APIRouter, Body

from sqlalchemy import insert, select

from src.api.dependencies import PaginationDep
from src.database import async_session_maker
from src.models.hotels import HotelsModel
from src.schemas.hotels import HotelPATCH, Hotel

router = APIRouter(prefix="/hotels", tags=["Отели"])


@router.get("", summary="Получение отелей")
async def get_hotels(
        pagination: PaginationDep,
        title: str | None = Query(None, description='Название отеля'),
        location: str | None = Query(None, description="Адрес отеля"),
):
    per_page = pagination.per_page or 5
    async with async_session_maker() as session:
        query = select(HotelsModel)
        if title:
            query = (
                query
                .filter(HotelsModel.title.ilike(f"%{title}%"))
            )
        if location:
            query = (
                query
                .filter(HotelsModel.location.ilike(f"%{location}%"))
            )
        query = (
            query
            .limit(per_page)
            .offset(per_page * (pagination.page - 1))
        )
        # Вывод сырого SQL-запроса в консоль
        print(query.compile(compile_kwargs={"literal_binds": True}))

        result = await session.execute(query)
        hotels = result.scalars().all()
        return hotels


@router.post("", summary="Добавление отеля")
async def create_hotel(hotel_data: Hotel = Body(openapi_examples={
    "1": {
        "summary": "Сочи",
        "value": {
            "title": "Отель Бирсон",
            "location": "Сочи, ул. Матросова, 13"
        }
    },
    "2": {
        "summary": "Дубай",
        "value": {
            "title": "Аль-Халиф",
            "location": "Дубай, ул. Кан, 3"
        }
    }
})):
    async with async_session_maker() as session:
        add_hotel_stmt = insert(HotelsModel).values(**hotel_data.model_dump())
        await session.execute(add_hotel_stmt)
        await session.commit()

    return {"status": "OK"}


@router.put("/{hotel_id}", summary="Изменение отеля")
def put_hotel(hotel_id: int, hotel_data: Hotel):
    for hotel in hotels:
        if hotel['id'] == hotel_id:
            hotel['title'], hotel['name'] = hotel_data.title, hotel_data.name
    return {"status": "OK"}


@router.patch("/{hotel_id}", summary="Частичное изменение отеля")
def patch_hotel(hotel_id: int, hotel_data: HotelPATCH):
    for hotel in hotels:
        if hotel["id"] == hotel_id:
            if hotel_data.title:
                hotel["title"] = hotel_data.title
            if hotel_data.name:
                hotel["name"] = hotel_data.name

    return {"status": "OK"}


@router.delete("/{hotel_id}", summary="Удаление отеля")
def delete_hotel(hotel_id: int):
    global hotels
    hotels = [hotel for hotel in hotels if hotel['id'] != hotel_id]
    return {"status": "OK!"}
