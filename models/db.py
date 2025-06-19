from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from constants import DB_URI

engine = create_engine(DB_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()