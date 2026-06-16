import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_admin
from app.models.admin import Admin
from app.models.family import Family
from app.models.user import User
from app.schemas.admin import AdminFamilyOut, AdminFamilyDetailOut, AdminUserOut
from app.schemas.pagination import PaginatedResponse

router = APIRouter(tags=["admin-families"])


@router.get("/", response_model=PaginatedResponse[AdminFamilyOut])
def list_families(
    page: int = 1,
    page_size: int = 20,
    code: str | None = None,
    admin: Admin = Depends(require_admin),
    db: Session = Depends(get_db),
):
    query = db.query(Family)
    if code:
        query = query.filter(Family.code.contains(code))
    total = query.count()
    families = query.order_by(Family.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    items = []
    for f in families:
        member_count = db.query(User).filter(User.family_id == f.id).count()
        items.append(AdminFamilyOut(id=f.id, code=f.code, member_count=member_count, is_deleted=f.is_deleted))
    return PaginatedResponse(total=total, items=items, page=page, page_size=page_size)


@router.get("/{family_id}", response_model=AdminFamilyDetailOut)
def get_family(family_id: uuid.UUID, admin: Admin = Depends(require_admin), db: Session = Depends(get_db)):
    family = db.query(Family).filter(Family.id == family_id).first()
    if not family:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Family not found")
    members = db.query(User).filter(User.family_id == family_id).all()
    member_outs = [
        AdminUserOut(id=m.id, phone=m.phone, role=m.role, family_id=m.family_id, is_active=m.is_active, is_deleted=m.is_deleted)
        for m in members
    ]
    return AdminFamilyDetailOut(
        id=family.id, code=family.code, member_count=len(members),
        is_deleted=family.is_deleted, members=member_outs,
    )


@router.delete("/{family_id}")
def delete_family(family_id: uuid.UUID, admin: Admin = Depends(require_admin), db: Session = Depends(get_db)):
    family = db.query(Family).filter(Family.id == family_id).first()
    if not family:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Family not found")
    family.is_deleted = True
    db.commit()
    return {"ok": True}
