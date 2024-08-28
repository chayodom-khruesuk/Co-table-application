from pydantic import BaseModel, ConfigDict

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

class TableList(BaseModel):
  model_config = ConfigDict(from_attributes=True)
  tables: list[Table]
  page: int
  page_count: int
  size_per_page: int
