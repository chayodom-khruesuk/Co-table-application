
from datetime import timedelta
from httpx import AsyncClient

import pytest

from sqlmodel.ext.asyncio.session import AsyncSession

@pytest.mark.asyncio
async def test_get_reservations(
    client: AsyncClient,
    session: AsyncSession,
):
    async with session:
        response = await client.get("/tables/")
        assert response.status_code == 200
        data = response.json()
        assert "tables" in data
        assert "page" in data
        assert "page_count" in data
        assert "size_per_page" in data
    
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