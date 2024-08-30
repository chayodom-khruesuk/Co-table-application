from fastapi import APIRouter, Depends, HTTPException, Request, status

from flask import json

from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from typing import Annotated

from .. import models
from .. import deps

router = APIRouter(tags=["Users"])

@router.post("/create_superuser")
async def create_superuser(
    email: str,
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
            detail="An account with this email already exists.",
        )
    
    existing_user = await session.exec(
        select(models.DBUser).where(models.DBUser.username == username)
    )
    if existing_user.one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this username already exists.",
        )

    user = models.DBUser(
        email=email,
        username=username,
        roles=json.dumps(["admin"])
    )
    await user.set_password(password)

    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

@router.post("/create")
async def create(
    email: str,
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
            detail="An account with this email already exists.",
        )
    
    existing_user = await session.exec(
        select(models.DBUser).where(models.DBUser.username == username)
    )
    if existing_user.one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this username already exists.",
        )

    user = models.DBUser(
        email=email,
        username=username,
        roles=json.dumps(["user"])
    )
    await user.set_password(password)

    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

@router.get("/get_me")
def get_me(current_user: models.User = Depends(deps.get_current_user)):
    return current_user

@router.get("/admin-only/")
async def admin_only_route(
    current_user: models.User = Depends(deps.get_current_active_superuser)
):
    return {"message": "Welcome, superuser!"}

@router.get("/{user_id}")
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
    verify_password: str,
    user_update: models.UpdatedUser,
    current_user: models.User = Depends(deps.get_current_user),
) -> models.User:

    user = await session.get(models.DBUser, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found this user",
        )

    if not user.verify_password(verify_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
        )

    user.sqlmodel_update(user_update)
    session.add(user)
    await session.commit()
    await session.refresh(user)

    return user