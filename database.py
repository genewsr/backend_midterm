from sqlmodel import SQLModel, create_engine

sqlite_url = "sqlite:///./election.db"
engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)