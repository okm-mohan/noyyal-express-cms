from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from urllib.parse import quote_plus
import os
from env_loader import load_local_env

load_local_env()

USERNAME = os.getenv("DB_USER", "root")
PASSWORD = os.getenv("DB_PASSWORD", "")
HOST = os.getenv("DB_HOST", "localhost")
PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "noyyalexpress")

DATABASE_URL = (
    f"mysql+pymysql://{USERNAME}:{quote_plus(PASSWORD)}@{HOST}:{PORT}/{DB_NAME}"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
