import re

from fastapi import APIRouter, Depends, HTTPException
from fastapi_framework import get_data, database_dependency
from fastapi_framework.database import DB, select

from app.models.user import User

router = APIRouter(prefix="/user", tags=["user"])

RE_USERNAME = re.compile(r"^[A-Za-z0-9\_\-\.äöüÄÖÜ]{3,50}$")


@router.get("/")
async def get_user(data=Depends(get_data)):
    return data.get("user")


@router.get("/username")
async def get_username(data=Depends(get_data)):
    return data.get("user").get("username")


@router.post("/username")
async def set_username(username: str, data=Depends(get_data), db: DB = Depends(database_dependency)):
    if data["user"]["username"] == username:
        raise HTTPException(400, "Nothing Changed")
    if await db.exists(select(User).filter_by(username=username)):
        raise HTTPException(409, "Username already used")
    user: User = await db.first(select(User).filter_by(id=data["user"]["id"]))
    if not user:
        raise HTTPException(500, "Unexpected Error")
    if not RE_USERNAME.match(username):
        raise HTTPException(400, "Username doesn't match Regex")
    user.username = username
    await db.commit()
    return {"id": user.id, "username": user.username}
