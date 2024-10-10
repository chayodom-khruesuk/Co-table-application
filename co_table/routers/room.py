from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from .. import models
from .. import deps

import math

router = APIRouter(
    prefix="/rooms",
    tags=["rooms"],
)

SIZE_PER_PAGE = 50

@router.post("/create_room", response_model=models.Room)
async def create_room(
    room: models.CreateRoom, 
    current_user: Annotated[models.User, Depends(deps.get_current_user)],
    session: Annotated[AsyncSession, Depends(models.get_session)]
    ) -> models.Room:
  if current_user.roles != "admin" or current_user.room_permission != True:
    raise HTTPException(status_code=403, detail="Not enough permissions")
  db_room = models.DBRoom.model_validate(room)
  db_room.user_id = current_user.id
  session.add(db_room)
  await session.commit()
  await session.refresh(db_room)
  return models.Room.model_validate(db_room)

@router.get("/get_listRoom", response_model=models.RoomList)
async def get_rooms(
    session: Annotated[AsyncSession, Depends(models.get_session)], 
    page: int = 1
    ) -> models.RoomList:
  result = await session.exec(select(models.DBRoom).offset((page - 1) * SIZE_PER_PAGE).limit(SIZE_PER_PAGE))

  db_rooms = result.all()
  page_count = int(math.ceil((await session.exec(select(func.count(models.DBRoom.id)))).first() / SIZE_PER_PAGE))

  return models.RoomList.model_validate(dict(rooms=db_rooms, page=page, page_count=page_count, size_per_page=SIZE_PER_PAGE))

@router.get("/room_id", response_model=models.Room)
async def get_room(
    room_id: int, 
    session: Annotated[AsyncSession, Depends(models.get_session)]
    ) -> models.Room:
  db_room = await session.get(models.DBRoom, room_id)
  if db_room:
    return models.Room.model_validate(db_room)
  raise HTTPException(status_code=404, detail="Room not found")

@router.put("/update_room", response_model=models.Room)
async def update_room(
    room_id: int, 
    room: models.UpdateRoom, 
    current_user: Annotated[models.User, Depends(deps.get_current_user)],
    session: Annotated[AsyncSession, Depends(models.get_session)]
    ) -> models.Room:
  if current_user.roles != "admin" or  current_user.room_permission != True:
    raise HTTPException(status_code=403, detail="Not enough permissions")
  data = room.model_dump()
  db_room = await session.get(models.DBRoom, room_id)
  if db_room.user_id != current_user.id:
    raise HTTPException(status_code=403, detail="You are not the owner of this room")
  if db_room:
    db_room.sqlmodel_update(data)
    session.add(db_room)
    await session.commit()
    await session.refresh(db_room)
    return models.Room.model_validate(db_room)
  raise HTTPException(status_code=404, detail="Room not found")

@router.delete("/delete_room")
async def delete_room(
    room_id: int,
    current_user: Annotated[models.User, Depends(deps.get_current_user)],
    session: Annotated[AsyncSession, Depends(models.get_session)]
    ) -> dict:
  if current_user.roles != "admin" or  current_user.room_permission != True:
    raise HTTPException(status_code=403, detail="Not enough permissions")
  db_room = await session.get(models.DBRoom, room_id)
  if db_room.user_id != current_user.id:
    raise HTTPException(status_code=403, detail="You are not the owner of this room")
  if db_room:
    await session.delete(db_room)
    await session.commit()
    return {"message": "Room deleted"}
  raise HTTPException(status_code=404, detail="Room not found")