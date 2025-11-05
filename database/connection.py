from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base
import os
from dotenv import load_dotenv
from pathlib import Path

# Загружаем переменные окружения
config_paths = [
    Path(__file__).parent.parent / 'config.env',
    Path.cwd() / 'config.env',
]
for config_path in config_paths:
    if config_path.exists():
        load_dotenv(config_path, override=False)
        break

# 1. Define the database URL from environment variable
# MySQL connection string format: mysql+pymysql://user:password@host/database_name
# Example: mysql+pymysql://user:1234@localhost/audio_store
# The connection string is loaded from config.env file
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./audio_store.db")

# 2. Create the SQLAlchemy engine.
# The `connect_args` is needed only for SQLite to allow multi-threaded access.
# For MySQL/PostgreSQL, we don't need this argument - it's removed automatically.
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
# For MySQL, connect_args will be empty dict, which is correct

engine = create_engine(
    DATABASE_URL, 
    connect_args=connect_args
)

# 3. Create a session factory.
# This will be used to create new session objects for database transactions.
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine
)

def get_db():
    """
    Dependency to get a database session.
    It ensures that the database connection is always closed after the request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    Initializes the database by creating all tables defined in the models.
    This function should be called once at application startup.
    """
    print("Initializing the database...")
    # The `Base.metadata.create_all` function uses the engine to create
    # all tables that are subclasses of `Base`.
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully.")
