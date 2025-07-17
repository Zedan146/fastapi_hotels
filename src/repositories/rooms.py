from datetime import date

from sqlalchemy import select, func

from src.database import engine
from src.models.bookings import BookingsModel
from src.repositories.base import BaseRepository
from src.models.rooms import RoomsModel
from src.schemas.rooms import Room


class RoomsRepository(BaseRepository):
    model = RoomsModel
    schema = Room

    async def get_filtered_by_time(self, hotel_id, date_from: date, date_to: date):
        """
        with rooms_count as (
            select room_id, count(*) as rooms_booked from bookings
            where date_from <= '2025-10-07' and date_to >= '2025-08-01'
            group by room_id
        ),

        rooms_left_table as (
            select rooms.id as room_id, quantity - coalesce(rooms_booked, 0) as rooms_left
            from rooms
            left join rooms_count on rooms.id = rooms_count.room_id
        )

        select * from rooms_left_table
        where rooms_left > 0
        """
        rooms_count = (
            select(BookingsModel.room_id, func.count("*").label('rooms_booked'))
            .select_from(BookingsModel)
            .filter(
                BookingsModel.date_from <= date_to,
                BookingsModel.date_to >= date_from
            )
            .group_by(BookingsModel.room_id)
            .cte(name='rooms_count')
        )

        rooms_left_table = (
            select(
                RoomsModel.id.label("room_id"),
                (RoomsModel.quantity - func.coalesce(rooms_count.c.rooms_booked, 0)).label("rooms_left")
            )
            .select_from(RoomsModel)
            .outerjoin(rooms_count, RoomsModel.id == rooms_count.c.room_id)
            .cte(name="rooms_left_table")
        )

        query = (
            select(rooms_left_table)
            .select_from(rooms_left_table)
            .filter(rooms_left_table.c.rooms_left > 0)
        )
