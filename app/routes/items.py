from fastapi import APIRouter, Form, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import SessionLocal
from app.models import Item, Inventory

router = APIRouter()


# =========================
# LIST ITEMS
# =========================
@router.get("/items", summary="List Items")
def list_items():
    db: Session = SessionLocal()
    items = db.query(Item).all()
    db.close()
    return items


# =========================
# CREATE ITEM
# =========================
@router.post("/items", summary="Create Item")
def create_item(
    name: str = Form(...),
    category: str = Form(""),
    part_number: str = Form(""),
    min_quantity: int = Form(0)
):
    db: Session = SessionLocal()

    name = name.strip()
    item = Item(
        name=name,
        category=category,
        part_number=part_number,
        min_quantity=min_quantity
    )

    db.add(item)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        db.close()
        raise HTTPException(
            status_code=400,
            detail=f"Item '{name}' already exists."
        )

    db.close()
    return item


# =========================
# UPDATE ITEM
# =========================
@router.put("/items/{item_id}", summary="Update Item")
def update_item(
    item_id: int,
    name: str = Form(...),
    category: str = Form(""),
    part_number: str = Form(""),
    min_quantity: int = Form(0)
):
    db: Session = SessionLocal()

    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        db.close()
        raise HTTPException(status_code=404, detail="Item not found")

    item.name = name.strip()
    item.category = category
    item.part_number = part_number
    item.min_quantity = min_quantity

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        db.close()
        raise HTTPException(
            status_code=400,
            detail="Another item with this name already exists."
        )

    db.close()
    return item


# =========================
# DELETE ITEM (SAFE)
# =========================
@router.delete("/items/{item_id}", summary="Delete Item")
def delete_item(item_id: int):
    db: Session = SessionLocal()

    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        db.close()
        raise HTTPException(status_code=404, detail="Item not found")

    # 🔒 Safety check: prevent deleting items with inventory
    inventory_exists = (
        db.query(Inventory)
        .filter(Inventory.item_id == item_id)
        .first()
    )

    if inventory_exists:
        db.close()
        raise HTTPException(
            status_code=400,
            detail="Cannot delete item with existing inventory."
        )

    db.delete(item)
    db.commit()
    db.close()

    return {"message": "Item deleted successfully"}
