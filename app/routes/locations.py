from fastapi import APIRouter, Form, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import SessionLocal
from app.models import Location, Inventory

router = APIRouter()


# =========================
# LIST LOCATIONS
# =========================
@router.get("/locations", summary="List Locations")
def list_locations():
    db: Session = SessionLocal()
    locations = db.query(Location).all()
    db.close()
    return locations


# =========================
# CREATE LOCATION
# =========================
@router.post("/locations", summary="Create Location")
def create_location(
    name: str = Form(...)
):
    db: Session = SessionLocal()

    normalized_name = name.strip()

    location = Location(
        name=normalized_name
    )

    db.add(location)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        db.close()
        raise HTTPException(
            status_code=400,
            detail=f"Location '{normalized_name}' already exists."
        )

    db.close()
    return location


# =========================
# UPDATE LOCATION
# =========================
@router.put("/locations/{location_id}", summary="Update Location")
def update_location(
    location_id: int,
    name: str = Form(...)
):
    db: Session = SessionLocal()

    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        db.close()
        raise HTTPException(status_code=404, detail="Location not found")

    location.name = name.strip()

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        db.close()
        raise HTTPException(
            status_code=400,
            detail="Another location with this name already exists."
        )

    db.close()
    return location


# =========================
# DELETE LOCATION (SAFE)
# =========================
@router.delete("/locations/{location_id}", summary="Delete Location")
def delete_location(location_id: int):
    db: Session = SessionLocal()

    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        db.close()
        raise HTTPException(status_code=404, detail="Location not found")

    # 🔒 Safety check: prevent deleting locations with inventory
    inventory_exists = (
        db.query(Inventory)
        .filter(Inventory.location_id == location_id)
        .first()
    )

    if inventory_exists:
        db.close()
        raise HTTPException(
            status_code=400,
            detail="Cannot delete location with existing inventory."
        )

    db.delete(location)
    db.commit()
    db.close()

    return {"message": "Location deleted successfully"}
