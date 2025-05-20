from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import List, Optional
from sqlmodel import Session, select
from db.database import get_session
from models.task import Task
from pydantic import BaseModel
from datetime import datetime
import logging

router = APIRouter(prefix="/tasks", tags=["tasks"])
logger = logging.getLogger(__name__)

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    is_completed: bool
    todo_list_id: int
    status_id: int

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    is_completed: Optional[bool] = None
    todo_list_id: Optional[int] = None
    status_id: Optional[int] = None

class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    is_completed: bool
    todo_list_id: int
    status_id: int
    created_at: datetime

    class Config:
        orm_mode = True

@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task_in: TaskCreate, session: Session = Depends(get_session)):
    task = Task(
        title=task_in.title,
        description=task_in.description,
        due_date=task_in.due_date,
        is_completed=task_in.is_completed,
        todo_list_id=task_in.todo_list_id,
        status_id=task_in.status_id,
        created_at=datetime.utcnow()
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    logger.info(f"Task created: {task.title}")  # Log task creation
    return task

@router.get("/", response_model=List[TaskResponse])
def get_tasks(
    todo_list_id: Optional[int] = Query(None),
    is_completed: Optional[bool] = Query(None),
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    query = select(Task)
    if todo_list_id is not None:
        query = query.where(Task.todo_list_id == todo_list_id)
    if is_completed is not None:
        query = query.where(Task.is_completed == is_completed)
    tasks = session.exec(query.offset(skip).limit(limit)).all()
    return tasks

@router.put("/{id}", response_model=TaskResponse)
def update_task(id: int, task_in: TaskUpdate, session: Session = Depends(get_session)):
    task = session.get(Task, id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    for field, value in task_in.dict(exclude_unset=True).items():
        setattr(task, field, value)
    session.commit()
    session.refresh(task)
    logger.info(f"Task updated: {task.title}")  # Log task update
    return task

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(id: int, session: Session = Depends(get_session)):
    task = session.get(Task, id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    session.delete(task)
    session.commit()
    logger.info(f"Task deleted: {id}")  # Log task deletion
    return {"message": "Task deleted successfully"}