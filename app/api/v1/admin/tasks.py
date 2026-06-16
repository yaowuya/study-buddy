import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_admin
from app.models.admin import Admin
from app.models.task import Task
from app.models.submission import Submission
from app.models.user import User
from app.models.family import Family
from app.schemas.admin import AdminTaskOut, AdminTaskDetailOut, AdminStatsOut
from app.schemas.pagination import PaginatedResponse

router = APIRouter(tags=["admin-tasks"])


@router.get("/stats", response_model=AdminStatsOut)
def get_stats(admin: Admin = Depends(require_admin), db: Session = Depends(get_db)):
    today = date.today()
    total_users = db.query(User).count()
    total_families = db.query(Family).count()
    today_tasks = db.query(Task).filter(Task.date == today).count()
    pending_submissions = db.query(Submission).filter(Submission.is_correct == None).count()
    return AdminStatsOut(
        total_users=total_users,
        total_families=total_families,
        today_tasks=today_tasks,
        pending_submissions=pending_submissions,
    )


@router.get("/", response_model=PaginatedResponse[AdminTaskOut])
def list_tasks(
    page: int = 1,
    page_size: int = 20,
    family_id: uuid.UUID | None = None,
    task_status: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    admin: Admin = Depends(require_admin),
    db: Session = Depends(get_db),
):
    query = db.query(Task)
    if family_id:
        query = query.filter(Task.family_id == family_id)
    if task_status:
        query = query.filter(Task.status == task_status)
    if date_from:
        query = query.filter(Task.date >= date_from)
    if date_to:
        query = query.filter(Task.date <= date_to)
    total = query.count()
    items = query.order_by(Task.date.desc()).offset((page - 1) * page_size).limit(page_size).all()
    out = [
        AdminTaskOut(
            id=t.id, family_id=t.family_id, type=t.type, title=t.title,
            status=t.status, date=str(t.date), subject=t.subject, is_deleted=t.is_deleted,
        )
        for t in items
    ]
    return PaginatedResponse(total=total, items=out, page=page, page_size=page_size)


@router.get("/{task_id}", response_model=AdminTaskDetailOut)
def get_task(task_id: uuid.UUID, admin: Admin = Depends(require_admin), db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Task not found")
    submission_data = None
    if task.submission:
        s = task.submission
        submission_data = {
            "is_correct": s.is_correct,
            "comment": s.comment,
            "submitted_at": s.submitted_at.isoformat(),
        }
    dictation_data = [
        {"content": d.content, "speed": d.speed, "pause_interval": d.pause_interval}
        for d in task.dictation_items
    ]
    return AdminTaskDetailOut(
        id=task.id, family_id=task.family_id, type=task.type, title=task.title,
        status=task.status, date=str(task.date), subject=task.subject, is_deleted=task.is_deleted,
        desc=task.desc, duration=task.duration,
        submission=submission_data, dictation_items=dictation_data,
    )


@router.delete("/{task_id}")
def delete_task(task_id: uuid.UUID, admin: Admin = Depends(require_admin), db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Task not found")
    task.is_deleted = True
    db.commit()
    return {"ok": True}
