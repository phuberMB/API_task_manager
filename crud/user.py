from sqlmodel import Session
from models.user import User

def create_user(session: Session, user: User):
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def get_user_by_id(session: Session, user_id: int):
    return session.get(User, user_id)

def get_all_users(session: Session):
    return session.query(User).all()

def update_user(session: Session, user_id: int, updated_data: dict):
    user = session.get(User, user_id)
    if user:
        for key, value in updated_data.items():
            setattr(user, key, value)
        session.commit()
        session.refresh(user)
    return user

def delete_user(session: Session, user_id: int):
    user = session.get(User, user_id)
    if user:
        session.delete(user)
        session.commit()
    return user