from sqlmodel import Session
from models.task_status import TaskStatus

def create_task_status(session: Session, task_status: TaskStatus):
    session.add(task_status)
    session.commit()
    session.refresh(task_status)
    return task_status

def get_task_status_by_id(session: Session, task_status_id: int):
    return session.get(TaskStatus, task_status_id)

def get_all_task_status(session: Session):
    return session.query(TaskStatus).all()

def update_task_status(session: Session, task_status_id: int, updated_data: dict):
    task_status = session.get(TaskStatus, task_status_id)
    if task_status:
        for key, value in updated_data.items():
            setattr(task_status, key, value)
        session.commit()
        session.refresh(task_status)
    return task_status

def delete_task_status(session: Session, task_status_id: int):
    task_status = session.get(TaskStatus, task_status_id)
    if task_status:
        session.delete(task_status)
        session.commit()
    return task_status