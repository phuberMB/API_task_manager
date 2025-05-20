from fastapi import Depends, HTTPException, status
from models.user import User, UserRole
from db.database import get_session
from sqlmodel import Session, select
from auth.jwt_auth import decode_access_token, oauth2_scheme

def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = session.exec(select(User).where(User.username == payload["sub"])).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def require_role(*roles):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return role_checker

def require_self_or_admin(user_id_param: str = "id"):
    def checker(current_user: User = Depends(get_current_user), **kwargs):
        user_id = kwargs.get(user_id_param)
        if current_user.role == UserRole.admin:
            return current_user
        if current_user.id != user_id:
            raise HTTPException(status_code=403, detail="You can only operate on your own user")
        return current_user
    return checker