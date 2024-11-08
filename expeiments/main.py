from enum import Enum
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Annotated
from .auth import get_current_active_user, User

# FastAPI app
app = FastAPI(
    title="ToolShare",
    description="A simple tool sharing application",
    version="0.1"
)

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

# Protect specific endpoints by adding the login requirement
@app.get("/")
def index() -> dict[str, dict[int, Item]]:
    return {"items": items}

@app.get("/items/{item_id}")
def get_item_by_id(item_id: int, current_user: Annotated[User, Depends(get_current_active_user)]) -> Item:
    if item_id not in items:
        raise HTTPException(status_code=404, detail=f"Item with {item_id = } not found")
    return items[item_id]

@app.post("/")
def add_item(item: Item, current_user: Annotated[User, Depends(get_current_active_user)]) -> dict[str, Item]:
    if item.id in items:
        raise HTTPException(status_code=400, detail=f"Item with {item.id = } already exists")
    items[item.id] = item
    return {"added": item}

@app.put("/update/{item_id}")
def update_item(item_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)], 
    name: str | None = None,
    description: str | None = None,
    price: float | None = None,
    categary: Categary | None = None
) -> dict[str, Item]:
    if item_id not in items:
        raise HTTPException(status_code=404, detail=f"Item with {item_id = } not found")
    item = items[item_id]
    if name is not None:
        item.name = name
    if description is not None:
        item.description = description
    if price is not None:
        item.price = price
    if categary is not None:
        item.categary = categary
    return {"updated": item}

@app.delete("/delete/{item_id}")
def delete_item(item_id: int, current_user: Annotated[User, Depends(get_current_active_user)]) -> dict[str, Item]:
    if item_id not in items:
        raise HTTPException(status_code=404, detail=f"Item with {item_id = } does not exist")
    item = items.pop(item_id)
    return {"deleted": item}