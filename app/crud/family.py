import random
import string
import uuid

from sqlalchemy.orm import Session

from app.models.family import Family


def _generate_code() -> str:
    return "".join(random.choices(string.digits, k=6))


def create_family(db: Session) -> Family:
    code = _generate_code()
    while db.query(Family).filter(Family.code == code).first():
        code = _generate_code()
    family = Family(code=code)
    db.add(family)
    db.commit()
    db.refresh(family)
    return family


def get_family_by_code(db: Session, code: str) -> Family | None:
    return db.query(Family).filter(Family.code == code, Family.is_deleted == False).first()


def get_family_by_id(db: Session, family_id: uuid.UUID) -> Family | None:
    return db.query(Family).filter(Family.id == family_id, Family.is_deleted == False).first()
