from fastapi import APIRouter, Depends, HTTPException, Request, status

from flask import json

from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, func

from typing import Annotated

from .. import models
from .. import deps

import math

router = APIRouter(prefix="/users",tags=["Users"],)

SIZE_PER_PAGE = 50

@router.post("/create_superuser")
async def create_superuser(
    email: str,
    name: str,
    username: str,
    password: str,
    session: Annotated[AsyncSession, Depends(models.get_session)],
):
    existing_email = await session.exec(
        select(models.DBUser).where(models.DBUser.email == email)
    )
    if existing_email.one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="อีเมลนี้ถูกใช้งานแล้ว",
        )
    
    existing_user = await session.exec(
        select(models.DBUser).where(models.DBUser.username == username)
    )
    if existing_user.one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="ชื่อบัญชีผู้ใช้นี้ถูกใช้งานแล้ว",
        )

    user = models.DBUser(
        email=email,
        name=name,
        username=username,
        roles="admin",
        faculty= "คณะแอดมิน",
        room_permission=True,
    )
    await user.set_password(password)

    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

@router.post("/create")
async def create(
    username: str,
    name: str,
    email: str,
    password: str,
    session: Annotated[AsyncSession, Depends(models.get_session)],
):
    existing_email = await session.exec(
        select(models.DBUser).where(models.DBUser.email == email)
    )
    if existing_email.one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="อีเมลนี้ถูกใช้งานแล้ว",
        )
    
    existing_user = await session.exec(
        select(models.DBUser).where(models.DBUser.username == username)
    )
    if existing_user.one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="ชื่อบัญชีผู้ใช้นี้ถูกใช้งานแล้ว",
        )

    user = models.DBUser(
        username=username,
        name=name,
        email=email,
        roles="visitor",
        faculty="ไม่มีคณะ",
        room_permission=False,
    )
    await user.set_password(password)

    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

@router.get("/get_me")
def get_me(current_user: models.User = Depends(deps.get_current_user)):
    return current_user

@router.get("/get_allUser", response_model=models.UserList)
async def get_users(
    session: Annotated[AsyncSession, Depends(models.get_session)], 
    page: int = 1
    ) -> models.UserList:
  result = await session.exec(select(models.DBUser).offset((page - 1) * SIZE_PER_PAGE).limit(SIZE_PER_PAGE))

  db_users = result.all()
  page_count = int(math.ceil((await session.exec(select(func.count(models.DBUser.id)))).first() / SIZE_PER_PAGE))

  return models.UserList.model_validate(dict(users=db_users, page=page, page_count=page_count, size_per_page=SIZE_PER_PAGE))

@router.get("/admin-only/")
async def admin_only_route(
    current_user: models.User = Depends(deps.get_current_active_superuser)
):
    return {"message": "Welcome, superuser!"}

@router.get("/user_id")
async def get_user_id(
    user_id: int,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.User = Depends(deps.get_current_user),
):

    user = await session.get(models.DBUser, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found this user",
        )
    return user

@router.put("/change_password")
async def change_password(
    user_id: int,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    password_update: models.ChangePasswordUser,
    current_user: models.User = Depends(deps.get_current_user),
): 
    user = await session.get(models.DBUser, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found this user",
        )
    
    if not user.verify_password(password_update.current_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
        )
    
    await user.set_password(password_update.new_password)
    session.add(user)
    await session.commit()

@router.put("/update_user")
async def update_user(
    user_id: int,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    request: Request,
    user_update: models.UpdatedUser,
    current_user: models.User = Depends(deps.get_current_user),
) -> models.User:
    if current_user.id != user_id and current_user.roles != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
   
    user = await session.get(models.DBUser, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found this user",
        )

    if current_user.id == user_id or current_user.roles == "admin":
        if user_update.name is not None:
            user.name = user_update.name
        if user_update.email is not None:
            user.email = user_update.email
        if user_update.faculty is not None:
            user.faculty = user_update.faculty
        if user_update.roles is not None and current_user.roles == "admin":
            user.roles = user_update.roles

        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user
    else:
        raise HTTPException(status_code=403, detail="Not enough permissions to update other users")



@router.put("/forgot_password")
async def forget_password(
    email: str,
    new_password: models.ForgotPassword,
    session: Annotated[AsyncSession, Depends(models.get_session)],
): 
    existing_email = await session.exec(select(models.DBUser).where(models.DBUser.email == email))
    existing_email = existing_email.one_or_none()

    if not existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email not found",
        )
    
    await existing_email.set_password(new_password.new_password)
    session.add(existing_email)
    await session.commit()
    await session.refresh(existing_email)

    return {"message": "Password has been reset successfully"}