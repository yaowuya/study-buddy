import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_admin
from app.models.admin import Admin
from app.models.user import User
from app.models.family import Family
from app.models.task import Task
from app.schemas.admin import AdminUserOut, AdminUserDetailOut, AdminUserUpdate
from app.schemas.pagination import PaginatedResponse

router = APIRouter(tags=["admin-users"])


@router.get("/", response_model=PaginatedResponse[AdminUserOut])
def list_users(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    phone: str | None = None,
    role: str | None = None,
    is_active: bool | None = None,
    admin: Admin = Depends(require_admin),
    db: Session = Depends(get_db),
):
    query = db.query(User)
    if phone:
        query = query.filter(User.phone.contains(phone))
    if role:
        query = query.filter(User.role == role)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    total = query.count()
    items = query.order_by(User.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return PaginatedResponse(total=total, items=items, page=page, page_size=page_size)


@router.get("/{user_id}", response_model=AdminUserDetailOut)
def get_user(user_id: uuid.UUID, admin: Admin = Depends(require_admin), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    family_code = None
    if user.family_id:
        family = db.query(Family).filter(Family.id == user.family_id).first()
        family_code = family.code if family else None
    task_count = db.query(Task).filter(
        Task.family_id == user.family_id,
        Task.is_deleted == False,
    ).count() if user.family_id else 0
    return AdminUserDetailOut(
        id=user.id, phone=user.phone, role=user.role, family_id=user.family_id,
        is_active=user.is_active, is_deleted=user.is_deleted,
        family_code=family_code, task_count=task_count,
    )


@router.patch("/{user_id}", response_model=AdminUserOut)
def update_user(
    user_id: uuid.UUID,
    body: AdminUserUpdate,
    admin: Admin = Depends(require_admin),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    if body.role is not None:
        user.role = body.role
    if body.is_active is not None:
        user.is_active = body.is_active
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}")
def delete_user(user_id: uuid.UUID, admin: Admin = Depends(require_admin), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    user.is_deleted = True
    db.commit()
    return {"ok": True}
