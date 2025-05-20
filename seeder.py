from datetime import datetime, timedelta
from db.database import create_db_and_tables, get_session
from models.user import User, UserRole
from models.todo_list import TodoList
from models.task import Task
from models.task_status import TaskStatus, TaskStatusEnum
from auth.jwt_auth import get_password_hash
from sqlalchemy import text

def seed_data():
    create_db_and_tables()  # Crear las tablas si no existen

    with next(get_session()) as session:
        # Borrar en orden: task -> todolist -> taskstatus -> user
        session.exec(text("DELETE FROM task"))
        session.exec(text("DELETE FROM todolist"))
        session.exec(text("DELETE FROM taskstatus"))
        session.exec(text('DELETE FROM "user"'))
        session.commit()

        # Crear estados de tareas
        pending_status = TaskStatus(name=TaskStatusEnum.PENDING, color="yellow")
        in_progress_status = TaskStatus(name=TaskStatusEnum.IN_PROGRESS, color="blue")
        completed_status = TaskStatus(name=TaskStatusEnum.COMPLETED, color="green")
        session.add_all([pending_status, in_progress_status, completed_status])
        session.commit()

        # Crear usuarios de todos los roles
        admin = User(
            username="admin",
            email="admin@example.com",
            hashed_password=get_password_hash("adminpass"),
            role=UserRole.admin
        )
        user = User(
            username="test_user",
            email="test@example.com",
            hashed_password=get_password_hash("userpass"),
            role=UserRole.user
        )
        viewer = User(
            username="viewer",
            email="viewer@example.com",
            hashed_password=get_password_hash("viewerpass"),
            role=UserRole.viewer
        )
        session.add_all([admin, user, viewer])
        session.commit()

        # Crear listas de tareas para admin y user
        admin_list = TodoList(title="Admin List", description="Lista de admin", owner_id=admin.id)
        user_list = TodoList(title="User List", description="Lista de usuario", owner_id=user.id)
        session.add_all([admin_list, user_list])
        session.commit()

        # Crear tareas para cada lista
        task1 = Task(
            title="Admin Task",
            description="Tarea de admin",
            due_date=datetime.utcnow() + timedelta(days=1),
            is_completed=False,
            todo_list_id=admin_list.id,
            status_id=pending_status.id,
            created_at=datetime.utcnow()
        )
        task2 = Task(
            title="User Task",
            description="Tarea de usuario",
            due_date=datetime.utcnow() + timedelta(days=2),
            is_completed=False,
            todo_list_id=user_list.id,
            status_id=in_progress_status.id,
            created_at=datetime.utcnow()
        )
        session.add_all([task1, task2])
        session.commit()

if __name__ == "__main__":
    seed_data()