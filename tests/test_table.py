from httpx import AsyncClient
import pytest

@pytest.mark.asyncio
async def test_create_table(client: AsyncClient):
    room_data = {"name": "Test Room"}
    response = await client.post("/rooms/", json=room_data)
    assert response.status_code == 401
    
    room_id = 1
    number = 1

    table_data = {"number": number, "room_id": room_id}
    response = await client.post("/tables/", json=table_data)
    assert response.status_code == 401

    error_response = response.json()
    assert 'detail' in error_response
    assert error_response['detail'] == 'Not authenticated'