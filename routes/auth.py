from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from db.database import get_session
from models.user import User, UserRole
from auth.jwt_auth import get_password_hash, create_access_token, create_refresh_token, verify_password, decode_refresh_token, is_token_revoked, decode_access_token, oauth2_scheme
from pydantic import BaseModel, EmailStr
from datetime import timedelta
import os

router = APIRouter(prefix="/api/auth", tags=["auth"])

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    role: UserRole = UserRole.user

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

REVOKED_TOKENS_FILE = "revoked_tokens.txt"

def revoke_token(token: str):
    with open(REVOKED_TOKENS_FILE, "a") as f:
        f.write(token + "\n")

@router.post("/register")
def register(data: RegisterRequest, session: Session = Depends(get_session)):
    if session.exec(select(User).where(User.username == data.username)).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    if session.exec(select(User).where(User.email == data.email)).first():
        raise HTTPException(status_code=400, detail="Email already exists")
    user = User(
        username=data.username,
        email=data.email,
        hashed_password=get_password_hash(data.password),
        role=data.role
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"message": "User registered successfully"}

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.username == form_data.username)).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    # Expiración según rol
    if user.role == UserRole.admin:
        expire = timedelta(minutes=60)
    elif user.role == UserRole.viewer:
        expire = timedelta(minutes=15)
    else:
        expire = timedelta(minutes=30)
    access_token = create_access_token(data={"sub": user.username, "role": user.role}, expires_delta=expire)
    refresh_token = create_refresh_token(data={"sub": user.username, "role": user.role})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh")
def refresh_token(refresh_token: str = Body(...), session: Session = Depends(get_session)):
    payload = decode_refresh_token(refresh_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    user = session.exec(select(User).where(User.username == payload["sub"])).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    # Expiración según rol
    if user.role == UserRole.admin:
        expire = timedelta(minutes=60)
    elif user.role == UserRole.viewer:
        expire = timedelta(minutes=15)
    else:
        expire = timedelta(minutes=30)
    access_token = create_access_token(data={"sub": user.username, "role": user.role}, expires_delta=expire)
    return {"access_token": access_token, "token_type": "bearer"}

from auth.jwt_auth import revoke_token, decode_access_token
from datetime import datetime

@router.post("/logout")
def logout(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload or "exp" not in payload:
        raise HTTPException(status_code=400, detail="Invalid token")
    exp_timestamp = payload["exp"]
    now = datetime.utcnow().timestamp()
    seconds_left = int(exp_timestamp - now)
    if seconds_left > 0:
        revoke_token(token, seconds_left)
    return {"message": "Logout successful"}

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

@router.post("/forgot-password")
def forgot_password(
    data: ForgotPasswordRequest,
    session: Session = Depends(get_session)
):
    user = session.exec(select(User).where(User.email == data.email)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Token de recuperación válido por 15 minutos
    token = create_access_token(
        data={"sub": user.username, "action": "reset_password"},
        expires_delta=timedelta(minutes=15)
    )
    return {"reset_token": token, "message": "Use this token to reset your password within 15 minutes."}

@router.post("/reset-password")
def reset_password(
    data: ResetPasswordRequest,
    session: Session = Depends(get_session)
):
    from auth.jwt_auth import decode_access_token
    payload = decode_access_token(data.token)
    if not payload or payload.get("action") != "reset_password":
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    username = payload.get("sub")
    user = session.exec(select(User).where(User.username == username)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.hashed_password = get_password_hash(data.new_password)
    session.commit()
    return {"message": "Password reset successfully"}