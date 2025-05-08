from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from .task import Task
from .user import User

class TodoList(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str = Field(unique=False)
    description: str = Optional[str]
    owner_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    tasks: List["Task"] = Relationship(back_populates="todo_list")
    owner: Optional["User"] = Relationship(back_populates="todo_lists")