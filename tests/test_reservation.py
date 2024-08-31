
from httpx import AsyncClient

import pytest

from sqlmodel.ext.asyncio.session import AsyncSession

from co_table import models

# @pytest.mark.asyncio
# async def test_create_reservation_user(
#     client: AsyncClient,
#     token_user1: models.Token,
# ):
#     reservation_payload = {
#         "user_id": token_user1.access_token,
#         "table_id": 1,
#         "start_time": "2022-01-01T00:00:00",
#         "end_time": "2022-01-01T00:00:00",
#     }

#     response = await client.post("/reservations/", json=reservation_payload)
#     assert response.status_code == 200

#     data = response.json()
#     assert "id" in data
#     assert "reserved_at" in data
#     assert "start_time" in data
#     assert "end_time" in data
#     assert data["user_id"] == reservation_payload["user_id"]
#     assert data["table_id"] == reservation_payload["table_id"]
#     assert data["duration_hours"] == reservation_payload["duration_hours"]

# @pytest.mark.asyncio
# async def test_create_reservation_unauthorize(
#     client: AsyncClient,
# ):
#     reservation_payload = {
#         "user_id": 1,
#         "table_id": 1,
#         "duration_hours": 2,
#     }

#     response = await client.post("/reservations/", json=reservation_payload)
#     assert response.status_code == 401

#     data = response.json()
#     assert "detail" in data
#     assert data["detail"] == "Not authenticated"

@pytest.mark.asyncio
async def test_get_nonexistent_reservation(
    client: AsyncClient,
    session: AsyncSession,
):
    reservation_id = 999  

    response = await client.get(f"/reservations/{reservation_id}")
    assert response.status_code == 404

    response_data = response.json()
    assert "detail" in response_data
    assert response_data["detail"] == "Reservation not found"