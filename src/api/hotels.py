from datetime import date

from fastapi import Query, APIRouter, Body, HTTPException

from fastapi_cache.decorator import cache

from src.api.dependencies import PaginationDep, DBDep
from src.exceptions import (
    ObjectNotFoundException,
    HotelNotFoundHTTPException,
    NoDataHasBeenTransmitted,
    ObjectAlreadyExistsException,
    ValidationException,
    ValidationHTTPException,
)
from src.schemas.hotels import HotelPATCH, HotelAdd
from src.services.hotels import HotelService

router = APIRouter(prefix="/hotels", tags=["Отели"])


@router.get("/{hotel_id}", summary="Получение одного отеля")
@cache(expire=10)
async def get_one_hotel(hotel_id: int, db: DBDep):
    try:
        return await HotelService(db).get_hotel(hotel_id)
    except ObjectNotFoundException:
        raise HotelNotFoundHTTPException


@router.get("", summary="Получение отелей")
@cache(expire=10)
async def get_hotels(
    pagination: PaginationDep,
    db: DBDep,
    title: str | None = Query(None, description="Название отеля"),
    location: str | None = Query(None, description="Адрес отеля"),
    date_from: date = Query(example="2025-08-01"),
    date_to: date = Query(example="2025-08-07"),
):
    return await HotelService(db).get_hotels_by_time(
        pagination,
        title,
        location,
        date_from,
        date_to,
    )


@router.post("", summary="Добавление отеля")
async def create_hotel(
    db: DBDep,
    hotel_data: HotelAdd = Body(
        openapi_examples={
            "1": {
                "summary": "Сочи",
                "value": {
                    "title": "Отель Бирсон",
                    "location": "Сочи, ул. Матросова, 13",
                },
            },
            "2": {
                "summary": "Дубай",
                "value": {"title": "Аль-Халиф", "location": "Дубай, ул. Кан, 3"},
            },
        }
    ),
):
    try:
        hotel = await HotelService(db).add_hotel(hotel_data)
    except ObjectAlreadyExistsException:
        return {"detail": "Такой отель уже существует"}
    except ValidationException:
        raise ValidationHTTPException
    return {"status": "OK", "data": hotel}


@router.put("/{hotel_id}", summary="Изменение отеля")
async def put_hotel(hotel_id: int, hotel_data: HotelAdd, db: DBDep):
    try:
        await HotelService(db).edit_hotel(hotel_id, hotel_data)
    except ObjectNotFoundException:
        raise HotelNotFoundHTTPException

    return {"status": "OK"}


@router.patch("/{hotel_id}", summary="Частичное изменение отеля")
async def patch_hotel(hotel_id: int, hotel_data: HotelPATCH, db: DBDep):
    try:
        await HotelService(db).edit_hotel_partially(hotel_id, hotel_data, exclude_unset=True)
    except ObjectNotFoundException:
        raise HotelNotFoundHTTPException
    except NoDataHasBeenTransmitted:
        raise HTTPException(status_code=400, detail="Данные для изменения не переданы")

    return {"status": "OK"}


@router.delete("/{hotel_id}", summary="Удаление отеля")
async def delete_hotel(hotel_id: int, db: DBDep):
    try:
        await HotelService(db).delete_hotel(hotel_id)
    except ObjectNotFoundException:
        raise HotelNotFoundHTTPException

    return {"status": "OK!"}
