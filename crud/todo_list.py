from sqlmodel import Session
from models.todo_list import TodoList

def create_todo_list(session: Session, todo_list: TodoList):
    session.add(todo_list)
    session.commit()
    session.refresh(todo_list)
    return todo_list

def get_todo_list_by_id(session: Session, todo_list_id: int):
    return session.get(TodoList, todo_list_id)

def get_all_todo_list(session: Session):
    return session.query(TodoList).all()

def update_todo_list(session:Session, todo_list_id: int, updated_data: dict):
    todo_list = session.get(TodoList, todo_list_id)
    if todo_list:
        for key, value in updated_data.items():
            setattr(todo_list, key, value)
        session.commit()
        session.refresh(todo_list)
    return todo_list

def delete_todo_list(session: Session, todo_list_id: int):
    todo_list = session.get(TodoList, todo_list_id)
    if todo_list:
        session.delete(todo_list)
        session.commit()
    return todo_list
