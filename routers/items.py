from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated
from dependencies.auth import get_current_active_user, get_current_user
from dependencies.db import get_db
from schemas.item import Item, ItemUpdate
from services.item_service import (
    add_item_service,
    update_item_service,
    get_item_by_id_service,
    delete_item_service,
)
from schemas.user import User

router = APIRouter(tags=["Items"])


@router.post(
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
            "description": "Invalid input data.",
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
    new_item = add_item_service(db, item)
    return {"added": new_item}


@router.get(
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
    db_item = get_item_by_id_service(db, item_id)
    return db_item


@router.put(
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
    updated_item = update_item_service(db, item_id, item)
    return {"updated": updated_item}


@router.delete(
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
    deleted_item = delete_item_service(db, item_id)
    return {"deleted": deleted_item}
