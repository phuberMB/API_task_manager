from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import List, Optional
from sqlmodel import Session, select
from db.database import get_session
from models.user import User
from pydantic import BaseModel
import logging

router = APIRouter(prefix="/users", tags=["users"])
logger = logging.getLogger(__name__)

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None

@router.get("/", response_model=List[User])
def get_users(
    id: Optional[int] = Query(None),
    username: Optional[str] = Query(None),
    email: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    query = select(User)
    if id is not None:
        query = query.where(User.id == id)
    if username is not None:
        query = query.where(User.username == username)
    if email is not None:
        query = query.where(User.email == email)
    users = session.exec(query.offset(skip).limit(limit)).all()
    return users

@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, session: Session = Depends(get_session)):
    db_user = session.exec(select(User).where((User.username == user.username) | (User.email == user.email))).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username or email already registered")
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=user.password  # Aquí deberías hashear la contraseña en producción
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    logger.info(f"User created: {new_user.username}")
    return new_user

@router.put("/{id}", response_model=User)
def update_user(id: int, user: UserUpdate, session: Session = Depends(get_session)):
    db_user = session.get(User, id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.username is not None:
        db_user.username = user.username
    if user.email is not None:
        db_user.email = user.email
    session.commit()
    session.refresh(db_user)
    return db_user

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(id: int, session: Session = Depends(get_session)):
    db_user = session.get(User, id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(db_user)
    session.commit()
    logger.info(f"Task deleted: {id}")
    return {"message": "User deleted successfully"}