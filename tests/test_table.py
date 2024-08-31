import asyncio
import pytest

from httpx import AsyncClient

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from co_table.models import Token
from co_table.models.dbmodel import DBTable

@pytest.mark.asyncio
async def test_create_table(
    client: AsyncClient,
    token_user2: Token,
    session: AsyncSession,
):
    try:
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
    finally:
        await session.close()


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
async def test_get_nonexistent_table(
    client: AsyncClient,
    session: AsyncSession,
):
    response = await client.get("/tables/9999")
    assert response.status_code == 404

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