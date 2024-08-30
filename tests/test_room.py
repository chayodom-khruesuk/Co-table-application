from httpx import AsyncClient
from co_table import models
import pytest

@pytest.mark.asyncio
async def test_no_permission_create_room(
  client: AsyncClient,
  ):

  payload = {
    "name": "room1",
  }

  response = await client.post("/rooms/", json=payload)
  assert response.status_code == 401

@pytest.mark.asyncio
async def test_no_permission_update_room(
  client: AsyncClient,
  ):

  payload = {
    "name": "room1 update",
  }

  response = await client.put("/rooms/{room.id}", json=payload)
  assert response.status_code == 401

@pytest.mark.asyncio
async def test_no_permission_delete_room(
    client: AsyncClient,
    ):
  response = await client.delete("/rooms/{room.id}")
  assert response.status_code == 401

@pytest.mark.asyncio
async def test_user_create_room(
  client: AsyncClient,
  token_user1: models.Token,
):
  header = {"Authorization": f"Bearer {token_user1.access_token}"}

  payload = {
    "name": "room1",
  }

  response = await client.post("/rooms/", json=payload, headers=header)
  assert response.status_code == 200