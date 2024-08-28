from pydantic import BaseModel, ConfigDict

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

class RoomList(BaseModel):
  model_config = ConfigDict(from_attributes=True)
  rooms: list[Room]
  page: int
  page_count: int
  size_per_page: int
