import asyncio
import pytest

from httpx import AsyncClient

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from sqlalchemy.exc import IntegrityError

from co_table import models
from co_table.models import Token
from co_table.models.dbmodel import DBRoom, DBTable

@pytest.mark.asyncio
async def test_create_table_authorized_admin(
    client: AsyncClient,
    token_user2: Token,
    session: AsyncSession,
):
    room_payload = {"name": "Test Room"}
    room_response = await client.post("/rooms/", json=room_payload, headers={"Authorization": f"Bearer {token_user2.access_token}"})
    assert room_response.status_code == 200
    room_data = room_response.json()

    header = {"Authorization": f"Bearer {token_user2.access_token}"}
    payload = {
        "number": 1,
        "room_id": room_data["id"],
    }
    response = await client.post("/tables/", json=payload, headers=header)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["number"] == payload["number"]
    assert data["room_id"] == payload["room_id"]

    result = await session.execute(select(DBTable).where(DBTable.id == data["id"]))
    db_table = result.scalar_one_or_none()
    assert db_table is not None
    assert db_table.number == payload["number"]
    assert db_table.room_id == payload["room_id"]

# @pytest.mark.asyncio
# async def test_create_table_authorized_user(
#     client: AsyncClient,
#     token_user1: Token,  
#     session: AsyncSession,
# ):
#     room_payload = {"name": "Test Table by User"}
#     room_response = await client.post("/tables/", json=room_payload, headers={"Authorization": f"Bearer {token_user1.access_token}"})

#     assert room_response.status_code == 403 

#     error_data = room_response.json()
#     assert "detail" in error_data
#     assert "Not enough permissions" in error_data["detail"]

@pytest.mark.asyncio
async def test_create_table_unauthorized(
    client: AsyncClient,
):
    payload = {
        "number": 1,
        "room_id": 1,
    }
    response = await client.post("/tables/", json=payload)
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_tables(
    client: AsyncClient,
    session: AsyncSession,
    event_loop: asyncio.AbstractEventLoop,
):  
    async with session:
        response = await client.get("/tables/")
        assert response.status_code == 200
        data = response.json()
        assert "tables" in data
        assert "page" in data
        assert "page_count" in data
        assert "size_per_page" in data
    
    await event_loop.run_in_executor(None, asyncio.sleep, 0.1)

    try:
        unique_room_id = 2  
        test_room = DBRoom(id=unique_room_id, name="Room name")
        session.add(test_room)
        await session.commit()

        test_table = DBTable(number=1, room_id=unique_room_id)
        session.add(test_table)
        await session.commit()
        await session.refresh(test_table)

        table_id = test_table.id

        response = await client.get(f"/tables/{table_id}")
        assert response.status_code == 200

        response_data = response.json()
        assert "id" in response_data
        assert response_data["id"] == table_id
        assert "number" in response_data
        assert "room_id" in response_data

    except IntegrityError as e:
        await session.rollback()
        raise e
    finally:
        await session.rollback()  
        await session.close()

@pytest.mark.asyncio
async def test_get_nonexistent_table(
    client: AsyncClient,
    session: AsyncSession,
):
    nonexistent_table_id = 9999

    response = await client.get(f"/tables/{nonexistent_table_id}")
    assert response.status_code == 404

    response_data = response.json()
    assert "detail" in response_data
    assert response_data["detail"] == "Table not found"

@pytest.mark.asyncio
async def test_delete_table_admin(
    client: AsyncClient,
    session: AsyncSession,
    token_user2: Token,
):
    try:
        room = DBRoom(name="Conference Room")
        session.add(room)
        await session.commit()
        await session.refresh(room)

        table = DBTable(number=1, name="Test Table", room_id=room.id)
        session.add(table)
        await session.commit()
        await session.refresh(table)

        assert table is not None

        header = {"Authorization": f"Bearer {token_user2.access_token}"}
        response = await client.delete(f"/tables/{table.id}", headers=header)
        
        assert response.status_code == 200
        assert response.json() == {"message": "Table deleted"}

        result = await session.execute(select(DBTable).where(DBTable.id == table.id))
        db_table = result.scalar_one_or_none()
        assert db_table is None

    finally:
        await session.rollback()
        await session.close()

@pytest.mark.asyncio
async def test_delete_table_unauthorized(
    client: AsyncClient,
):
    table_id = 1

    response = await client.delete(f"/tables/{table_id}")
    assert response.status_code == 401
    response_data = response.json()
    assert "detail" in response_data
    assert response_data["detail"] == "Not authenticated"
    
@pytest.mark.asyncio
async def test_delete_nonexistent_table(
    session: AsyncSession,
    client: AsyncClient,
    token_user2: Token,
):
    header = {"Authorization": f"Bearer {token_user2.access_token}"}
    
    response = await client.delete("/tables/9999", headers=header)
    
    assert response.status_code == 404
    
    response_data = response.json()
    assert "detail" in response_data
    assert response_data["detail"] == "Table not found"

    async with session:
        result = await session.execute(select(DBTable).where(DBTable.id == 9999))
        assert result.scalar_one_or_none() is None