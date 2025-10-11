from fastapi import APIRouter, Body

from fastapi_cache.decorator import cache

from src.api.dependencies import DBDep
from src.exceptions import ObjectAlreadyExistsHTTPException, ObjectAlreadyExistsException
from src.schemas.facilities import FacilityAdd
from src.services.facilities import FacilityService

router = APIRouter(prefix="/facilities", tags=["Удобства"])


@router.get("", summary="Получить список всех удобств")
@cache(expire=15)
async def get_facilities(db: DBDep):
    return await FacilityService(db).get_facilities()


@router.post("", summary="Добавление нового удобства")
async def create_facility(
    db: DBDep,
    facility_data: FacilityAdd = Body(),
):
    try:
        facility = await FacilityService(db).create_facility(facility_data)
    except ObjectAlreadyExistsException:
        raise ObjectAlreadyExistsHTTPException
    return {"status": "OK", "data": facility}
