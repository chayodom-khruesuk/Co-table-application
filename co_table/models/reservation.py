from pydantic import BaseModel, ConfigDict
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
  reserved_at: datetime.datetime | None
  start_time: datetime.datetime | None
  end_time: datetime.datetime | None
  
class ReservationList(BaseModel):
  model_config = ConfigDict(from_attributes=True)
  Reservations: list[Reservation]
  page: int
  page_count: int
  size_per_page: int
