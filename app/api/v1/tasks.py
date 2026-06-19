import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user, require_parent
from app.models.user import User
from app.models.task import Task
from app.crud import task as task_crud
from app.schemas.task import TaskCreate, TaskUpdate, TaskUpdateStatus, TaskOut

router = APIRouter(prefix="/tasks", tags=["tasks"])


def _check_family(user: User):
    if not user.family_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Not bound to a family")


def _to_task_out(task: Task) -> TaskOut:
    return TaskOut(
        id=task.id,
        type=task.type,
        title=task.title,
        desc=task.desc,
        duration=task.duration,
        status=task.status,
        date=task.date,
        subject=task.subject,
        has_dictation=len(task.dictation_items) > 0,
    )


@router.post("/", response_model=TaskOut)
def create_task(body: TaskCreate, user: User = Depends(require_parent), db: Session = Depends(get_db)):
    _check_family(user)
    task = task_crud.create_task(db, family_id=user.family_id, **body.model_dump())
    return _to_task_out(task)


@router.get("/", response_model=list[TaskOut])
def list_tasks(
    task_date: date | None = None,          # 精确查询某一天（快捷参数）
    date_from: date | None = None,
    date_to: date | None = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _check_family(user)
    if task_date:
        date_from = date_from or task_date
        date_to = date_to or task_date
    tasks = task_crud.get_family_tasks_by_date(db, user.family_id, date_from, date_to)
    return [_to_task_out(t) for t in tasks]


@router.get("/{task_id}", response_model=TaskOut)
def get_task(task_id: uuid.UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _check_family(user)
    task = task_crud.get_task_by_id(db, task_id)
    if not task or task.family_id != user.family_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Task not found")
    return _to_task_out(task)


@router.patch("/{task_id}", response_model=TaskOut)
def update_task(task_id: uuid.UUID, body: TaskUpdate, user: User = Depends(require_parent), db: Session = Depends(get_db)):
    _check_family(user)
    task = task_crud.get_task_by_id(db, task_id)
    if not task or task.family_id != user.family_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Task not found")
    updated = task_crud.update_task(db, task, **body.model_dump(exclude_unset=True))
    return _to_task_out(updated)


@router.patch("/{task_id}/status", response_model=TaskOut)
def update_status(task_id: uuid.UUID, body: TaskUpdateStatus, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _check_family(user)
    task = task_crud.get_task_by_id(db, task_id)
    if not task or task.family_id != user.family_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Task not found")
    updated = task_crud.update_task_status(db, task, body.status)
    return _to_task_out(updated)


@router.delete("/{task_id}")
def delete_task(task_id: uuid.UUID, user: User = Depends(require_parent), db: Session = Depends(get_db)):
    _check_family(user)
    task = task_crud.get_task_by_id(db, task_id)
    if not task or task.family_id != user.family_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Task not found")
    task_crud.delete_task(db, task)
    return {"ok": True}
