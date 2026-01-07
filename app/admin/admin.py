import os
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.model.user import User
from app.core.auth import hashed_password

def create_default_admin():
    db: Session = SessionLocal()

    try:
        admin = db.query(User).filter(User.role == "admin").first()
        if admin:
            return

        username = os.getenv("ADMIN_USERNAME")
        email = os.getenv("ADMIN_EMAIL")
        password = os.getenv("ADMIN_PASSWORD")

        if not username or not email or not password:
            raise RuntimeError("Admin credentials are not set in .env")

        admin_user = User(
            username=username,
            email=email,
            password=hashed_password(password),
            role="admin"
        )

        db.add(admin_user)
        db.commit()
        print("Admin created from .env")

    finally:
        db.close()
