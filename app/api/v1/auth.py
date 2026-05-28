from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud import user as user_crud
from app.crud import family as family_crud
from app.core.security import verify_password, create_access_token
from app.core.deps import get_db, get_current_user, require_parent, require_student
from app.models.user import User, UserRole
from app.schemas.user import UserRegister, UserLogin, UserOut
from app.schemas.family import FamilyBind, FamilyOut
from app.schemas.token import Token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=Token)
def register(body: UserRegister, db: Session = Depends(get_db)):
    if user_crud.get_user_by_phone(db, body.phone):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Phone already registered")
    user = user_crud.create_user(db, body.phone, body.password, body.role)
    if user.role == UserRole.PARENT:
        family = family_crud.create_family(db)
        user_crud.update_user_family(db, user, family.id)
    token = create_access_token(str(user.id))
    return Token(access_token=token)


@router.post("/login", response_model=Token)
def login(body: UserLogin, db: Session = Depends(get_db)):
    user = user_crud.get_user_by_phone(db, body.phone)
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")
    token = create_access_token(str(user.id))
    return Token(access_token=token)


@router.post("/bind", response_model=FamilyOut)
def bind_family(
    body: FamilyBind,
    user: User = Depends(require_parent),
    db: Session = Depends(get_db),
):
    if user.family_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Already bound to a family")
    family = family_crud.get_family_by_code(db, body.code)
    if not family:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Family code not found")
    user_crud.update_user_family(db, user, family.id)
    return family


@router.post("/student-bind", response_model=FamilyOut)
def student_bind_family(
    body: FamilyBind,
    user: User = Depends(require_student),
    db: Session = Depends(get_db),
):
    if user.family_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Already bound to a family")
    family = family_crud.get_family_by_code(db, body.code)
    if not family:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Family code not found")
    user_crud.update_user_family(db, user, family.id)
    return family


@router.get("/me", response_model=UserOut)
def get_me(user: User = Depends(get_current_user)):
    return user


@router.get("/family", response_model=FamilyOut)
def get_family(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user.family_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Not bound to a family")
    family = family_crud.get_family_by_id(db, user.family_id)
    if not family:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Family not found")
    return family
