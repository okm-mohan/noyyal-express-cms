from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# XAMPP MySQL config
USERNAME = "noyyal_admin"
PASSWORD = "Epiclife@cbe32#"          # XAMPP default
HOST = "localhost"
DB_NAME = "noyyal_express"

DATABASE_URL = f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOST}/{DB_NAME}"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()