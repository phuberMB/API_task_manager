from typing import TYPE_CHECKING, Optional
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime

if TYPE_CHECKING:
    from .todo_list import TodoList
    from .task_status import TaskStatus

class Task(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    is_completed: bool
    todo_list_id: int = Field(foreign_key="todolist.id")
    status_id: int = Field(foreign_key="taskstatus.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    todo_list: Optional["TodoList"] = Relationship(back_populates="tasks")
    status: Optional["TaskStatus"] = Relationship(back_populates="tasks")