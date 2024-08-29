from pydantic import BaseModel, ConfigDict
from sqlmodel import Field, Relationship
from .table import DBTable
from .user import DBUser
from .room import DBRoom

import datetime

class BaseReservation(BaseModel):
  model_config = ConfigDict(from_attributes=True)
  user_id: int
  table_id: int
  duration_hours: int

class CreateReservation(BaseReservation):
  pass

class UpdateReservation(BaseReservation):
  pass

class Reservation(BaseReservation):
  id: int

class DBReservation(BaseReservation):
  __tablename__ = "reservations"
  id: int = Field(default=None, primary_key=True)
  reserved_at: datetime
  start_time: datetime
  end_time: datetime
  user_id: DBUser | None = Relationship()
  table_id: DBTable | None = Relationship()
  room_id: DBRoom | None = Relationship()
  

class ReservationList(BaseModel):
  model_config = ConfigDict(from_attributes=True)
  Reservations: list[Reservation]
  page: int
  page_count: int
  size_per_page: int
