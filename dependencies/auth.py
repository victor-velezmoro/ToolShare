from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from config import settings
from schemas.auth import TokenData
from services.auth_service import get_user
from dependencies.db import get_db
from models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

SECRET_KEY = settings.secret_key
ALGORITHM = "HS256"


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    current_user.disabled = False
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
