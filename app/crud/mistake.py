import uuid

from sqlalchemy.orm import Session

from app.models.mistake import Mistake
from app.models.task import Task


def create_mistake(db: Session, task_id: uuid.UUID, subject: str | None) -> Mistake:
    mistake = Mistake(task_id=task_id, subject=subject)
    db.add(mistake)
    db.commit()
    db.refresh(mistake)
    return mistake


def get_family_mistakes(db: Session, family_id: uuid.UUID, subject: str | None = None, archived: bool | None = None) -> list[Mistake]:
    q = db.query(Mistake).join(Task, Mistake.task_id == Task.id).filter(Task.family_id == family_id)
    if subject:
        q = q.filter(Mistake.subject == subject)
    if archived is not None:
        q = q.filter(Mistake.archived == archived)
    return q.order_by(Mistake.id.desc()).all()


def archive_mistake(db: Session, mistake: Mistake) -> Mistake:
    mistake.archived = True
    db.commit()
    db.refresh(mistake)
    return mistake


def get_mistake_by_id(db: Session, mistake_id: uuid.UUID) -> Mistake | None:
    return db.query(Mistake).filter(Mistake.id == mistake_id).first()
