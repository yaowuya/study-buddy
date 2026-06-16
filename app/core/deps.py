import uuid

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.user import User, UserRole
from app.models.admin import Admin
from app.core.security import decode_access_token
from app.crud.user import get_user_by_id


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    authorization = request.headers.get("Authorization")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing token")
    token = authorization.removeprefix("Bearer ")
    user_id = decode_access_token(token)
    if not user_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")
    # admin token 以 "admin:" 前缀，不允许访问用户端接口
    if user_id.startswith("admin:"):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Admin token cannot access user endpoints")
    user = get_user_by_id(db, uuid.UUID(user_id))
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found")
    return user


def require_parent(user: User = Depends(get_current_user)) -> User:
    if user.role != UserRole.PARENT:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Parent access required")
    return user


def require_student(user: User = Depends(get_current_user)) -> User:
    if user.role != UserRole.STUDENT:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Student access required")
    return user


def require_admin(request: Request, db: Session = Depends(get_db)) -> Admin:
    authorization = request.headers.get("Authorization")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing token")
    token = authorization.removeprefix("Bearer ")
    payload = decode_access_token(token)
    if not payload or not payload.startswith("admin:"):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Admin access required")
    try:
        admin_id = uuid.UUID(payload.removeprefix("admin:"))
    except ValueError:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Admin access required")
    admin = db.query(Admin).filter(Admin.id == admin_id, Admin.is_active == True).first()
    if not admin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Admin not found or inactive")
    return admin
