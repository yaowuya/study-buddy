import uuid

from sqlalchemy.orm import Session

from app.models.dictation_item import DictationItem


def create_items(db: Session, task_id: uuid.UUID, items: list[dict]) -> list[DictationItem]:
    created = []
    for item_data in items:
        item = DictationItem(task_id=task_id, **item_data)
        db.add(item)
        created.append(item)
    db.commit()
    for item in created:
        db.refresh(item)
    return created


def get_items_by_task(db: Session, task_id: uuid.UUID) -> list[DictationItem]:
    return db.query(DictationItem).filter(DictationItem.task_id == task_id).order_by(DictationItem.id).all()


def delete_items_by_task(db: Session, task_id: uuid.UUID) -> None:
    db.query(DictationItem).filter(DictationItem.task_id == task_id).delete()
    db.commit()
