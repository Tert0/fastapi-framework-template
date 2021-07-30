import re

from fastapi import APIRouter, Depends, HTTPException
from fastapi_framework import get_data, database_dependency, pwd_context
from fastapi_framework.database import DB, select
from app.schemas.user import UserSchema, UpdateUser

from app.models.user import User

router = APIRouter(prefix="/user", tags=["user"])

RE_USERNAME = re.compile(r"^[A-Za-z0-9\_\-\.äöüÄÖÜ]{3,50}$")


@router.get("/", response_model=UserSchema)
async def get_user(data=Depends(get_data), db: DB = Depends(database_dependency)):
    user: User = await db.first(select(User).filter_by(id=data["user"]["id"]))
    return UserSchema(**{"id": user.id, "username": user.username})


@router.put("/", response_model=UserSchema)
async def update_user(updated_user: UpdateUser, data=Depends(get_data), db: DB = Depends(database_dependency)):
    user: User = await db.first(select(User).filter_by(id=data["user"]["id"]))
    if user.username == updated_user.username:
        updated_user.username = None
    elif updated_user.username:
        if not RE_USERNAME.match(updated_user.username):
            raise HTTPException(400, "Username doesn't match Regex")
        if await db.exists(select(User).filter_by(username=updated_user.username)):
            raise HTTPException(409, "Username already used")
    if not updated_user.username and not updated_user.password:
        raise HTTPException(400, "Nothing Changed")
    if not user:
        raise HTTPException(500, "Unexpected Error")
    if updated_user.username:
        user.username = updated_user.username
    if updated_user.password:
        user.password = pwd_context.hash(updated_user.password)
    await db.commit()
    return UserSchema(**{"id": user.id, "username": user.username})
