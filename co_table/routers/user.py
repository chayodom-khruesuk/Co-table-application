from fastapi import APIRouter, Depends, HTTPException, status

from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from typing import Annotated

from co_table.models.user import DBUser, RegisteredUser, User
from .. import models

router = APIRouter(tags=["Users"])

@router.post("/create")
async def create_user(
    user_info: RegisteredUser,
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> User:

    result = await session.exec(
        select(DBUser).where(DBUser.username == user_info.username)
    )

    user = result.one_or_none()

    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This username is exists.",
        )

    user = DBUser.from_orm(user_info)
    await user.set_password(user_info.password)
    session.add(user)
    await session.commit()
    return user
