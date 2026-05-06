from fastapi import APIRouter, Form, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Inventory, InventoryTransaction
from app.auth import require_login

router = APIRouter()


# =========================
# RECEIVE INVENTORY (PROTECTED)
# =========================
@router.post("/inventory/receive")
def receive_inventory(
    item_id: int = Form(...),
    location_id: int = Form(...),
    quantity: int = Form(...),
    request: Request = None,
    user = Depends(require_login),
):
    db: Session = SessionLocal()

    record = (
        db.query(Inventory)
        .filter_by(item_id=item_id, location_id=location_id)
        .first()
    )

    if record:
        record.quantity += quantity
    else:
        record = Inventory(
            item_id=item_id,
            location_id=location_id,
            quantity=quantity
        )
        db.add(record)

    db.add(
        InventoryTransaction(
            item_id=item_id,
            location_id=location_id,
            change=quantity,
            note=f"Received by {user.username}"
        )
    )

    db.commit()
    db.close()

    return RedirectResponse("/", status_code=303)


# =========================
# ISSUE INVENTORY (PROTECTED)
# =========================
@router.post("/inventory/issue")
def issue_inventory(
    item_id: int = Form(...),
    location_id: int = Form(...),
    quantity: int = Form(...),
    note: str = Form(""),
    request: Request = None,
    user = Depends(require_login),
):
    db: Session = SessionLocal()

    record = (
        db.query(Inventory)
        .filter_by(item_id=item_id, location_id=location_id)
        .first()
    )

    if not record or record.quantity < quantity:
        db.close()
        raise HTTPException(status_code=400, detail="Not enough inventory")

    record.quantity -= quantity

    db.add(
        InventoryTransaction(
            item_id=item_id,
            location_id=location_id,
            change=-quantity,
            note=f"{note} (issued by {user.username})"
        )
    )

    db.commit()
    db.close()

    return RedirectResponse("/", status_code=303)


# =========================
# UPDATE INVENTORY NOTE (PROTECTED)
# =========================
@router.put("/inventory/history/{transaction_id}/note")
def update_inventory_note(
    transaction_id: int,
    note: str = Form(...),
    request: Request = None,
    user = Depends(require_login),
):
    db: Session = SessionLocal()

    tx = db.query(InventoryTransaction).filter(
        InventoryTransaction.id == transaction_id
    ).first()

    if not tx:
        db.close()
        raise HTTPException(status_code=404, detail="Transaction not found")

    tx.note = f"{note} (edited by {user.username})"
    db.commit()
    db.close()

    return {"success": True}


# =========================
# DELETE INVENTORY RECORD (PROTECTED)
# =========================
@router.delete("/inventory/{inventory_id}")
def delete_inventory(
    inventory_id: int,
    request: Request = None,
    user = Depends(require_login),
):
    db: Session = SessionLocal()

    record = db.query(Inventory).filter(
        Inventory.id == inventory_id
    ).first()

    if not record:
        db.close()
        raise HTTPException(status_code=404, detail="Inventory not found")

    if record.quantity != 0:
        db.close()
        raise HTTPException(
            status_code=400,
            detail="Inventory must be zero before deletion"
        )

    db.delete(record)
    db.commit()
    db.close()

    return {"message": "Inventory record deleted"}
