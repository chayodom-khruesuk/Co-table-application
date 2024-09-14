from typing import Optional
from . import BaseRoom, BaseTable, BaseReservation
from sqlmodel import Field, SQLModel, Relationship
from . import DBUser

import datetime
import pydantic

class DBRoom(BaseRoom, SQLModel, table = True):
  __tablename__ = "rooms"
  id: Optional[int] = Field(default=None, primary_key=True)
  tables: list["DBTable"] = Relationship(back_populates="room", cascade_delete=True)
  user_id: int = Field(default=None, foreign_key="users.id")
  user: DBUser | None = Relationship()

class DBTable(BaseTable, SQLModel, table = True):
  __tablename__ = "tables"
  id: Optional[int] = Field(default=None, primary_key=True)
  room_id: int = Field(default=None, foreign_key="rooms.id")
  room: DBRoom = Relationship(back_populates="tables")
  reservations: list["DBReservation"] = Relationship(back_populates="table", cascade_delete=True)

class DBReservation(BaseReservation, SQLModel, table = True):
  __tablename__ = "reservations"
  id: Optional[int] = Field(default=None, primary_key=True)
  reserved_at: datetime.datetime | None = pydantic.Field(
        json_schema_extra=dict(example="2023-01-01T00:00:00.000000"), default=None
    )
  start_time: datetime.datetime | None = pydantic.Field(
        json_schema_extra=dict(example="2023-01-01T00:00:00.000000"), default=None
    )
  end_time: datetime.datetime | None = pydantic.Field(
        json_schema_extra=dict(example="2023-01-01T00:00:00.000000"), default=None
    )
  user_id: int = Field(default=None, foreign_key="users.id")
  user: DBUser | None = Relationship()
  table_id: int = Field(default=None, foreign_key="tables.id")
  table: DBTable = Relationship(back_populates="reservations")
