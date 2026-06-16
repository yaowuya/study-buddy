from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_admin
from app.core.security import verify_password, create_access_token, hash_password
from app.models.admin import Admin
from app.crud import admin as admin_crud
from app.schemas.admin import AdminLogin, AdminOut, AdminPasswordChange
from app.schemas.token import Token

router = APIRouter(tags=["admin-auth"])


@router.post("/login", response_model=Token)
def admin_login(body: AdminLogin, db: Session = Depends(get_db)):
    admin = admin_crud.get_admin_by_username(db, body.username)
    if not admin or not verify_password(body.password, admin.hashed_password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")
    if not admin.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Admin account disabled")
    token = create_access_token(f"admin:{admin.id}")
    return Token(access_token=token)


@router.get("/me", response_model=AdminOut)
def admin_me(admin: Admin = Depends(require_admin)):
    return admin


@router.patch("/password")
def admin_change_password(
    body: AdminPasswordChange,
    admin: Admin = Depends(require_admin),
    db: Session = Depends(get_db),
):
    if not verify_password(body.old_password, admin.hashed_password):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Old password is incorrect")
    admin_crud.update_admin_password(db, admin, hash_password(body.new_password))
    return {"ok": True}
