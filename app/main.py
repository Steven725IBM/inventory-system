from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from app.database import Base, engine, SessionLocal
from app import models
from app.auth import get_current_user

# Routers
from app.routes.auth import router as auth_router
from app.routes.inventory import router as inventory_router
from app.routes.items import router as items_router
from app.routes.locations import router as locations_router
from app.routes.users import router as users_router  # ✅ for creating users


# =========================
# CREATE APP
# =========================
app = FastAPI()


# =========================
# SESSION MIDDLEWARE
# =========================
app.add_middleware(
    SessionMiddleware,
    secret_key="iod_inventory_super_secret_key_12345"
)


# =========================
# DATABASE INIT
# =========================
Base.metadata.create_all(bind=engine)


# =========================
# TEMPLATE SETUP
# =========================
templates = Jinja2Templates(directory="app/templates")


# =========================
# HOME PAGE (MAIN DASHBOARD)
# =========================
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    db = SessionLocal()

    # ✅ THIS is what tells the UI if you're logged in
    current_user = get_current_user(request)

    items = db.query(models.Item).all()
    locations = db.query(models.Location).all()

    inventory_rows = (
        db.query(models.Inventory, models.Item, models.Location)
        .join(models.Item, models.Inventory.item_id == models.Item.id)
        .join(models.Location, models.Inventory.location_id == models.Location.id)
        .all()
    )

    history_rows = (
        db.query(
            models.InventoryTransaction,
            models.Item,
            models.Location,
        )
        .join(
            models.Item,
            models.InventoryTransaction.item_id == models.Item.id,
        )
        .join(
            models.Location,
            models.InventoryTransaction.location_id == models.Location.id,
        )
        .order_by(models.InventoryTransaction.created_at.desc())
        .all()
    )

    db.close()

    context = {
        "request": request,
        "current_user": current_user,   # ✅ REQUIRED FOR LOGIN STATE
        "items": items,
        "locations": locations,
        "inventory_rows": inventory_rows,
        "history_rows": history_rows,
    }

    # ✅ Manual render — avoids your earlier TemplateResponse bug
    html = templates.get_template("index.html").render(context)
    return HTMLResponse(html)


# =========================
# REGISTER ROUTERS
# =========================
app.include_router(auth_router)
app.include_router(inventory_router)
app.include_router(items_router)
app.include_router(locations_router)
app.include_router(users_router)
