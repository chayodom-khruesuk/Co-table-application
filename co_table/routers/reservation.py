from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, func
from typing import Annotated
from .. import models
from .. import deps

import math
import datetime

router = APIRouter(
    prefix="/reservations",
    tags=["reservations"],
)

SIZE_PER_PAGE = 50

@router.post("/", response_model=models.Reservation)
async def create_reservation(
    reservation: models.CreateReservation,
    current_user: Annotated[models.User, Depends(deps.get_current_user)],
    session: Annotated[AsyncSession, Depends(models.get_session)],
    ) -> models.Reservation:
  db_reservation = models.DBReservation.model_validate(reservation)
  if db_reservation.table.room.status != True:
    raise HTTPException(status_code=403, detail="This room is closed, please try again later")
  if db_reservation.table.room.faculty != current_user.faculty and db_reservation.table.room.faculty != "ไม่มีคณะ":
    raise HTTPException(status_code=403, detail="You can only reserve tables in your faculty's rooms")
  db_reservation.reserved_at = datetime.datetime.now()
  db_reservation.start_time = datetime.datetime.now()
  db_reservation.end_time = db_reservation.start_time + datetime.timedelta(hours=reservation.duration_hours)
  session.add(db_reservation)
  await session.commit()
  await session.refresh(db_reservation)
  return models.Reservation.model_validate(db_reservation)

@router.get("/", response_model=models.ReservationList)
async def get_reservations(session: Annotated[AsyncSession, Depends(models.get_session)], page: int = 1) -> list[models.ReservationList]:
  result = await session.exec(select(models.DBReservation).offset((page - 1) * SIZE_PER_PAGE).limit(SIZE_PER_PAGE))

  db_reservations = result.all()

  page_count = int(math.ceil((await session.exec(select(func.count(models.DBReservation.id)))).first() / SIZE_PER_PAGE))

  return models.ReservationList.model_validate(dict(reservations=db_reservations, page=page, page_count=page_count, size_per_page=SIZE_PER_PAGE))

@router.get("/{reservation_id}", response_model=models.Reservation)
async def get_reservation(reservation_id: int, session: Annotated[AsyncSession, Depends(models.get_session)]) -> models.Reservation:
  db_reservation = await session.get(models.DBReservation, reservation_id)
  if db_reservation:
    return models.Reservation.model_validate(db_reservation)
  raise HTTPException(status_code=404, detail="Reservation not found")

@router.put("/{reservation_id}", response_model=models.Reservation)
async def update_reservation(
    reservation_id: int,
    reservation: models.UpdateReservation,
    current_user: Annotated[models.User, Depends(deps.get_current_user)],
    session: Annotated[AsyncSession, Depends(models.get_session)]
    ) -> models.Reservation:
  db_reservation = await session.get(models.DBReservation, reservation_id)
  
  if not db_reservation:
    raise HTTPException(status_code=404, detail="Reservation not found")

  if db_reservation.user_id != current_user.id and current_user.roles != "admin":
    raise HTTPException(
      status_code=403, 
      detail="You are not allowed to update this reservation")
  
  data = reservation.model_dump()
  db_reservation.sqlmodel_update(data)
  
  if db_reservation.start_time is None:
    db_reservation.start_time = datetime.datetime.now()
  
  db_reservation.end_time = db_reservation.start_time + datetime.timedelta(hours=reservation.duration_hours)
  session.add(db_reservation)
  await session.commit()
  await session.refresh(db_reservation)
  return models.Reservation.model_validate(db_reservation)

@router.delete("/{reservation_id}")
async def delete_reservation(
    reservation_id: int, 
    current_user: Annotated[models.User, Depends(deps.get_current_user)],
    session: Annotated[AsyncSession, Depends(models.get_session)]
    ) -> None:
  db_reservation = await session.get(models.DBReservation, reservation_id)
  if not db_reservation:
    raise HTTPException(status_code=404, detail="Reservation not found")
  if db_reservation.user_id != current_user.id and current_user.roles != "admin":
    raise HTTPException(
      status_code=403, 
      detail="You are not allowed to delete this reservation")
  await session.delete(db_reservation)
  await session.commit()
  return {"message": "Reservation deleted"}