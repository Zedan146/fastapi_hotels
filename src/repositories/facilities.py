from sqlalchemy import select, delete, insert

from src.models.facilities import FacilitiesModel, RoomFacilitiesModel
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import FacilityDataMapper
from src.schemas.facilities import Facility, RoomFacility


class FacilitiesRepository(BaseRepository):
    model = FacilitiesModel
    schema = Facility
    mapper = FacilityDataMapper


class RoomFacilitiesRepository(BaseRepository):
    model = RoomFacilitiesModel
    schema = RoomFacility
    mapper = FacilityDataMapper

    async def edit_room_with_facilities(
            self,
            room_id: int,
            facilities_ids: list[int]
    ) -> None:
        get_current_facilities_ids_query = await self.session.execute(
            select(self.model.facility_id)
            .select_from(self.model)
            .filter_by(room_id=room_id)
        )
        current_facilities_ids = get_current_facilities_ids_query.scalars().all()

        ids_to_delete = list(set(current_facilities_ids) - set(facilities_ids))
        ids_to_insert = list(set(facilities_ids) - set(current_facilities_ids))

        if ids_to_delete:
            delete_facilities_stmt = (
                delete(self.model)
                .filter(
                    self.model.room_id == room_id,
                    self.model.facility_id.in_(ids_to_delete)
                )
            )
            await self.session.execute(delete_facilities_stmt)

        if ids_to_insert:
            insert_facilities_stmt = (
                insert(self.model)
                .values(
                    [{"room_id": room_id, "facility_id": fid} for fid in ids_to_insert]
                )
            )
            await self.session.execute(insert_facilities_stmt)
