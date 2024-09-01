from httpx import AsyncClient

import pytest

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from co_table.models import Token
from co_table.models.dbmodel import DBRoom

@pytest.mark.asyncio
async def test_create_room_admin(
    client: AsyncClient,
    token_user2: Token,
    session: AsyncSession,
):
    room_payload = {"name": "Test Room"}
    room_response = await client.post("/rooms/", json=room_payload, headers={"Authorization": f"Bearer {token_user2.access_token}"})
    assert room_response.status_code == 200
        
    room_data = room_response.json()
    assert "id" in room_data
    assert room_data["name"] == room_payload["name"]

    result = await session.execute(select(DBRoom).where(DBRoom.id == room_data["id"]))
    db_room = result.scalar_one_or_none()
   
@pytest.mark.asyncio
async def test_create_room_user(
    client: AsyncClient,
    token_user1: Token,  
    session: AsyncSession,
):
    room_payload = {"name": "Test Room by User"}
    room_response = await client.post("/rooms/", json=room_payload, headers={"Authorization": f"Bearer {token_user1.access_token}"})

    assert room_response.status_code == 403 

    error_data = room_response.json()
    assert "detail" in error_data
    assert "Not enough permissions" in error_data["detail"]

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
async def test_get_room_id(client: AsyncClient, session: AsyncSession):
    new_room = DBRoom(name="Test Room")
    session.add(new_room)
    await session.commit()
    await session.refresh(new_room)

    response = await client.get(f"/rooms/{new_room.id}")
    assert response.status_code == 200

    data = response.json()
    assert "id" in data
    assert "name" in data
    assert data["id"] == new_room.id
    assert data["name"] == new_room.name

    await session.delete(new_room)
    await session.commit()

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
async def test_update_room_authorized_admin(
    client: AsyncClient,
    token_user2: Token,
    session: AsyncSession,
):
    room_payload = {"name": "Original Room Name"}
    create_response = await client.post(
        "/rooms/",
        json=room_payload,
        headers={"Authorization": f"Bearer {token_user2.access_token}"}
    )
    assert create_response.status_code == 200
    created_room = create_response.json()
    print("Created room data:", created_room)
    room_id = created_room.get("id")

    if room_id is None:
        raise AssertionError("Room ID was not returned in the creation response.")

    update_payload = {"name": "Updated Room Name"}
    update_response = await client.put(
        f"/rooms/{room_id}",
        json=update_payload,
        headers={"Authorization": f"Bearer {token_user2.access_token}"}
    )
    
    assert update_response.status_code == 200
    updated_room = update_response.json()
    assert updated_room["id"] == room_id
    assert updated_room["name"] == update_payload["name"]

@pytest.mark.asyncio
async def test_update_room_authorized_user(
    client: AsyncClient,
    token_user1: Token,
    token_user2: Token,
    session: AsyncSession,
):
    room_payload = {"name": "Original Room Name"}
    create_response = await client.post(
        "/rooms/",
        json=room_payload,
        headers={"Authorization": f"Bearer {token_user2.access_token}"}
    )
    assert create_response.status_code == 200
    created_room = create_response.json()
    room_id = created_room["id"]

    update_payload = {"name": "Updated Room Name"}
    update_response = await client.put(
        f"/rooms/{room_id}",
        json=update_payload,
        headers={"Authorization": f"Bearer {token_user1.access_token}"}
    )
    
    assert update_response.status_code == 403
    assert update_response.json()["detail"] == "Not enough permissions"

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
async def test_delete_authorized_admin(
    client: AsyncClient,
    token_user2: Token,
    session: AsyncSession,
):
    room_payload = {"name": "Room to be deleted"}
    create_response = await client.post(
        "/rooms/",
        json=room_payload,
        headers={"Authorization": f"Bearer {token_user2.access_token}"}
    )
    assert create_response.status_code == 200
    created_room = create_response.json()
    room_id = created_room.get("id")

    if room_id is None:
        raise AssertionError("Room ID was not returned in the creation response.")

    delete_response = await client.delete(
        f"/rooms/{room_id}",
        headers={"Authorization": f"Bearer {token_user2.access_token}"}
    )
    assert delete_response.status_code == 200
    assert delete_response.json() == {"message": "Room deleted"}

@pytest.mark.asyncio
async def test_delete_unauthorized_user(
    client: AsyncClient,
    token_user1: Token,
    token_user2: Token,
    session: AsyncSession,
):
    room_payload = {"name": "Room that shouldn't be deleted"}
    create_response = await client.post(
        "/rooms/",
        json=room_payload,
        headers={"Authorization": f"Bearer {token_user2.access_token}"}
    )
    assert create_response.status_code == 200
    created_room = create_response.json()
    room_id = created_room["id"]

    delete_response = await client.delete(
        f"/rooms/{room_id}",
        headers={"Authorization": f"Bearer {token_user1.access_token}"}
    )
    assert delete_response.status_code == 403

    response_data = delete_response.json()
    assert "detail" in response_data
    assert response_data["detail"] == "Not enough permissions"

@pytest.mark.asyncio
async def test_no_permission_delete_room(
    client: AsyncClient,
    ):
  response = await client.delete("/rooms/{room.id}")
  assert response.status_code == 401
  assert response.json() == {"detail": "Not authenticated"}

