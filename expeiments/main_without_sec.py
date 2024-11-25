from enum import Enum
from fastapi import FastAPI
from pydantic import BaseModel, Field
from fastapi import HTTPException


app = FastAPI(
    title="ToolShare", description="A simple tool sharing application", version="0.1"
)


class Categary(Enum):
    """ "Catefories of items"""

    TOOLS = "tools"
    SERVICE = "service"


class Item(BaseModel):
    """Item model"""

    name: str = Field(description="Name of the item", min_length=1)
    description: str | None = None
    price: float = Field(description="Price for borrowing the item")
    id: int = Field(description="Unique identifier for the item")
    categary: Categary = Field(description="Categary of the item")


items = {
    0: Item(name="Hammmer", price=12.5, id=0, categary=Categary.TOOLS),
    1: Item(name="Drill", price=3.0, id=1, categary=Categary.TOOLS),
    2: Item(name="Mower", price=10.0, id=2, categary=Categary.TOOLS),
    3: Item(name="Lawn Service", price=20.0, id=3, categary=Categary.SERVICE),
}


# Get application root


@app.get("/")
def index() -> dict[str, dict[int, Item]]:
    return {"items": items}


@app.get("/items/{item_id}")
def get_item_by_id(item_id: int) -> Item:
    if item_id not in items:
        raise HTTPException(status_code=404, detail=f"Item with {item_id = } not found")
    return items[item_id]


Selection = dict[str, str | int | float | Categary | None]


# Get items by parameters
@app.get("/items")
def show_item_by_parameters(
    name: str | None = None,
    description: str | None = None,
    price: float | None = None,
    categary: Categary | None = None,
) -> dict[str, Selection | list[Item]]:
    def check_item(item: Item):
        return all(
            (
                name is None or item.name == name,
                description is None or item.description == description,
                price is None or item.price == price,
                categary is None or item.categary == categary,
            )
        )

    selection = [item for item in items.values() if check_item(item)]
    return {
        "query": {
            "name": name,
            "description": description,
            "price": price,
            "categary": categary,
        },
        "selection": selection,
    }


# Add item


@app.post("/")
def add_item(item: Item) -> dict[str, Item]:

    if item.id in items:
        HTTPException(status_code=400, detail=f"Item with {item.id = } already exists")

    items[item.id] = item
    return {"added": item}


# Update item


@app.put("/update/{item_id}")
def update(
    item_id: int,
    name: str | None = None,
    description: str | None = None,
    price: float | None = None,
    categary: Categary | None = None,
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


# Delete item


@app.delete("/delete/{item_id}")
def delete(item_id: int) -> dict[str, Item]:
    if item_id not in items:
        raise HTTPException(
            status_code=404, detail=f"Item with {item_id = } does not exist"
        )

    item = items.pop(item_id)
    return {"deleted": item}
