from fastapi import APIRouter, Depends, HTTPException
from schemas.auth import Token
from dependencies.db import get_db
from services.auth_service import authenticate_user, create_access_token
from datetime import timedelta
from config import settings
from fastapi.security import OAuth2PasswordRequestForm
import logging
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/token",
    response_model=Token,
    description="Generate an access token for authentication.",
    responses={
        200: {
            "description": "Access token successfully generated.",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer",
                    }
                }
            },
        },
        401: {
            "description": "Invalid username or password.",
            "content": {
                "application/json": {
                    "example": {"detail": "Incorrect username or password"}
                }
            },
        },
    },
)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    logger.info("Attempting to authenticate user")
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        logger.error("Authentication failed for user: %s", form_data.username)
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    logger.info("User authenticated successfully: %s", user.username)
    return {"access_token": access_token, "token_type": "bearer"}
