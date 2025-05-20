from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from sqlmodel import Session, select
from db.database import get_session
from models.task_status import TaskStatus
from pydantic import BaseModel
import logging
from auth.jwt_auth import oauth2_scheme, decode_access_token, is_token_revoked
from utils.deps import get_current_user, require_role
from models.user import User, UserRole

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

@router.post(
    "/", 
    response_model=TaskStatusResponse, 
    status_code=status.HTTP_201_CREATED, 
    dependencies=[Depends(require_role(UserRole.admin))]
)
def create_status(
    status_in: TaskStatusCreate, 
    session: Session = Depends(get_session)
):
    status_obj = TaskStatus(name=status_in.name, color=status_in.color)
    session.add(status_obj)
    session.commit()
    session.refresh(status_obj)
    logger.info(f"Status created: {status_obj.name}")
    return status_obj

@router.get(
    "/", 
    response_model=List[TaskStatusResponse], 
    dependencies=[Depends(require_role(UserRole.admin, UserRole.user, UserRole.viewer))]
)
def get_statuses(session: Session = Depends(get_session)):
    statuses = session.exec(select(TaskStatus)).all()
    return statuses

@router.put(
    "/{id}", 
    response_model=TaskStatusResponse, 
    dependencies=[Depends(require_role(UserRole.admin))]
)
def update_status(
    id: int, 
    status_in: TaskStatusUpdate, 
    session: Session = Depends(get_session)
):
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

@router.delete(
    "/{id}", 
    status_code=status.HTTP_204_NO_CONTENT, 
    dependencies=[Depends(require_role(UserRole.admin))]
)
def delete_status(
    id: int, 
    session: Session = Depends(get_session)
):
    status_obj = session.get(TaskStatus, id)
    if not status_obj:
        raise HTTPException(status_code=404, detail="Status not found")
    session.delete(status_obj)
    session.commit()
    logger.info(f"Status deleted: {id}")
    return {"message": "Status deleted successfully"}