from sqlmodel import Session
from models.task import Task

def create_task(session: Session, task: Task):
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

def get_task_by_id(session: Session, task_id: int):
    return session.get(Task, task_id)

def get_all_tasks(session: Session):
    return session.query(Task).all()

def update_task(session: Session, task_id: int, updated_data: dict):
    task = session.get(Task, task_id)
    if task:
        for key, value in updated_data.items():
            setattr(task, key, value)
        session.commit()
        session. refresh(task)
    return task

def delete_task(session: Session, task_id: int):
    task = session.get(Task, task_id)
    if task:
        session.delete(task)
        session.commit()
    return task