from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from app.database import Base


# =========================
# ITEMS
# =========================
class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    category = Column(String)
    part_number = Column(String)
    min_quantity = Column(Integer, default=0)


# =========================
# LOCATIONS
# =========================
class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)


# =========================
# CURRENT INVENTORY
# =========================
class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, nullable=False)
    location_id = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)


# =========================
# INVENTORY HISTORY / TRANSACTIONS
# =========================
class InventoryTransaction(Base):
    __tablename__ = "inventory_transactions"

    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, nullable=False)
    location_id = Column(Integer, nullable=False)
    change = Column(Integer, nullable=False)
    note = Column(String)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )


# =========================
# USERS (AUTHENTICATION)
# =========================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)  # admin | user | viewer
