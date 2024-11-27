from sqlalchemy.orm import Session
from models import User as DBUser
from schemas.user import UserCreate
from services.auth_service import get_password_hash


def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = DBUser(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
        disabled=False,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user(db: Session, username: str):
    return db.query(DBUser).filter(DBUser.username == username).first()
