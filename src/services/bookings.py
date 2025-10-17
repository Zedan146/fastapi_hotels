from src.api.dependencies import UserIdDep
from src.schemas.bookings import BookingAddRequest, BookingAdd
from src.services.base import BaseService
from src.services.rooms import RoomService


class BookingService(BaseService):
    async def get_bookings(self):
        return await self.db.bookings.get_all()

    async def get_user_bookings(self, user_id: UserIdDep):
        return await self.db.bookings.get_filtered(user_id=user_id)

    async def create_booking(self, user_id: UserIdDep, booking_data: BookingAddRequest):
        room_data = await RoomService(self.db).get_room_with_check(booking_data.room_id)
        hotel_id = room_data.hotel_id
        _booking_data = BookingAdd(
            user_id=user_id, price=room_data.price, **booking_data.model_dump()
        )
        booking = await self.db.bookings.add_booking(
            _booking_data,
            hotel_id,
            _booking_data.room_id,
            _booking_data.date_from,
            _booking_data.date_to,
        )

        await self.db.session_commit()
        return booking
