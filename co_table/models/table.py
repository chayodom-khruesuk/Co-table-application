from pydantic import BaseModel, ConfigDict


class BaseTable(BaseModel):
  model_config = ConfigDict(from_attributes=True)
  number: int
  room_id: int
  is_available: bool

class CreateTable(BaseTable):
  pass

class UpdateTable(BaseTable):
  pass

class Table(BaseTable):
  id: int

class TableList(BaseModel):
  model_config = ConfigDict(from_attributes=True)
  tables: list[Table]
  page: int
  page_count: int
  size_per_page: int
