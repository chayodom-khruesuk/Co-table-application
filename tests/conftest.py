import datetime
import pathlib
import sys
import os
import pytest
import asyncio
import pytest_asyncio

from typing import AsyncIterator
from fastapi import FastAPI

from pydantic_settings import SettingsConfigDict
from sqlmodel import select

from sqlalchemy.ext.asyncio import AsyncSession

from co_table import config, main, models, security

from httpx import AsyncClient, ASGITransport

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

SettingsTesting = config.Settings
SettingsTesting.model_config = SettingsConfigDict(
    env_file=".testing.env", validate_assignment=True, extra="allow"
)

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(name="app", scope="session")
def app_fixture():
    settings = SettingsTesting()
    path = pathlib.Path("test-data")
    if not path.exists():
        path.mkdir()
    app = main.create_app(settings)
    asyncio.run(models.recreate_table())
    yield app

@pytest.fixture(name="client", scope="session")
def client_fixture(app: FastAPI) -> AsyncClient:
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost")

@pytest_asyncio.fixture(name="session")
async def get_session() -> AsyncIterator[AsyncSession]:
    settings = SettingsTesting()
    models.init_db(settings)

    async_session = models.sessionmaker(
        models.engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture(name="user1")
async def example_user1(session: AsyncSession) -> models.DBUser:
    username = "usernameUser"
    password = "passwordUser"

    query = await session.execute(
        select(models.DBUser).where(models.DBUser.username == username).limit(1)
    )
    user = query.scalar_one_or_none()
    if user:
        return user

    user = models.DBUser(
        username=username,
        password=password,
        name="User 1",
        email="test1@test.com",
        first_name="Firstname",
        last_name="lastname",
        last_login_date=datetime.datetime.now(),
        roles="user",
        room_permission=False
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@pytest_asyncio.fixture(name="user2")
async def example_user2(session: AsyncSession) -> models.DBUser:
    username = 'usernameAdmin'
    password = 'passwordAdmin'

    result = await session.execute(
        select(models.DBUser).where(models.DBUser.username == username and models.DBUser.password == password).limit(1)
    )
    user = result.scalar_one_or_none()
    if user:
        return user

    user = models.DBUser(
        username=username, 
        password=password,
        name="User 2",
        email="test2@test.com",
        first_name="Firstname",
        last_name="lastname",
        last_login_date=datetime.datetime.now(),
        roles="admin",
        room_permission = True
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

@pytest_asyncio.fixture(name="token_user1")
async def oauth_token_user1(user1: models.DBUser) -> models.Token:
    settings = SettingsTesting()
    access_token_expires = datetime.timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    user = user1

    if not user.name:
        user.name = "User 1" 

    return models.Token(
        access_token=security.create_access_token(
            data={"sub": user.id},
            expires_delta=access_token_expires,
        ),
        refresh_token=security.create_refresh_token(
            data={"sub": user.id},
            expires_delta=access_token_expires,
        ),
        token_type="Bearer",
        scope="",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        expires_at=datetime.datetime.now() + access_token_expires,
        issued_at=user1.last_login_date,
        user_id=user.id,
    )

@pytest_asyncio.fixture(name="token_user2")
async def oauth_token_user2(user2: models.DBUser) -> models.Token:
    settings = SettingsTesting()
    access_token_expires = datetime.timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    user = user2
    
    if not user.name:
        user.name = "User 2" 
    
    return models.Token(
        access_token=security.create_access_token(
            data={"sub": user.id},
            expires_delta=access_token_expires,
        ),
        refresh_token=security.create_refresh_token(
            data={"sub": user.id},
            expires_delta=access_token_expires,
        ),
        token_type="Bearer",
        scope="",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        expires_at=datetime.datetime.now() + access_token_expires,
        issued_at=user2.last_login_date,
        user_id=user.id,
    )

@pytest_asyncio.fixture(name="room")
async def ex_room_user1(session: AsyncSession) -> models.DBRoom:
    async with session.begin():
        room = models.DBRoom(name="room")
        result = await session.execute(select(models.DBRoom).where(models.DBRoom.name == room.name).limit(1))
        existing_room = result.scalar_one_or_none()
        if existing_room:
            return existing_room
        
        session.add(room)
        await session.commit()
        await session.refresh(room)
        return room
    
@pytest_asyncio.fixture(name="table")
async def ex_table_user1(
    session: AsyncSession,
    room1: models.DBRoom
) -> models.DBTable:
    async with session.begin():
        table = models.DBTable(room_id=room1.id)
        result = await session.execute(
            select(models.DBTable)
            .where(models.DBTable.room_id == room1.id)
            .limit(1)
        )
        existing_table = result.scalar_one_or_none()
        if existing_table:
            return existing_table
        
        session.add(table)
        await session.commit()
        await session.refresh(table)
        return table
    
@pytest_asyncio.fixture(name="reservation")
async def example_reservation_user1(
    session: AsyncSession,
    user1: models.DBUser,
    table: models.DBTable,
) -> models.DBReservation:
   
   user = models.DBUser(id = 1, name = "Test User")
   table = models.DBTable(id = 1, name = "Test Table")
   reservation = models.DBReservation(
       id = 1,
       user_id = user.id,
       table_id = table.id,
       reserved_at = datetime.datetime(2023, 1, 1, 0, 0, 0),
       start_time = datetime.datetime(2023, 1, 1, 10, 0, 0),
       end_time = datetime.datetime(2023, 1, 1, 12, 0, 0),
   )

   session.add_all([user, table, reservation])
   await session.commit()
   await session.refresh(reservation)
   return reservation