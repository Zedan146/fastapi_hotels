from fastapi import Query, APIRouter, Body

from src.repositories.hotels import HotelsRepository
from src.api.dependencies import PaginationDep
from src.database import async_session_maker
from src.schemas.hotels import HotelPATCH, HotelAdd

router = APIRouter(prefix="/hotels", tags=["Отели"])


@router.get("/{hotel_id}", summary="Получение одного отеля")
async def get_one_hotel(hotel_id: int):
    async with async_session_maker() as session:
        return await HotelsRepository(session).get_one_or_none(id=hotel_id)


@router.get("", summary="Получение отелей")
async def get_hotels(
        pagination: PaginationDep,
        title: str | None = Query(None, description='Название отеля'),
        location: str | None = Query(None, description="Адрес отеля"),
):
    per_page = pagination.per_page or 5
    async with async_session_maker() as session:
        return await HotelsRepository(session).get_all(
            title=title,
            location=location,
            limit=per_page,
            offset=per_page * (pagination.page - 1)
        )


@router.post("", summary="Добавление отеля")
async def create_hotel(hotel_data: HotelAdd = Body(openapi_examples={
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
        hotel = await HotelsRepository(session).add(hotel_data)
        await session.commit()

    return {"status": "OK", "data": hotel}


@router.put("/{hotel_id}", summary="Изменение отеля")
async def put_hotel(hotel_id: int, hotel_data: HotelAdd):
    async with async_session_maker() as session:
        edit_hotel = await HotelsRepository(session).edit(hotel_data, id=hotel_id)
        await session.commit()
    return {"status": "OK", "data": edit_hotel}


@router.patch("/{hotel_id}", summary="Частичное изменение отеля")
async def patch_hotel(hotel_id: int, hotel_data: HotelPATCH):
    async with async_session_maker() as session:
        patch_hotel = await HotelsRepository(session).edit(hotel_data, exclude_unset=True, id=hotel_id)
        await session.commit()   

    return {"status": "OK", "data": patch_hotel}


@router.delete("/{hotel_id}", summary="Удаление отеля")
async def delete_hotel(hotel_id: int):
    async with async_session_maker() as session:
        delete_hotel = await HotelsRepository(session).delete(id=hotel_id)
        await session.commit()
    return {"status": "OK!", "data": delete_hotel}
