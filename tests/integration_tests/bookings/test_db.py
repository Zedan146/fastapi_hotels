from datetime import date

from src.schemas.bookings import BookingAdd


async def test_booking_crud (db):
    room_id = (await db.rooms.get_all())[0].id
    user_id = (await db.users.get_all())[0].id
    booking_data = BookingAdd(
        room_id=room_id,
        user_id=user_id,
        date_from=date(year=2025, month=8, day=10),
        date_to=date(year=2025, month=8, day=20),
        price=250,
    )
    await db.bookings.add(booking_data)
    await db.bookings.get_all()
    await db.bookings.edit(booking_data, room_id=room_id)
    await db.bookings.delete(room_id=room_id)

    await db.session_commit()
