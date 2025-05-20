from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import List, Optional
from sqlmodel import Session, select
from db.database import get_session
from models.todo_list import TodoList
from models.user import User
from pydantic import BaseModel
import logging
from auth.jwt_auth import oauth2_scheme, decode_access_token, is_token_revoked
from utils.deps import get_current_user, require_role
from models.user import UserRole

router = APIRouter(prefix="/lists", tags=["lists"])
logger = logging.getLogger(__name__)

class TodoListCreate(BaseModel):
    title: str
    description: Optional[str] = None
    owner_username: str

class TodoListUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

class TodoListResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    owner_username: str
    created_at: str

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

@router.post("/", response_model=TodoListResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_role(UserRole.admin, UserRole.user))])
def create_list(list_in: TodoListCreate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    # Admin puede crear listas para cualquiera, user solo para sí mismo
    if current_user.role == UserRole.user and list_in.owner_username != current_user.username:
        raise HTTPException(status_code=403, detail="You can only create lists for yourself")
    owner = session.exec(select(User).where(User.username == list_in.owner_username)).first()
    if not owner:
        raise HTTPException(status_code=404, detail="Owner user not found")
    todo_list = TodoList(
        title=list_in.title,
        description=list_in.description,
        owner_id=owner.id
    )
    session.add(todo_list)
    session.commit()
    session.refresh(todo_list)
    logger.info(f"User created: {owner.username}")
    return TodoListResponse(
        id=todo_list.id,
        title=todo_list.title,
        description=todo_list.description,
        owner_username=owner.username,
        created_at=todo_list.created_at.isoformat()
    )

@router.get("/", response_model=List[TodoListResponse])
def get_lists(
    id: Optional[int] = Query(None),
    owner_id: Optional[int] = Query(None),
    username: Optional[str] = Query(None),
    email: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(UserRole.admin, UserRole.user, UserRole.viewer))
):
    # Admin: ve todas, user/viewer: solo sus propias listas
    query = select(TodoList, User).join(User, TodoList.owner_id == User.id)
    if id is not None:
        query = query.where(TodoList.id == id)
    if owner_id is not None:
        query = query.where(TodoList.owner_id == owner_id)
    if username is not None:
        query = query.where(User.username == username)
    if email is not None:
        query = query.where(User.email == email)
    results = session.exec(query.offset(skip).limit(limit)).all()
    response = [
        TodoListResponse(
            id=todo_list.id,
            title=todo_list.title,
            description=todo_list.description,
            owner_username=user.username,
            created_at=todo_list.created_at.isoformat()
        )
        for todo_list, user in results
    ]
    if current_user.role == UserRole.admin:
        return response
    else:
        # Solo listas propias
        response = [l for l in response if l.owner_username == current_user.username]
        return response

@router.put("/{id}", response_model=TodoListResponse)
def update_list(id: int, list_in: TodoListUpdate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    todo_list = session.get(TodoList, id)
    if not todo_list:
        raise HTTPException(status_code=404, detail="List not found")
    if current_user.role != UserRole.admin and todo_list.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only update your own lists")
    if list_in.title is not None:
        todo_list.title = list_in.title
    if list_in.description is not None:
        todo_list.description = list_in.description
    session.commit()
    session.refresh(todo_list)
    owner = session.get(User, todo_list.owner_id)
    return TodoListResponse(
        id=todo_list.id,
        title=todo_list.title,
        description=todo_list.description,
        owner_username=owner.username,
        created_at=todo_list.created_at.isoformat()
    )

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_list(id: int, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    todo_list = session.get(TodoList, id)
    if not todo_list:
        raise HTTPException(status_code=404, detail="List not found")
    if current_user.role != UserRole.admin and todo_list.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only delete your own lists")
    session.delete(todo_list)
    session.commit()
    logger.info(f"Task deleted: {id}")
    return {"message": "List deleted successfully"}