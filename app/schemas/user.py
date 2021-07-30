from typing import Optional

from pydantic import BaseModel


class UserSchema(BaseModel):
    id: int
    username: str


class CreateUser(BaseModel):
    username: str
    password: str


class UpdateUser(BaseModel):
    username: Optional[str]
    password: Optional[str]
