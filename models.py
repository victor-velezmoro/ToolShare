from enum import Enum
from sqlalchemy import Column, Integer, String, Float, Enum as SqlEnum
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Category(Enum):
    TOOLS = "tools"
    SERVICE = "service"


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True, nullable=True)
    price = Column(Float)
    category = Column(SqlEnum(Category))


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String)
    disabled = Column(String)
