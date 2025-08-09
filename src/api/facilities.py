import json

from fastapi import APIRouter, Body

from src.api.dependencies import DBDep
from src.init import redis_manager
from src.schemas.facilities import FacilityAdd

router = APIRouter(prefix="/facilities", tags=["Удобства"])


@router.get("", summary="Получить список всех удобств")
async def get_facilities(db: DBDep):
    facilities_from_cache = await redis_manager.get("facilities")
    print(f"{facilities_from_cache}")
    if not facilities_from_cache:
        facilities = await db.facilities.get_all()
        facilities_schemas: list[dict] = [f.model_dump() for f in facilities]
        facilities_json: str = json.dumps(facilities_schemas)
        await redis_manager.set("facilities", facilities_json)
        return facilities
    else:
        facilities_dict = json.loads(facilities_from_cache)
        return facilities_dict


@router.post("", summary="Добавление нового удобства")
async def create_facility(
        db: DBDep,
        facility_data: FacilityAdd = Body(),
):
    facility = await db.facilities.add(facility_data)
    await db.session_commit()

    return {"status": "OK", "data": facility}
