# db/session.py
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
import boto3
import os

# ---------------------------------------
# Get database URL from AWS Parameter Store
# ---------------------------------------

def get_database_url():
    try:
        # Attempt to read from AWS Parameter Store
        ssm = boto3.client("ssm", region_name="us-east-1")

        response = ssm.get_parameter(
            Name="/supportbot/database_url",
            WithDecryption=True
        )

        print("Loaded DATABASE_URL from AWS Parameter Store")

        return response["Parameter"]["Value"]

    except Exception as e:
        print("Using local DATABASE_URL from environment")

        return os.getenv(
            "DATABASE_URL",
            "postgresql://postgres:Eleventeen2005@supportbot-db.cyxy2gyok0ao.us-east-1.rds.amazonaws.com:5432/postgres"
        )


DATABASE_URL = get_database_url()

# ---------------------------------------
# SQLAlchemy setup
# ---------------------------------------

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


# ---------------------------------------
# Initialize database
# ---------------------------------------

def init_db():
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()

    Base.metadata.create_all(bind=engine)