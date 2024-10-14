from pydantic import BaseModel, ConfigDict

class BaseRoom(BaseModel):
  model_config = ConfigDict(from_attributes=True)
  name: str
  user_id: int
  status: bool
  faculty: str

class CreateRoom(BaseModel):
    name: str
    faculty: str
    user_id: int

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
