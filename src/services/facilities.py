from src.exceptions import ObjectAlreadyExistsException
from src.schemas.facilities import FacilityAdd
from src.services.base import BaseService
from src.tasks.tasks import test_task


class FacilityService(BaseService):
    async def get_facilities(self):
        return await self.db.facilities.get_all()

    async def create_facility(self, data: FacilityAdd):
        facilities = await self.get_facilities()
        if data.title in [entity.title for entity in facilities]:
            raise ObjectAlreadyExistsException
        facility = await self.db.facilities.add(data)
        await self.db.session_commit()

        test_task.delay()   # type: ignore
        return facility

    async def get_missing_facility_with_check(self, facilities_ids: list[int]) -> list[int]:
        if facilities_ids:
            unique_ids = list(set(facilities_ids))

            facilities = await self.db.facilities.get_by_ids(facilities_ids)

            found_ids = {facility.id for facility in facilities}
            missing_ids = set(unique_ids) - found_ids

            if missing_ids:
                return list(missing_ids)
