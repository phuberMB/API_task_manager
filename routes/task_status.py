from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from sqlmodel import Session, select
from db.database import get_session
from models.task_status import TaskStatus
from pydantic import BaseModel
import logging

router = APIRouter(prefix="/status", tags=["status"])
logger = logging.getLogger(__name__)

class TaskStatusCreate(BaseModel):
    name: str
    color: Optional[str] = None

class TaskStatusUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None

class TaskStatusResponse(BaseModel):
    id: int
    name: str
    color: Optional[str] = None

    class Config:
        orm_mode = True

@router.post("/", response_model=TaskStatusResponse, status_code=status.HTTP_201_CREATED)
def create_status(status_in: TaskStatusCreate, session: Session = Depends(get_session)):
    status_obj = TaskStatus(name=status_in.name, color=status_in.color)
    session.add(status_obj)
    session.commit()
    session.refresh(status_obj)
    logger.info(f"Status created: {status_obj.name}")
    return status_obj

@router.get("/", response_model=List[TaskStatusResponse])
def get_statuses(session: Session = Depends(get_session)):
    statuses = session.exec(select(TaskStatus)).all()
    return statuses

@router.put("/{id}", response_model=TaskStatusResponse)
def update_status(id: int, status_in: TaskStatusUpdate, session: Session = Depends(get_session)):
    status_obj = session.get(TaskStatus, id)
    if not status_obj:
        raise HTTPException(status_code=404, detail="Status not found")
    if status_in.name is not None:
        status_obj.name = status_in.name
    if status_in.color is not None:
        status_obj.color = status_in.color
    session.commit()
    session.refresh(status_obj)
    logger.info(f"Status updated: {status_obj.name}")
    return status_obj

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_status(id: int, session: Session = Depends(get_session)):
    status_obj = session.get(TaskStatus, id)
    if not status_obj:
        raise HTTPException(status_code=404, detail="Status not found")
    session.delete(status_obj)
    session.commit()
    logger.info(f"Status deleted: {id}")
    return {"message": "Status deleted successfully"}