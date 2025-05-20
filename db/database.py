from sqlmodel import SQLModel, create_engine, Session

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/task_manager"

# Crear el motor de la base de datos
engine = create_engine(DATABASE_URL, echo=True)

# Crear las tablas en la base de datos
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# Crear una sesión para interactuar con la base de datos
def get_session():
    with Session(engine) as session:
        yield session