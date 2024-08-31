from httpx import AsyncClient

import pytest

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from co_table.models import Token
from co_table.models.dbmodel import DBRoom

@pytest.mark.asyncio
async def test_create_room(
    client: AsyncClient,
    token_user2: Token,
    session: AsyncSession,
):
    try:
        room_payload = {"name": "Test Room"}
        room_response = await client.post("/rooms/", json=room_payload, headers={"Authorization": f"Bearer {token_user2.access_token}"})
        assert room_response.status_code == 200
        
        room_data = room_response.json()
        assert "id" in room_data
        assert room_data["name"] == room_payload["name"]

        result = await session.execute(select(DBRoom).where(DBRoom.id == room_data["id"]))
        db_room = result.scalar_one_or_none()

        assert db_room is not None
        assert db_room.name == room_payload["name"]
    finally:
        await session.close()

@pytest.mark.asyncio
async def test_get_rooms(
    client: AsyncClient,
):
    response = await client.get("/rooms/")
    assert response.status_code == 200

    data = response.json()
    assert "rooms" in data
    assert "page" in data
    assert "page_count" in data
    assert "size_per_page" in data
    assert isinstance(data["rooms"], list)
    assert isinstance(data["page"], int)
    assert isinstance(data["page_count"], int)
    assert isinstance(data["size_per_page"], int)

@pytest.mark.asyncio
async def test_get_room_id(
   client: AsyncClient,
): 
   room_id = 1
   response = await client.get(f"/rooms/{room_id}")
   assert response.status_code == 200

   data = response.json()
   assert "id" in data
   assert "name" in data

@pytest.mark.asyncio
async def test_get_room_not_found(
    client: AsyncClient,
):
    room_id = 9999
    response = await client.get(f"/rooms/{room_id}")
    assert response.status_code == 404

    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Room not found"


@pytest.mark.asyncio
async def test_no_permission_update_room(
    client: AsyncClient,  
):
    room_id = 1
    update_payload = {
        "name": "Updated room name",
    }
    response = await client.put(f"/rooms/{room_id}", json=update_payload)
    
    assert response.status_code == 401
    
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Not authenticated"  


@pytest.mark.asyncio
async def test_no_permission_delete_room(
    client: AsyncClient,
    ):
  response = await client.delete("/rooms/{room.id}")
  assert response.status_code == 401

@pytest.mark.asyncio
async def test_create_room_unauthorized(
    client: AsyncClient,
):
    payload = {
        "name": 1,
        "room_id": 1,
    }
    response = await client.post("/tables/", json=payload)
    assert response.status_code == 401
