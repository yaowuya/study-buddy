import uuid

from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.core.security import hash_password


def get_user_by_phone(db: Session, phone: str) -> User | None:
    return db.query(User).filter(User.phone == phone, User.is_deleted == False).first()


def get_user_by_id(db: Session, user_id: uuid.UUID) -> User | None:
    return db.query(User).filter(
        User.id == user_id,
        User.is_deleted == False,
        User.is_active == True,
    ).first()


def create_user(db: Session, phone: str, password: str, role: UserRole) -> User:
    user = User(phone=phone, hashed_password=hash_password(password), role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user_family(db: Session, user: User, family_id: uuid.UUID) -> User:
    user.family_id = family_id
    db.commit()
    db.refresh(user)
    return user
