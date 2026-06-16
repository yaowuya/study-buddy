import uuid
from datetime import date

from sqlalchemy.orm import Session

from app.models.task import Task, TaskStatus


def create_task(db: Session, family_id: uuid.UUID, **kwargs) -> Task:
    task = Task(family_id=family_id, **kwargs)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def get_family_tasks_by_date(db: Session, family_id: uuid.UUID, date_from: date | None = None, date_to: date | None = None) -> list[Task]:
    query = db.query(Task).filter(Task.family_id == family_id, Task.is_deleted == False)
    if date_from:
        query = query.filter(Task.date >= date_from)
    if date_to:
        query = query.filter(Task.date <= date_to)
    return query.order_by(Task.date.desc()).all()


def get_task_by_id(db: Session, task_id: uuid.UUID) -> Task | None:
    return db.query(Task).filter(Task.id == task_id, Task.is_deleted == False).first()


def update_task_status(db: Session, task: Task, status: TaskStatus) -> Task:
    task.status = status
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task: Task) -> None:
    db.delete(task)
    db.commit()


def update_task(db: Session, task: Task, **kwargs) -> Task:
    for key, value in kwargs.items():
        if value is not None and hasattr(task, key):
            setattr(task, key, value)
    db.commit()
    db.refresh(task)
    return task
