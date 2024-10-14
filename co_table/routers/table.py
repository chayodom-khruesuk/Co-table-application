from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from .. import models
from .. import deps

import math

router = APIRouter(
    prefix="/tables",
    tags=["tables"],
)

SIZE_PER_PAGE = 50

@router.post("/create_table", response_model=models.Table)
async def create_Table(
    table: models.CreateTable, 
    current_user: Annotated[models.User, Depends(deps.get_current_user)],
    session: Annotated[AsyncSession, Depends(models.get_session)]
    ) -> models.Table:
  if current_user.roles != "admin" or current_user.room_permission != True:
    raise HTTPException(status_code=403, detail="Not enough permissions")
  created_tables = []
  result = await session.exec(select(models.DBTable.number).where(models.DBTable.room_id == table.room_id))
  max_number = max(result.all() or [0])
  for i in range(table.number):
    db_table = models.DBTable.model_validate(table)
    db_room = await session.get(models.DBRoom, db_table.room_id)
    if db_room.user_id != current_user.id or current_user.roles != "admin":
      raise HTTPException(
          status_code=403,
          detail="Not enough permissions"
    )
    if not db_room:
        raise HTTPException(
            status_code=404,
            detail="Room not found"
        )
    db_table.room = db_room
    db_table.number = max_number + i + 1
    session.add(db_table)
    created_tables.append(db_table)
  await session.commit()
  for db_table in created_tables:
    await session.refresh(db_table)
  return models.Table.model_validate(db_table)

@router.get("/get_listTable", response_model=models.TableList)
async def get_tables(
    session: Annotated[AsyncSession, Depends(models.get_session)], 
    page: int = 1
    ) -> models.TableList:
  result = await session.exec(select(models.DBTable).offset((page - 1) * SIZE_PER_PAGE).limit(SIZE_PER_PAGE))

  db_tables = result.all()
  page_count = int(math.ceil((await session.exec(select(func.count(models.DBTable.id)))).first() / SIZE_PER_PAGE))

  return models.TableList.model_validate(dict(tables=db_tables, page=page, page_count=page_count, size_per_page=SIZE_PER_PAGE))


@router.get("/table_id", response_model=models.Table)
async def get_table(
    table_id: int, 
    session: Annotated[AsyncSession, Depends(models.get_session)]
) -> models.Table:
    result = await session.execute(select(models.DBTable).where(models.DBTable.id == table_id))
    db_table = result.scalar_one_or_none()

    if db_table:
        return models.Table.model_validate(db_table)
    else:
        raise HTTPException(status_code=404, detail="Table not found")
    
@router.delete("/delete_table")
async def delete_Table(
    table_id: int, 
    current_user: Annotated[models.User, Depends(deps.get_current_user)],
    session: Annotated[AsyncSession, Depends(models.get_session)]
    ) -> dict:
  if current_user.roles != "admin" or current_user.room_permission != True:
    raise HTTPException(status_code=403, detail="Not enough permissions")
  db_table = await session.get(models.DBTable, table_id)
  if db_table:
     await session.refresh(db_table, ['room'])
  if db_table.room.user_id != current_user.id:
      raise HTTPException(
          status_code=403,
          detail="Not enough permissions"
      )
  if db_table:
    await session.delete(db_table)
    await session.commit()
    return {"message": "Table deleted"}
  raise HTTPException(status_code=404, detail="Table not found")

@router.delete("/del_table_in_room/{room_id}")
async def del_table_in_room(
    room_id: int,
    current_user: Annotated[models.User, Depends(deps.get_current_user)],
    session: Annotated[AsyncSession, Depends(models.get_session)]
) -> dict:
    if current_user.roles != "admin" or current_user.room_permission != True:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db_room = await session.get(models.DBRoom, room_id)
    if not db_room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    if db_room.user_id != current_user.id and current_user.roles != "admin":
        raise HTTPException(status_code=403, detail="You are not the owner of this room")
    
    result = await session.execute(delete(models.DBTable).where(models.DBTable.room_id == room_id))
    
    await session.commit()
    
    return {"message": f"All tables in room {room_id} have been deleted", "tables_deleted": result.rowcount}