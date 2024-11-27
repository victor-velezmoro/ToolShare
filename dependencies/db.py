from sqlalchemy.orm import Session
from database import SessionLocal
import logging

logger = logging.getLogger(__name__)


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
