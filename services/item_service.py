from sqlalchemy.orm import Session
from models import Item as DBItem
from schemas.item import Item, ItemUpdate
from fastapi import HTTPException


def add_item_service(db: Session, item: Item):
    new_item = DBItem(**item.dict())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item


def get_item_by_id_service(db: Session, item_id: int):
    db_item = db.query(DBItem).filter(DBItem.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail=f"Item with id={item_id} not found")
    return db_item


def update_item_service(db: Session, item_id: int, item: ItemUpdate):
    db_item = db.query(DBItem).filter(DBItem.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail=f"Item with id={item_id} not found")
    update_data = item.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item


def delete_item_service(db: Session, item_id: int):
    db_item = db.query(DBItem).filter(DBItem.id == item_id).first()
    if not db_item:
        raise HTTPException(
            status_code=404, detail=f"Item with id={item_id} does not exist"
        )
    db.delete(db_item)
    db.commit()
    return db_item
