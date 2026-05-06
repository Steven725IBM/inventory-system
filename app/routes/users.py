from fastapi import APIRouter, Form, Depends, Request, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import User
from app.security import hash_password
from app.auth import require_login

router = APIRouter()


# =========================
# CREATE USER (ADMIN ONLY)
# =========================
@router.post("/users/create")
def create_user(
    request: Request,
    user = Depends(require_login),
    username: str = Form(...),
    password: str = Form(...),
    role: str = Form(...)
):
    # ✅ Only admins can create users
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    db: Session = SessionLocal()

    existing = db.query(User).filter(User.username == username).first()
    if existing:
        db.close()
        raise HTTPException(status_code=400, detail="Username already exists")

    new_user = User(
        username=username,
        password_hash=hash_password(password),
        role=role
    )

    db.add(new_user)
    db.commit()
    db.close()

    return {"message": f"User '{username}' created successfully"}
