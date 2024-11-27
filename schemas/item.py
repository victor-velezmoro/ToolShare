from pydantic import BaseModel, Field
from typing import Optional
from models import Category


class Item(BaseModel):
    name: str = Field(description="Name of the item", min_length=1)
    description: Optional[str] = None
    price: float = Field(description="Price for borrowing the item")
    category: Category = Field(description="Category of the item")


class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[Category] = None
