from fastapi import FastAPI, HTTPException, Depends, Request
from pydantic import BaseModel, Field
from typing import Annotated, Optional
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from database import init_db, SessionLocal
from models import Item as DBItem, User as DBUser, Category
import logging
from logging.handlers import RotatingFileHandler
from config import settings


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        RotatingFileHandler("app.log", maxBytes=1000000, backupCount=3),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)
logger.info("Test log message to verify file output")


app = FastAPI(
    title="settings.app_name",
    description="A simple tool sharing application",
    version="0.3",
)


# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Security
SECRET_KEY = settings.secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None


class UserInDB(User):
    hashed_password: str


class UserCreate(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    password: str


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db: Session, username: str):
    return db.query(DBUser).filter(DBUser.username == username).first()


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


def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")
    print(f"Middleware triggered for {request.method} {request.url}")
    return response


# @app.post("/token", response_model=Token)
# async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
#     user = authenticate_user(db, form_data.username, form_data.password)
#     if not user:
#         raise HTTPException(
#             status_code=401,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token = create_access_token(
#         data={"sub": user.username}, expires_delta=access_token_expires
#     )
#     return {"access_token": access_token, "token_type": "bearer"}


@app.post(
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
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# @app.post("/register", response_model=User)
# def register(user: UserCreate, db: Session = Depends(get_db)):
#     db_user = get_user(db, user.username)
#     if db_user:
#         raise HTTPException(status_code=400, detail="Username already registered")
#     return create_user(db, user)


@app.post(
    "/register",
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
    db_user = get_user(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return create_user(db, user)


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    # print("Retrieved user:", user)
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


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    print("Current user's disabled status:", current_user.disabled)
    # debug
    current_user.disabled = False
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


class Item(BaseModel):
    name: str = Field(description="Name of the item", min_length=1)
    description: Optional[str] = None
    price: float = Field(description="Price for borrowing the item")
    # id: int = Field(description="Unique identifier for the item")
    category: Category = Field(description="category of the item")


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/")
def index(db: Session = Depends(get_db)) -> dict[str, list[Item]]:
    db_items = db.query(DBItem).all()
    items = [
        Item(**db_item.__dict__)
        for db_item in db_items
        if "_sa_instance_state" not in db_item.__dict__
    ]
    return {"items": items}


@app.get(
    "/items/{item_id}",
    response_model=Item,
    description="Retrieve the details of an item by its unique ID.",
    responses={
        200: {
            "description": "Item found successfully.",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "name": "Hammer",
                        "description": "A tool for hitting nails.",
                        "price": 10.0,
                        "category": "tools",
                    }
                }
            },
        },
        404: {
            "description": "Item not found.",
            "content": {
                "application/json": {"example": {"detail": "Item with id=1 not found"}}
            },
        },
    },
)
def get_item_by_id(
    item_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
) -> Item:
    db_item = db.query(DBItem).filter(DBItem.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail=f"Item with id={item_id} not found")
    return db_item


@app.post(
    "/",
    description="Add a new item to the system. The user must be authenticated.",
    responses={
        200: {
            "description": "Item successfully added.",
            "content": {
                "application/json": {
                    "example": {
                        "added": {
                            "id": 1,
                            "name": "Hammer",
                            "description": "A useful tool for construction.",
                            "price": 10.0,
                            "category": "tools",
                        }
                    }
                }
            },
        },
        400: {
            "description": "Invalid input data or unauthorized access.",
            "content": {
                "application/json": {"example": {"detail": "Invalid input data"}}
            },
        },
    },
)
def add_item(
    item: Item,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> dict[str, Item]:
    """
    Add a new item to the database.

    Parameters:
    - `item`: The item details (name, description, price, category).
    - `current_user`: The authenticated user adding the item.

    Returns:
    - A dictionary containing the added item.
    """
    new_item = DBItem(**item.dict())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return {"added": new_item}


class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[Category] = None


@app.put(
    "/update/{item_id}",
    description="Update the details of an item by its ID. The user must be authenticated.",
    responses={
        200: {
            "description": "Item successfully updated.",
            "content": {
                "application/json": {
                    "example": {
                        "updated": {
                            "id": 1,
                            "name": "Updated Hammer",
                            "description": "An updated description for the hammer.",
                            "price": 15.0,
                            "category": "tools",
                        }
                    }
                }
            },
        },
        404: {
            "description": "Item not found.",
            "content": {
                "application/json": {"example": {"detail": "Item with id=1 not found"}}
            },
        },
    },
)
def update_item(
    item_id: int,
    item: ItemUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
) -> dict[str, Item]:
    db_item = db.query(DBItem).filter(DBItem.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail=f"Item with id={item_id} not found")

    update_data = item.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_item, key, value)

    db.commit()
    db.refresh(db_item)
    return {"updated": db_item}


@app.delete(
    "/delete/{item_id}",
    description="Delete an item by its ID. The user must be authenticated.",
    responses={
        200: {
            "description": "Item successfully deleted.",
            "content": {
                "application/json": {
                    "example": {
                        "deleted": {
                            "id": 1,
                            "name": "Hammer",
                            "description": "A tool for hitting nails.",
                            "price": 10.0,
                            "category": "tools",
                        }
                    }
                }
            },
        },
        404: {
            "description": "Item not found.",
            "content": {
                "application/json": {
                    "example": {"detail": "Item with id=1 does not exist"}
                }
            },
        },
    },
)
def delete_item(
    item_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
) -> dict[str, Item]:
    db_item = db.query(DBItem).filter(DBItem.id == item_id).first()
    if db_item is None:
        raise HTTPException(
            status_code=404, detail=f"Item with id={item_id} does not exist"
        )
    db.delete(db_item)
    db.commit()
    return {"deleted": db_item}


@app.get("/users/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    return current_user
