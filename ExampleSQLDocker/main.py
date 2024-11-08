from enum import Enum
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Annotated
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
import jwt
from jwt.exceptions import InvalidTokenError
from database import init_db
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Item as DBItem
from models import Categary
from typing import Optional
from jose import JWTError


app = FastAPI(
    title="ToolShare",
    description="A simple tool sharing application",
    version="0.1"
)

#database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
##Security 

# secret key for JWT
SECRET_KEY = "128efd6b4d377c3e6354d4ccd33ac360bd72bc3e7d119a6f5181d6c9f17f889d"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

#password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
#oauth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")




class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None


fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    }    
}

# class UserInDB(User):
#     hashed_password: str

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return User(**user_dict)
    
# def get_password_hash(password):
#     return pwd_context.hash(password)

#autehnticate user
def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

#create access token
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Login endpoint
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
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

# async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
#     credentials_exception = HTTPException(
#         status_code=401, detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username: str = payload.get("sub")
#         if username is None:
#             raise credentials_exception
#         token_data = TokenData(username=username)
#     except InvalidTokenError:
#         raise credentials_exception
#     user = get_user(fake_users_db, username=token_data.username)
#     if user is None:
#         raise credentials_exception
#     return user
# Get current user
async def get_current_user(token: str = Depends(oauth2_scheme)):
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
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user



async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user




class Categary(Enum):
    TOOLS = "tools"
    SERVICE = "service"

class Item(BaseModel):
    name: str = Field(description="Name of the item", min_length=1)
    description: str | None = None
    price: float = Field(description="Price for borrowing the item")
    id: int = Field(description="Unique identifier for the item")
    categary: Categary = Field(description="Categary of the item")

items = {
    0: Item(name="Hammer", price=12.5, id=0, categary=Categary.TOOLS),
    1: Item(name="Drill", price=3.0, id=1, categary=Categary.TOOLS),
    2: Item(name="Mower", price=10.0, id=2, categary=Categary.TOOLS),
    3: Item(name="Lawn Service", price=20.0, id=3, categary=Categary.SERVICE)
}


        
@app.on_event("startup")
def on_startup():
    init_db()
        
    
# Protect specific endpoints by adding the login requirement
@app.get("/")
def index() -> dict[str, dict[int, Item]]:
    return {"items": items}

# @app.get("/items/{item_id}")
# def get_item_by_id(item_id: int, db: Session = Depends(get_db), current_user: Annotated[User, Depends(get_current_active_user)]) -> Item:
#     if item_id not in items:
#         raise HTTPException(status_code=404, detail=f"Item with {item_id = } not found")
#     return items[item_id]

@app.get("/items/{item_id}")
def get_item_by_id(item_id: int, current_user: Annotated[User, Depends(get_current_active_user)], db: Session = Depends(get_db)) -> Item:
    db_item = db.query(DBItem).filter(DBItem.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail=f"Item with {item_id = } not found")
    return db_item



# @app.post("/")
# def add_item(item: Item, current_user: Annotated[User, Depends(get_current_active_user)]) -> dict[str, Item]:
#     if item.id in items:
#         raise HTTPException(status_code=400, detail=f"Item with {item.id = } already exists")
#     items[item.id] = item
#     return {"added": item}

@app.post("/")
def add_item(item: Item, current_user: Annotated[User, Depends(get_current_active_user)], db: Session = Depends(get_db)) -> dict[str, Item]:
    db_item = db.query(DBItem).filter(DBItem.id == item.id).first()
    if db_item:
        raise HTTPException(status_code=400, detail=f"Item with {item.id = } already exists")
    new_item = DBItem(**item.dict())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return {"added": new_item}


# @app.put("/update/{item_id}")
# def update_item(item_id: int,
#     current_user: Annotated[User, Depends(get_current_active_user)], 
#     name: str | None = None,
#     description: str | None = None,
#     price: float | None = None,
#     categary: Categary | None = None
# ) -> dict[str, Item]:
#     if item_id not in items:
#         raise HTTPException(status_code=404, detail=f"Item with {item_id = } not found")
#     item = items[item_id]
#     if name is not None:
#         item.name = name
#     if description is not None:
#         item.description = description
#     if price is not None:
#         item.price = price
#     if categary is not None:
#         item.categary = categary
#     return {"updated": item}

@app.put("/update/{item_id}")
def update_item(item_id: int, current_user: Annotated[User, Depends(get_current_active_user)], db: Session = Depends(get_db), 
    name: str | None = None,
    description: str | None = None,
    price: float | None = None,
    categary: Categary | None = None
) -> dict[str, Item]:
    db_item = db.query(DBItem).filter(DBItem.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail=f"Item with {item_id = } not found")
    if name is not None:
        db_item.name = name
    if description is not None:
        db_item.description = description
    if price is not None:
        db_item.price = price
    if categary is not None:
        db_item.categary = categary
    db.commit()
    db.refresh(db_item)
    return {"updated": db_item}

# @app.delete("/delete/{item_id}")
# def delete_item(item_id: int, current_user: Annotated[User, Depends(get_current_active_user)]) -> dict[str, Item]:
#     if item_id not in items:
#         raise HTTPException(status_code=404, detail=f"Item with {item_id = } does not exist")
#     item = items.pop(item_id)
#     return {"deleted": item}

@app.delete("/delete/{item_id}")
def delete_item(item_id: int, current_user: Annotated[User, Depends(get_current_active_user)], db: Session = Depends(get_db)) -> dict[str, Item]:
    db_item = db.query(DBItem).filter(DBItem.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail=f"Item with {item_id = } does not exist")
    db.delete(db_item)
    db.commit()
    return {"deleted": db_item}

# Authentication endpoints
@app.post("/token")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401, detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return Token(access_token=access_token, token_type="bearer")

@app.get("/users/me/", response_model=User)
async def read_users_me(current_user: Annotated[User, Depends(get_current_active_user)]):
    return current_user
