from typing import Union

from fastapi_framework.database import database_dependency, DB
from sqlalchemy import Column, Integer, String


class User(database_dependency.db.Base):
    __tablename__ = "users"
    id: Union[int, Column] = Column(Integer, primary_key=True)
    username: Union[str, Column] = Column(String(50), unique=True)
    password: Union[str, Column] = Column(String(255))

    @staticmethod
    async def create(username: str, password: str, db: DB) -> "User":
        row: User = User(username=username, password=password)
        await db.add(row)
        return row
