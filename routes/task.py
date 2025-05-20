from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import List, Optional
from sqlmodel import Session, select
from db.database import get_session
from models.task import Task
from pydantic import BaseModel
from datetime import datetime
import logging
from auth.jwt_auth import oauth2_scheme, decode_access_token, is_token_revoked
from utils.deps import get_current_user, require_role
from models.user import User, UserRole
from models.todo_list import TodoList

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

@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_role(UserRole.admin, UserRole.user))])
def create_task(task_in: TaskCreate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    todo_list = session.get(TodoList, task_in.todo_list_id)
    if not todo_list:
        raise HTTPException(status_code=404, detail="Todo list not found")
    if current_user.role == UserRole.user and todo_list.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only create tasks in your own lists")
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
    logger.info(f"Task created: {task.title}")
    return task

@router.get("/", response_model=List[TaskResponse])
def get_tasks(
    todo_list_id: Optional[int] = Query(None),
    is_completed: Optional[bool] = Query(None),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_role(UserRole.admin, UserRole.user, UserRole.viewer)),
    session: Session = Depends(get_session)
):
    query = select(Task)
    if current_user.role == UserRole.admin:
        if todo_list_id is not None:
            query = query.where(Task.todo_list_id == todo_list_id)
        if is_completed is not None:
            query = query.where(Task.is_completed == is_completed)
        tasks = session.exec(query.offset(skip).limit(limit)).all()
        return tasks
    else:
        # Solo tareas de listas propias
        user_lists = session.exec(select(TodoList.id).where(TodoList.owner_id == current_user.id)).all()
        # user_lists es una lista de enteros (IDs)
        query = query.where(Task.todo_list_id.in_(user_lists))
        tasks = session.exec(query.offset(skip).limit(limit)).all()
        return tasks

@router.put("/{id}", response_model=TaskResponse)
def update_task(
    id: int,
    task_in: TaskUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    task = session.get(Task, id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    todo_list = session.get(TodoList, task.todo_list_id)
    if current_user.role != UserRole.admin and todo_list.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only update tasks in your own lists")

    # Validar nuevos IDs antes de actualizar
    data = task_in.dict(exclude_unset=True)
    if "todo_list_id" in data:
        new_list = session.get(TodoList, data["todo_list_id"])
        if not new_list:
            raise HTTPException(status_code=404, detail="Todo list not found")
        if current_user.role != UserRole.admin and new_list.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="You can only assign tasks to your own lists")
    if "status_id" in data:
        from models.task_status import TaskStatus
        new_status = session.get(TaskStatus, data["status_id"])
        if not new_status:
            raise HTTPException(status_code=404, detail="Task status not found")

    for field, value in data.items():
        setattr(task, field, value)
    session.commit()
    session.refresh(task)
    logger.info(f"Task updated: {task.title}")
    return task

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    task = session.get(Task, id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    todo_list = session.get(TodoList, task.todo_list_id)
    if current_user.role != UserRole.admin and todo_list.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only delete tasks in your own lists")
    session.delete(task)
    session.commit()
    logger.info(f"Task deleted: {id}")
    return {"message": "Task deleted successfully"}

from auth.jwt_auth import is_token_revoked

def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    if is_token_revoked(token):
        raise HTTPException(status_code=401, detail="Token has been revoked")
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = session.exec(select(User).where(User.username == payload["sub"])).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user