from typing import Dict

from fastapi import APIRouter, Depends, HTTPException
from fastapi_framework import (
    redis_dependency,
    database_dependency,
    pwd_context,
    generate_tokens,
    check_refresh_token,
    invalidate_refresh_token,
    get_data,
    Redis,
)
from app.schemas.authentication import Tokens
from fastapi_framework.database import select, DB
import re
from app.models.user import User
from app.schemas.user import UserSchema

router = APIRouter(prefix="/authentication", tags=["auth"])

RE_USERNAME = re.compile(r"^[A-Za-z0-9\_\-\.äöüÄÖÜ]{3,50}$")


@router.on_event("startup")
async def on_startup():
    await redis_dependency.init()
    await database_dependency.init()


@router.post("/token", response_model=Tokens)
async def token_route(
    username: str, password: str, redis: Redis = Depends(redis_dependency), db: DB = Depends(database_dependency)
):
    user: User
    if not (user := await db.first(select(User).filter_by(username=username))):
        raise HTTPException(401, detail="Username or Password is wrong")
    if not pwd_context.verify(password, user.password):
        raise HTTPException(401, detail="Username or Password is wrong")
    return await generate_tokens({"user": {"id": user.id, "username": user.username}}, int(user.id), redis)


@router.post("/register", response_model=UserSchema)
async def register_route(username: str, password: str, db: DB = Depends(database_dependency)):
    if await db.exists(select(User).filter_by(username=username)):
        raise HTTPException(409, "Username already exists")
    if not RE_USERNAME.match(username):
        raise HTTPException(400, "Username doesn't match Regex")
    user: User = await User.create(username, pwd_context.hash(password), db)
    await db.commit()
    return UserSchema(**{"id": user.id, "username": user.username})


@router.post("/refresh", response_model=Tokens)
async def refresh_route(
    refresh_token: str, redis: Redis = Depends(redis_dependency), db: DB = Depends(database_dependency)
):
    data: Dict = {}
    if not await check_refresh_token(refresh_token, redis):
        raise HTTPException(401, "Refresh Token Invalid")
    try:
        data = await get_data(refresh_token)
    except HTTPException as e:
        if e.detail == "Token is expired":
            await invalidate_refresh_token(refresh_token, redis)
            raise e
    user: User = await db.first(select(User).filter_by(id=int(data["user_id"])))
    if not user:
        raise HTTPException(500, "Unexpected Error")
    await invalidate_refresh_token(refresh_token, redis)
    return await generate_tokens({"user": {"id": user.id, "username": user.username}}, int(user.id), redis)


@router.post("/logout")
async def logout_route(refresh_token: str, redis: Redis = Depends(redis_dependency)):
    await invalidate_refresh_token(refresh_token, redis)
    return "Logged out"
