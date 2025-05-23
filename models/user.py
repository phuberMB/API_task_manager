from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from typing import List
from .todo_list import TodoList
from enum import Enum

class UserRole(str, Enum):
    admin = "admin"
    user = "user"
    viewer = "viewer"

class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    username: str = Field(unique=True)
    email: str = Field(unique=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    role: UserRole = Field(default=UserRole.user)
    todo_lists: List["TodoList"] = Relationship(back_populates="owner")