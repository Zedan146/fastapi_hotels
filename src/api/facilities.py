from fastapi import APIRouter, Body

from src.api.dependencies import DBDep
from src.schemas.facilities import FacilitiesAdd

router = APIRouter(prefix="", tags=["Удобства"])


@router.get("/facilities", summary="Получить список всех удобств")
async def get_facilities(db: DBDep):
    return await db.facilities.get_all()


@router.post("/facilities", summary="Добавление нового удобства")
async def create_facility(
        db: DBDep,
        facilities_data: FacilitiesAdd = Body(),
):
    facility = await db.facilities.add(facilities_data)
    await db.session_commit()

    return {"status": "OK", "data": facility}
