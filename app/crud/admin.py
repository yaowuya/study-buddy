import uuid

from sqlalchemy.orm import Session

from app.models.admin import Admin
from app.core.security import hash_password


def get_admin_by_username(db: Session, username: str) -> Admin | None:
    return db.query(Admin).filter(Admin.username == username).first()


def get_admin_by_id(db: Session, admin_id: uuid.UUID) -> Admin | None:
    return db.query(Admin).filter(Admin.id == admin_id).first()


def seed_admin(db: Session) -> None:
    """幂等插入默认管理员"""
    if not db.query(Admin).first():
        admin = Admin(username="admin", hashed_password=hash_password("admin123"))
        db.add(admin)
        db.commit()


def update_admin_password(db: Session, admin: Admin, new_hashed_password: str) -> Admin:
    admin.hashed_password = new_hashed_password
    db.commit()
    db.refresh(admin)
    return admin
