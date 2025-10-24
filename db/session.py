# db/session.py
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
# from dotenv import load_dotenv
import os

# 1. Load environment variables from .env file
# load_dotenv()

# 2. Read the DATABASE_URL variable
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@db:5432/supportbot")

# 3. Create SQLAlchemy engine (connects to PostgreSQL)
engine = create_engine(DATABASE_URL)

# 4. Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 5. Base class for models
Base = declarative_base()

# 6. Initialize pgvector extension if not present
def init_db():
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()
    Base.metadata.create_all(bind=engine)
