from datetime import date

from src.schemas.bookings import BookingAdd


async def test_booking_crud(db):
    room_id = (await db.rooms.get_all())[0].id
    user_id = (await db.users.get_all())[0].id
    booking_data = BookingAdd(
        room_id=room_id,
        user_id=user_id,
        date_from=date(year=2025, month=8, day=10),
        date_to=date(year=2025, month=8, day=20),
        price=250,
    )
    # Добавление бронирования
    new_booking = await db.bookings.add(booking_data)

    # Получение бронирования
    booking = await db.bookings.get_one_or_none(id=new_booking.id)
    assert booking
    assert booking.id == new_booking.id
    assert booking.room_id == new_booking.room_id
    assert booking.user_id == new_booking.user_id

    # Изменение бронирования
    updated_date = date(year=2025, month=9, day=5)
    edit_booking_data = BookingAdd(
        room_id=room_id,
        user_id=user_id,
        date_from=date(year=2025, month=8, day=10),
        date_to=updated_date,
        price=350,
    )
    updated_booking = await db.bookings.edit(edit_booking_data, room_id=new_booking.id)
    assert updated_booking
    assert updated_booking.id == new_booking.id
    assert updated_booking.date_to == updated_date
    assert updated_booking.price == 350

    # Удаление бронирования
    await db.bookings.delete(id=new_booking.id)
    assert not await db.bookings.get_one_or_none(id=new_booking.id)

    await db.session_commit()
