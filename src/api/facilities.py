from fastapi import APIRouter, Body

from fastapi_cache.decorator import cache

from src.api.dependencies import DBDep
from src.schemas.facilities import FacilityAdd

router = APIRouter(prefix="/facilities", tags=["Удобства"])


@router.get("", summary="Получить список всех удобств")
# @cache(expire=15)
async def get_facilities(db: DBDep):
    return await db.facilities.get_all()


@router.post("", summary="Добавление нового удобства")
async def create_facility(
        db: DBDep,
        facility_data: FacilityAdd = Body(),
):
    facility = await db.facilities.add(facility_data)
    await db.session_commit()

    return {"status": "OK", "data": facility}
