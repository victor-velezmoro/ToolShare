import sqlalchemy as _sql 
import sqlalchemy.ext.declarative as _declarative
import sqlalchemy.orm as _orm
from sqlalchemy.orm import sessionmaker
from models import Base, Item, User
import os

# #DATABASE_URL = "postgresql://myuser:password@localhost/fastapi_database"
# DATABASE_URL = "postgresql://myuser:password@localhost:5432/fastapi_database"
# engine = _sql.create_engine(DATABASE_URL, echo = True)
# SessionLocal = _orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)

# def init_db():
#     Base.metadata.create_all(bind=engine)


# Use the DATABASE_URL from the environment variable if it exists
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://myuser:password@localhost:5432/fastapi_database")
engine = _sql.create_engine(DATABASE_URL, echo=True)
SessionLocal = _orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
