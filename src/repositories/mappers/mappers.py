from src.models.bookings import BookingsModel
from src.models.facilities import FacilitiesModel
from src.models.hotels import HotelsModel
from src.models.rooms import RoomsModel
from src.models.users import UsersModel
from src.repositories.mappers.base import DataMapper
from src.schemas.bookings import Booking
from src.schemas.facilities import Facility
from src.schemas.hotels import Hotel
from src.schemas.rooms import Room, RoomWithRels
from src.schemas.users import User, UserWithHashedPassword


class HotelDataMapper(DataMapper):
    db_model = HotelsModel
    schema = Hotel


class FacilityDataMapper(DataMapper):
    db_model = FacilitiesModel
    schema = Facility


class RoomDataMapper(DataMapper):
    db_model = RoomsModel
    schema = Room


class RoomWithRelsDataMapper(DataMapper):
    db_model = RoomsModel
    schema = RoomWithRels


class UserDataMapper(DataMapper):
    db_model = UsersModel
    schema = User


class UserWithHashedPasswordDataMapper(DataMapper):
    db_model = UsersModel
    schema = UserWithHashedPassword


class BookingDataMapper(DataMapper):
    db_model = BookingsModel
    schema = Booking
