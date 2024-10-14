import datetime
from httpx import AsyncClient

import pytest

from sqlmodel.ext.asyncio.session import AsyncSession

from co_table import models
from co_table.models import Token

# @pytest.mark.asyncio
# async def test_reservations_admin(
#     client: AsyncClient,
#     session: AsyncSession,
#     token_user2: Token,
# ):
#     admin_user = models.DBUser(
#         name="reservationsAdmin",
#         username="reservationsAdmin",
#         password="reservationsAdmin",
#         email="reservationsAdmin@example.com",
#     )
#     room = models.DBRoom(name="Admin Room")
#     table = models.DBTable(number=1, room=room)
#     session.add_all([admin_user, room, table])
#     await session.commit()
#     await session.refresh(table)

#     reservation_data = {
#         "table_id": table.id,
#         "duration_hours": 2,
#         "notes": "Admin test reservation",
#         "user_id": admin_user.id
#     }

#     response = await client.post(
#         "/reservations/",
#         json=reservation_data,
#         headers={"Authorization": f"Bearer {token_user2.access_token}"}
#     )
#     if response.status_code != 200:
#         print(f"Error response: {response.text}")
#     assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"

# @pytest.mark.asyncio
# async def test_reservations_user(
#     client: AsyncClient,
#     session: AsyncSession,
#     token_user2: Token,
# ):
#     user_user = models.DBUser(
#         name="reservationsUser",
#         username="reservationsUser",
#         password="reservationsUser",
#         email="reservationsUser@example.com",
#     )
#     room = models.DBRoom(name="user Room")
#     table = models.DBTable(number=1, room=room)
#     session.add_all([user_user, room, table])
#     await session.commit()
#     await session.refresh(table)

#     reservation_data = {
#         "table_id": table.id,
#         "duration_hours": 2,
#         "notes": "user test reservation",
#         "user_id": user_user.id
#     }

#     response = await client.post(
#         "/reservations/",
#         json=reservation_data,
#         headers={"Authorization": f"Bearer {token_user2.access_token}"}
#     )
#     if response.status_code != 200:
#         print(f"Error response: {response.text}")
#     assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"


# @pytest.mark.asyncio
# async def test_get_reservations(
#     client: AsyncClient,
#     session: AsyncSession,
# ):
#     async with session:
#         response = await client.get("/tables/")
#         assert response.status_code == 200
#         data = response.json()
#         assert "tables" in data
#         assert "page" in data
#         assert "page_count" in data
#         assert "size_per_page" in data
    
# @pytest.mark.asyncio
# async def test_get_reservation_by_id(
#     client: AsyncClient,
#     session: AsyncSession,
#     token_user2: Token,
# ):
#     room = models.DBRoom(name="Test Room")
#     session.add(room)
#     await session.flush()
    
#     table = models.DBTable(number=1, room_id=room.id)
#     session.add(table)
#     await session.flush()

#     reservation = models.DBReservation(
#         table_id=table.id,
#         user_id=token_user2.user_id,
#         duration_hours=2,
#     )
#     session.add(reservation)
#     await session.commit()
#     await session.refresh(reservation)

#     response = await client.get(
#         f"/reservations/{reservation.id}",
#         headers={"Authorization": f"Bearer {token_user2.access_token}"}
#     )
    
#     assert response.status_code == 200
#     reservation_data = response.json()
#     assert reservation_data["id"] == reservation.id
#     assert reservation_data["table_id"] == table.id
#     assert reservation_data["user_id"] == token_user2.user_id
#     assert reservation_data["duration_hours"] == 2


# @pytest.mark.asyncio
# async def test_get_nonexistent_reservation(client: AsyncClient):
#     reservation_id = 999  

#     response = await client.get(f"/reservations/{reservation_id}")
#     assert response.status_code == 404

#     response_data = response.json()
#     assert "detail" in response_data
#     assert response_data["detail"] == "Reservation not found"

# @pytest.mark.asyncio
# async def test_update_reservation_authorized_admin(
#     client: AsyncClient,
#     session: AsyncSession,
#     token_user2: Token,
# ):
#     admin_user = models.DBUser(
#         name="UpdateReservationAdmin",
#         username="UpdateReservationAdmin",
#         password="UpdateReservationAdmin",
#         email="UpdateReservationAdmin@example.com")
#     session.add(admin_user)
#     await session.flush()

#     room = models.DBRoom(name="Test Room")
#     session.add(room)
#     await session.flush()
    
#     table = models.DBTable(number=1, room_id=room.id)
#     session.add(table)
#     await session.flush()

#     reservation = models.DBReservation(
#         table_id=table.id,
#         user_id=token_user2.user_id,
#         duration_hours=2,
#     )
#     session.add(reservation)
#     await session.commit()
#     await session.refresh(reservation)

#     update_data = {"duration_hours": 3,"user_id": token_user2.user_id,"table_id": table.id}

#     response = await client.put(
#         f"/reservations/{reservation.id}",
#         json=update_data,
#         headers={"Authorization": f"Bearer {token_user2.access_token}"}
#     )

#     assert response.status_code == 200
#     updated_reservation = response.json()
#     assert updated_reservation["duration_hours"] == 3
#     assert updated_reservation["user_id"] == token_user2.user_id
#     assert updated_reservation["table_id"] == table.id

# @pytest.mark.asyncio
# async def test_update_reservation_authorized_user(
#     client: AsyncClient,
#     session: AsyncSession,
#     token_user1: Token,
#     token_user2: Token,
# ):
#     room = models.DBRoom(name="Test Room")
#     session.add(room)
#     await session.flush()
    
#     table = models.DBTable(number=1, room_id=room.id)
#     session.add(table)
#     await session.flush()

#     reservation = models.DBReservation(
#         table_id=table.id,
#         user_id=token_user2.user_id,
#         duration_hours=2,
#         start_time=datetime.datetime.now()
#     )
#     session.add(reservation)
#     await session.commit()
#     await session.refresh(reservation)

#     update_data = {"duration_hours": 3,"user_id": token_user2.user_id,"table_id": table.id }

#     response = await client.put(
#         f"/reservations/{reservation.id}",
#         json=update_data,
#         headers={"Authorization": f"Bearer {token_user1.access_token}"}
#     )

#     assert response.status_code == 403
#     assert response.json()["detail"] == "You are not allowed to update this reservation"

# @pytest.mark.asyncio
# async def test_update_reservation_unauthorized(
#     client: AsyncClient,
#     session: AsyncSession,
# ):
#     room = models.DBRoom(name="Test Room")
#     session.add(room)
#     await session.flush()
    
#     table = models.DBTable(number=1, room_id=room.id)
#     session.add(table)
#     await session.flush()

#     user = models.DBUser(
#         name="TestUpdateUnauthorized", 
#         username="TestUpdateUnauthorized",
#         password="TestUpdateUnauthorized",
#         email="TestUpdateUnauthorized@example.com")
#     session.add(user)
#     await session.flush()

#     reservation = models.DBReservation(
#         table_id=table.id,
#         user_id=user.id,
#         duration_hours=2,
#         start_time=datetime.datetime.now()
#     )
#     session.add(reservation)
#     await session.commit()
#     await session.refresh(reservation)

#     update_data = {
#         "duration_hours": 3,
#         "user_id": user.id,
#         "table_id": table.id
#     }

#     response = await client.put(
#         f"/reservations/{reservation.id}",
#         json=update_data
#     )

#     assert response.status_code == 401
#     assert response.json()["detail"] == "Not authenticated"

# @pytest.mark.asyncio
# async def test_delete_reservation_authorized_admin(
#     client: AsyncClient,
#     token_user2: Token,
#     session: AsyncSession
# ):
#     user = models.DBUser(
#         name="TestDeleteReservationAdmin", 
#         username="TestDeleteReservationAdmin", 
#         password="TestDeleteReservationAdmin", 
#         email="TestDeleteReservationAdmin@example.com")
#     room = models.DBRoom(name="Test Room")
#     table = models.DBTable(number=1, room=room)
#     session.add_all([user, room, table])
#     await session.commit()

#     reservation = models.DBReservation(
#         user_id=user.id,
#         table_id=table.id,
#         start_time=datetime.datetime.now(),
#         duration_hours=2
#     )
#     session.add(reservation)
#     await session.commit()

#     response = await client.delete(
#         f"/reservations/{reservation.id}",
#         headers={"Authorization": f"Bearer {token_user2.access_token}"}
#     )

#     assert response.status_code == 200
#     assert response.json() == {"message": "Reservation deleted"}

# @pytest.mark.asyncio
# async def test_delete_reservation_authorized_user(
#     client: AsyncClient,
#     token_user1: Token,
#     session: AsyncSession
# ):
#     user = await session.get(models.DBUser, token_user1.user_id)
#     room = models.DBRoom(name="Test Room")
#     table = models.DBTable(number=1, room=room)
#     session.add_all([user, room, table])
#     await session.commit()

#     reservation = models.DBReservation(
#         user_id=user.id,
#         table_id=table.id,
#         start_time=datetime.datetime.now(),
#         duration_hours=2
#     )
#     session.add(reservation)
#     await session.commit()

#     response = await client.delete(
#         f"/reservations/{reservation.id}",
#         headers={"Authorization": f"Bearer {token_user1.access_token}"}
#     )

#     assert response.status_code == 200
#     assert response.json() == {"message": "Reservation deleted"}

# @pytest.mark.asyncio
# async def test_delete_reservation_unauthorized(client: AsyncClient,):
#     response = await client.delete("/reservations/1")
#     assert response.status_code == 401  
#     assert "detail" in response.json()
#     assert response.json()["detail"] == "Not authenticated"