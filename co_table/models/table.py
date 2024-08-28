from pydantic import BaseModel, ConfigDict

from sqlmodel import Field, Relationship, SQLModel

from .room import DBRoom
from .user import DBUser

class BaseTable(BaseModel):
  model_config = ConfigDict(from_attributes=True)
  name: str

class CreateTable(BaseTable):
  pass

class UpdateTable(BaseTable):
  pass

class Table(BaseTable):
  id: int
  number: int

class DBTable(Table, SQLModel, table = True):
  __tablename__ = "tables"
  id: int = Field(default=None, primary_key=True)
  room_id: int = Field(default=None, foreign_key="rooms.id")
  room: DBRoom = Relationship(back_populates="tables")
  user_id: DBUser | None = Relationship() 

  
class TableList(BaseModel):
  model_config = ConfigDict(from_attributes=True)
  tables: list[Table]
  page: int
  page_count: int
  size_per_page: int
