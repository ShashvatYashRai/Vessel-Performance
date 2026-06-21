import os
from sqlalchemy.orm import Session
from app.database.connection import SessionLocal, engine
from app.models.user import User
from app.services.auth_service import hash_password


def seed_default_admin():
    """Create a default admin account if the users table is empty.
    This function is idempotent and safe to run multiple times.
    """
    # Ensure tables are created (Alembic migrations should have run already)
    # Using a direct session to avoid FastAPI dependencies.
    db: Session = SessionLocal()
    try:
        user_count = db.query(User).count()
        if user_count == 0:
            admin_user = User(
                username=os.getenv("DEFAULT_ADMIN_USERNAME", "admin"),
                email=os.getenv("DEFAULT_ADMIN_EMAIL", "admin@vpro.local"),
                password_hash=hash_password(os.getenv("DEFAULT_ADMIN_PASSWORD", "admin123")),
                role="admin",
            )
            db.add(admin_user)
            db.commit()
            print("Default admin account created.")
        else:
            print("Users table already contains data; no admin seed needed.")
    finally:
        db.close()
