from fastapi import APIRouter, Depends, HTTPException
from schemas.user import User, UserCreate
from dependencies.db import get_db
from services.user_service import create_user, get_user
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/register",
    response_model=User,
    description="Register a new user with a unique username and email address.",
    responses={
        200: {
            "description": "User successfully registered.",
            "content": {
                "application/json": {
                    "example": {
                        "username": "johndoe",
                        "email": "johndoe@example.com",
                        "full_name": "John Doe",
                        "disabled": False,
                    }
                }
            },
        },
        400: {
            "description": "Username already registered.",
            "content": {
                "application/json": {
                    "example": {"detail": "Username already registered"}
                }
            },
        },
    },
)
def register(user: UserCreate, db: Session = Depends(get_db)):
    logger.info("Attempting to register user: %s", user.username)
    db_user = get_user(db, user.username)
    if db_user:
        logger.error("Username already registered: %s", user.username)
        raise HTTPException(status_code=400, detail="Username already registered")
    new_user = create_user(db, user)
    logger.info("User registered successfully: %s", new_user.username)
    return new_user

