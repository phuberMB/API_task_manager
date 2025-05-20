from datetime import datetime, timedelta
from db.database import create_db_and_tables, get_session
from models.user import User
from models.todo_list import TodoList
from models.task import Task
from models.task_status import TaskStatus, TaskStatusEnum

def seed_data():
    create_db_and_tables()  # Crear las tablas si no existen

    with next(get_session()) as session:
        # Crear estados de tareas
        pending_status = TaskStatus(name=TaskStatusEnum.PENDING, color="yellow")
        in_progress_status = TaskStatus(name=TaskStatusEnum.IN_PROGRESS, color="blue")
        completed_status = TaskStatus(name=TaskStatusEnum.COMPLETED, color="green")

        session.add_all([pending_status, in_progress_status, completed_status])
        session.commit()

        # Crear un usuario
        user = User(username="test_user", email="test@example.com", hashed_password="hashed_password")
        session.add(user)
        session.commit()

        # Crear una lista de tareas
        todo_list = TodoList(title="My First Todo List", description="This is a test list", owner_id=user.id)
        session.add(todo_list)
        session.commit()

        # Crear tareas
        task1 = Task(
            title="Task 1",
            description="First task",
            due_date=datetime.utcnow() + timedelta(days=1),
            is_completed=False,
            todo_list_id=todo_list.id,
            status_id=pending_status.id,
            created_at=datetime.utcnow()
        )
        task2 = Task(
            title="Task 2",
            description="Second task",
            due_date=datetime.utcnow() + timedelta(days=2),
            is_completed=False,
            todo_list_id=todo_list.id,
            status_id=in_progress_status.id,
            created_at=datetime.utcnow()
        )

        session.add_all([task1, task2])
        session.commit()

if __name__ == "__main__":
    seed_data()