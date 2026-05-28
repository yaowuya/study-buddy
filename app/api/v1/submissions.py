import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user, require_parent
from app.models.user import User
from app.models.task import Task, TaskStatus
from app.models.submission import Submission
from app.crud import task as task_crud
from app.crud import submission as submission_crud
from app.crud import mistake as mistake_crud
from app.schemas.submission import SubmissionCreate, SubmissionGrade, SubmissionOut

router = APIRouter(prefix="/submissions", tags=["submissions"])


def _get_family_task(db: Session, task_id: uuid.UUID, user: User):
    if not user.family_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Not bound to a family")
    task = task_crud.get_task_by_id(db, task_id)
    if not task or task.family_id != user.family_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Task not found")
    return task


@router.get("/", response_model=list[SubmissionOut])
def list_submissions(task_id: uuid.UUID | None = None, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user.family_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Not bound to a family")
    q = db.query(Submission).join(Task, Submission.task_id == Task.id).filter(Task.family_id == user.family_id)
    if task_id:
        q = q.filter(Submission.task_id == task_id)
    return q.all()


@router.post("/", response_model=SubmissionOut)
def submit_task(body: SubmissionCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    task = _get_family_task(db, body.task_id, user)
    if task.status == TaskStatus.GRADED:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Task already graded")
    existing = submission_crud.get_submission_by_task(db, body.task_id)
    if existing:
        return existing  # 已有 submission 直接返回，幂等处理
    sub = submission_crud.create_submission(db, body.task_id)
    task_crud.update_task_status(db, task, TaskStatus.SUBMITTED)
    return sub


@router.post("/{submission_id}/grade", response_model=SubmissionOut)
def grade_submission(submission_id: uuid.UUID, body: SubmissionGrade, user: User = Depends(require_parent), db: Session = Depends(get_db)):
    sub = submission_crud.get_submission_by_id(db, submission_id)
    if not sub:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Submission not found")
    task = task_crud.get_task_by_id(db, sub.task_id)
    if not task or task.family_id != user.family_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Submission not found")
    sub = submission_crud.grade_submission(db, sub, body.is_correct, body.comment)
    task_crud.update_task_status(db, task, TaskStatus.GRADED)
    if not body.is_correct:
        mistake_crud.create_mistake(db, task.id, task.subject)
    return sub
