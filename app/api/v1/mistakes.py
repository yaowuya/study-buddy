import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_parent
from app.models.user import User
from app.crud import task as task_crud
from app.crud import mistake as mistake_crud
from app.schemas.mistake import MistakeOut

router = APIRouter(prefix="/mistakes", tags=["mistakes"])


@router.get("/", response_model=list[MistakeOut])
def list_mistakes(subject: str | None = None, archived: bool | None = None, user: User = Depends(require_parent), db: Session = Depends(get_db)):
    if not user.family_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Not bound to a family")
    return mistake_crud.get_family_mistakes(db, user.family_id, subject, archived)


@router.post("/{mistake_id}/archive", response_model=MistakeOut)
def archive_mistake(mistake_id: uuid.UUID, user: User = Depends(require_parent), db: Session = Depends(get_db)):
    if not user.family_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Not bound to a family")
    mistake = mistake_crud.get_mistake_by_id(db, mistake_id)
    if not mistake:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Mistake not found")
    task = task_crud.get_task_by_id(db, mistake.task_id)
    if not task or task.family_id != user.family_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Mistake not found")
    return mistake_crud.archive_mistake(db, mistake)
