import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.crud import task as task_crud
from app.crud import dictation_item as dictation_crud
from app.schemas.dictation_item import DictationItemBatch, DictationItemOut

router = APIRouter(prefix="/dictation", tags=["dictation"])


def _get_family_task(db: Session, task_id: uuid.UUID, user: User):
    if not user.family_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Not bound to a family")
    task = task_crud.get_task_by_id(db, task_id)
    if not task or task.family_id != user.family_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Task not found")
    return task


@router.post("/", response_model=list[DictationItemOut])
def create_dictation_items(body: DictationItemBatch, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _get_family_task(db, body.task_id, user)
    return dictation_crud.create_items(db, body.task_id, [i.model_dump() for i in body.items])


@router.get("/{task_id}", response_model=list[DictationItemOut])
def get_dictation_items(task_id: uuid.UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _get_family_task(db, task_id, user)
    return dictation_crud.get_items_by_task(db, task_id)


@router.delete("/{task_id}")
def delete_dictation_items(task_id: uuid.UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _get_family_task(db, task_id, user)
    dictation_crud.delete_items_by_task(db, task_id)
    return {"ok": True}
