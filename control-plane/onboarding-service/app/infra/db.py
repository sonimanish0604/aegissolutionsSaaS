import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://aegis:aegis@localhost:5432/controlplane")

engine = create_engine(DATABASE_URL, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()