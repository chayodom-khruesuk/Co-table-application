import datetime
import json
from typing import List, Optional
import bcrypt

from sqlmodel import SQLModel, Field

from pydantic import BaseModel, ConfigDict, EmailStr
import pydantic

class BaseUser(BaseModel):
    model_config = ConfigDict(from_attributes = True, populate_by_name = True)
    email: str = pydantic.Field(json_schema_extra = dict(example = "admin@email.local"))
    username: str = pydantic.Field(json_schema_extra = dict(example = "admin"))
    name: str = pydantic.Field(json_schema_extra = dict(example = "name"))
    faculty: str = pydantic.Field(json_schema_extra = dict(example = "Engineering"))

class User(BaseUser):
    id: int
    last_login_date: datetime.datetime | None = pydantic.Field(
        json_schema_extra = dict(example = "2023-01-01T00:00:00.000000"), default=None
    )
    register_date: datetime.datetime | None = pydantic.Field(
        json_schema_extra = dict(example = "2023-01-01T00:00:00.000000"), default=None
    )

class ReferenceUser(BaseModel):
    model_config = ConfigDict(from_attributes = True, populate_by_name = True)
    username: str = pydantic.Field(example = "admin")
    name: str = pydantic.Field(example = "name")

class UserList(BaseModel):
    model_config = ConfigDict(from_attributes = True, populate_by_name = True)
    users: list[User]

class UpdatedUser(BaseModel):
    email: EmailStr
    name: str = Field(min_length = 1)
    faculty: str

    model_config = ConfigDict(from_attributes = True, populate_by_name = True)

class ChangePasswordUser(BaseModel):
    current_password: str
    new_password: str

class ForgotPassword(BaseModel):
    new_password: str
    
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    scope: str
    expires_in: int
    expires_at: datetime.datetime
    issued_at: datetime.datetime
    user_id: int

class DBUser(SQLModel, table=True):
    __tablename__ = "users"
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    password: str = Field(index=True, unique=True)
    name: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    roles: str = Field(default_factory=str)
    faculty: str = Field(default_factory=str)
    room_permission: bool = pydantic.Field(json_schema_extra = dict(example = False))
    register_date: datetime.datetime = Field(default_factory=datetime.datetime.now)
    updated_date: datetime.datetime = Field(default_factory=datetime.datetime.now)
    last_login_date: Optional[datetime.datetime] = Field(default=None)

    async def has_roles(self, roles: List[str]) -> bool:
        user_roles = self.roles
        return any(role in user_roles for role in roles)

    async def get_encrypted_password(self, password: str) -> str:
        return bcrypt.hashpw(
            password.encode("utf-8"), salt=bcrypt.gensalt()
        ).decode("utf-8")

    async def set_password(self, password: str):
        self.password = await self.get_encrypted_password(password)

    async def verify_password(self, password: str) -> bool:
        return bcrypt.checkpw(
            password.encode("utf-8"), self.password.encode("utf-8")
        )