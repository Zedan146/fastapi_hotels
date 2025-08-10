from fastapi import APIRouter, Body

from fastapi_cache.decorator import cache

from src.api.dependencies import DBDep
from src.schemas.facilities import FacilityAdd
from src.tasks.tasks import test_task

router = APIRouter(prefix="/facilities", tags=["Удобства"])


@router.get("", summary="Получить список всех удобств")
@cache(expire=15)
async def get_facilities(db: DBDep):
    return await db.facilities.get_all()


@router.post("", summary="Добавление нового удобства")
async def create_facility(
        db: DBDep,
        facility_data: FacilityAdd = Body(),
):
    facility = await db.facilities.add(facility_data)
    await db.session_commit()

    # test_task.delay()

    return {"status": "OK", "data": facility}
