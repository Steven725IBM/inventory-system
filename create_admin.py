from app.database import SessionLocal, engine, Base
from app.models import User
from app.security import hash_password

# Ensure tables exist
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# CHANGE THESE VALUES
USERNAME = "admin"
PASSWORD = "ChangeMeAdmin123"
ROLE = "admin"

existing = db.query(User).filter(User.username == USERNAME).first()
if existing:
    print("Admin user already exists.")
else:
    user = User(
        username=USERNAME,
        password_hash=hash_password(PASSWORD),
        role=ROLE
    )
    db.add(user)
    db.commit()
    print("Admin user created successfully.")

db.close()
