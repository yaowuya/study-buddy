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


def get_family_tasks_by_date(db: Session, family_id: uuid.UUID, task_date: date) -> list[Task]:
    return db.query(Task).filter(Task.family_id == family_id, Task.date == task_date).order_by(Task.date).all()


def get_task_by_id(db: Session, task_id: uuid.UUID) -> Task | None:
    return db.query(Task).filter(Task.id == task_id).first()


def update_task_status(db: Session, task: Task, status: TaskStatus) -> Task:
    task.status = status
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task: Task) -> None:
    db.delete(task)
    db.commit()
