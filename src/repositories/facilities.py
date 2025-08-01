from pydantic import BaseModel
from sqlalchemy import select, delete, insert

from src.models.facilities import FacilitiesModel, RoomFacilitiesModel
from src.repositories.base import BaseRepository
from src.schemas.facilities import Facility, RoomFacility


class FacilitiesRepository(BaseRepository):
    model = FacilitiesModel
    schema = Facility


class RoomFacilitiesRepository(BaseRepository):
    model = RoomFacilitiesModel
    schema = RoomFacility

    async def edit_room_with_facilities(
            self,
            data: BaseModel,
            room_id: int,
            **filter_by
    ) -> None:
        current_facilities = await self.session.execute(
            select(self.model.facility_id)
            .select_from(self.model)
            .where(self.model.room_id == room_id)
        )
        current_facilities_ids = {row.facility_id for row in current_facilities}
        new_facilities_ids = data.facilities_ids

        if data.facilities_ids is None:
            ids_to_insert = ids_to_delete = set()
        else:
            ids_to_delete = set(current_facilities_ids) - set(new_facilities_ids)
            ids_to_insert = set(new_facilities_ids) - set(current_facilities_ids)

        if ids_to_delete:
            delete_stmt = (
                delete(self.model)
                .where(
                    (self.model.room_id == room_id) & (self.model.facility_id.in_(ids_to_delete))
                )
            )
            await self.session.execute(delete_stmt)

        if ids_to_insert:
            insert_stmt = (
                insert(self.model)
                .values(
                    [{"room_id": room_id, "facility_id": fid} for fid in ids_to_insert]
                )
            )
            await self.session.execute(insert_stmt)
