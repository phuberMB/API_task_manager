from enum import Enum
from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional
from .task import Task

class TaskStatusEnum(str, Enum):
    PENDING = "pendiente"
    IN_PROGRESS = "en progreso"
    COMPLETED = "completada"

class TaskStatus(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: TaskStatusEnum
    color: Optional[str] = None
    
    tasks: List["Task"] = Relationship(back_populates="status")