import re

from fastapi import APIRouter, Depends, HTTPException
from fastapi_framework import get_data, database_dependency, pwd_context
from fastapi_framework.database import DB, select
from app.schemas.user import UserSchema, UpdateUser

from app.models.user import User

router = APIRouter(prefix="/user", tags=["user"])

RE_USERNAME = re.compile(r"^[A-Za-z0-9\_\-\.äöüÄÖÜ]{3,50}$")


@router.get("/", response_model=UserSchema)
async def get_user(data=Depends(get_data)):
    return data.get("user")


@router.put("/", response_model=UserSchema)
async def update_user(updated_user: UpdateUser, data=Depends(get_data), db: DB = Depends(database_dependency)):
    if data["user"]["username"] == updated_user.username:
        raise HTTPException(400, "Nothing Changed")
    if await db.exists(select(User).filter_by(username=updated_user.username)):
        raise HTTPException(409, "Username already used")
    user: User = await db.first(select(User).filter_by(id=data["user"]["id"]))
    if not user:
        raise HTTPException(500, "Unexpected Error")
    if not RE_USERNAME.match(updated_user.username):
        raise HTTPException(400, "Username doesn't match Regex")
    user.username = updated_user.username
    if updated_user.password:
        user.password = pwd_context.hash(updated_user.password)
    await db.commit()
    return UserSchema(**{"id": user.id, "username": user.username})
