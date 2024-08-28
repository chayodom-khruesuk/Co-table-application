from pydantic import BaseModel, ConfigDict
from sqlmodel import Field, Relationship
from .table import DBTable

class BaseRoom(BaseModel):
  model_config = ConfigDict(from_attributes=True)
  name: str
  table_count: int

class CreateRoom(BaseRoom):
  pass

class UpdateRoom(BaseRoom):
  pass

class Room(BaseRoom):
  id: int

class DBRoom(BaseRoom):
  __tablename__ = "rooms"
  id: int = Field(default=None, primary_key=True)
  tables: list[DBTable] = Relationship(back_populates="room", cascade_delete=True)
  table_id: int = Field(default=None, foreign_key="tables.id")

class RoomList(BaseModel):
  model_config = ConfigDict(from_attributes=True)
  rooms: list[Room]
  page: int
  page_count: int
  size_per_page: int
