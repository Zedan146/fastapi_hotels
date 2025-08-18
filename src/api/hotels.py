from datetime import date

from fastapi import Query, APIRouter, Body

from fastapi_cache.decorator import cache

from src.api.dependencies import PaginationDep, DBDep
from src.schemas.hotels import HotelPATCH, HotelAdd

router = APIRouter(prefix="/hotels", tags=["Отели"])


@router.get("/{hotel_id}", summary="Получение одного отеля")
@cache(expire=10)
async def get_one_hotel(hotel_id: int, db: DBDep):
    return await db.hotels.get_one_or_none(id=hotel_id)


@router.get("", summary="Получение отелей")
# @cache(expire=10)
async def get_hotels(
        pagination: PaginationDep,
        db: DBDep,
        title: str | None = Query(None, description='Название отеля'),
        location: str | None = Query(None, description="Адрес отеля"),
        date_from: date = Query(example='2025-08-01'),
        date_to: date = Query(example='2025-08-07'),
):
    per_page = pagination.per_page or 5

    return await db.hotels.get_hotels_by_time(
        title=title,
        location=location,
        date_from=date_from,
        date_to=date_to,
        limit=per_page,
        offset=per_page * (pagination.page - 1)
    )


@router.post("", summary="Добавление отеля")
async def create_hotel(db: DBDep, hotel_data: HotelAdd = Body(openapi_examples={
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
    hotel = await db.hotels.add(hotel_data)
    await db.session_commit()

    return {"status": "OK", "data": hotel}


@router.put("/{hotel_id}", summary="Изменение отеля")
async def put_hotel(hotel_id: int, hotel_data: HotelAdd, db: DBDep):
    edit_data = await db.hotels.edit(hotel_data, id=hotel_id)
    await db.session_commit()
    return {"status": "OK", "data": edit_data}


@router.patch("/{hotel_id}", summary="Частичное изменение отеля")
async def patch_hotel(hotel_id: int, hotel_data: HotelPATCH, db: DBDep):
    edit_data = await db.hotels.edit(hotel_data, exclude_unset=True, id=hotel_id)
    await db.session_commit()

    return {"status": "OK", "data": edit_data}


@router.delete("/{hotel_id}", summary="Удаление отеля")
async def delete_hotel(hotel_id: int, db: DBDep):
    delete_data = await db.hotels.delete(id=hotel_id)
    await db.session_commit()
    return {"status": "OK!", "data": delete_data}
