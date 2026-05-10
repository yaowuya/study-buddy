# 后端基础与认证 — 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 搭建 FastAPI 后端项目骨架，完成数据库模型、认证 API 和家庭绑定功能。

**Architecture:** FastAPI + SQLAlchemy 2.x + Alembic + PostgreSQL。分层结构：models → schemas → crud → api。JWT 无状态认证。

**Tech Stack:** Python 3.11+, FastAPI, SQLAlchemy 2.x, Alembic, python-jose, passlib, psycopg2-binary

---

## File Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI 入口，挂载路由
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── auth.py         # 注册、登录、绑定
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # 环境变量配置
│   │   ├── security.py         # JWT 创建/验证、密码哈希
│   │   └── deps.py             # 依赖注入（get_current_user, get_db）
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py             # User 模型
│   │   └── family.py           # Family 模型
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py             # User Pydantic schemas
│   │   ├── family.py           # Family Pydantic schemas
│   │   └── token.py            # Token schema
│   ├── crud/
│   │   ├── __init__.py
│   │   ├── user.py             # User CRUD
│   │   └── family.py           # Family CRUD
│   └── database.py             # SQLAlchemy engine/session
├── alembic/
│   ├── env.py
│   └── versions/
├── alembic.ini
├── requirements.txt
└── Dockerfile
```

---

### Task 1: 项目初始化与依赖

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/app/__init__.py`
- Create: `backend/app/main.py`
- Create: `backend/app/database.py`
- Create: `backend/app/core/__init__.py`
- Create: `backend/app/core/config.py`

- [ ] **Step 1: 创建项目目录结构**

```bash
cd D:/01-code/study-buddy
mkdir -p backend/app/api/v1 backend/app/core backend/app/models backend/app/schemas backend/app/crud backend/alembic/versions
```

- [ ] **Step 2: 创建 requirements.txt**

```txt
fastapi==0.115.6
uvicorn[standard]==0.34.0
sqlalchemy==2.0.36
alembic==1.14.0
psycopg2-binary==2.9.10
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
pydantic==2.10.3
pydantic-settings==2.7.0
```

- [ ] **Step 3: 创建 config.py**

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/studybuddy"
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    class Config:
        env_file = ".env"

settings = Settings()
```

- [ ] **Step 4: 创建 database.py**

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass
```

- [ ] **Step 5: 创建 main.py（最小骨架）**

```python
from fastapi import FastAPI

app = FastAPI(title="作业陪伴助手", version="0.1.0")

@app.get("/health")
def health_check():
    return {"status": "ok"}
```

- [ ] **Step 6: 创建所有 __init__.py**

```bash
touch backend/app/__init__.py backend/app/api/__init__.py backend/app/api/v1/__init__.py backend/app/core/__init__.py backend/app/models/__init__.py backend/app/schemas/__init__.py backend/app/crud/__init__.py
```

- [ ] **Step 7: 提交**

```bash
cd D:/01-code/study-buddy
git add backend/
git commit -m "feat(backend): scaffold project structure with config and database"
```

---

### Task 2: User 和 Family 数据模型

**Files:**
- Create: `backend/app/models/user.py`
- Create: `backend/app/models/family.py`
- Modify: `backend/app/models/__init__.py`

- [ ] **Step 1: 创建 User 模型**

```python
# backend/app/models/user.py
import uuid
from enum import StrEnum

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

class UserRole(StrEnum):
    PARENT = "parent"
    STUDENT = "student"

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    role: Mapped[UserRole] = mapped_column(String(10), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(128), nullable=False)
    family_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("families.id"), nullable=True)

    family: Mapped["Family | None"] = relationship(back_populates="members")
```

- [ ] **Step 2: 创建 Family 模型**

```python
# backend/app/models/family.py
import uuid

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

class Family(Base):
    __tablename__ = "families"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(6), unique=True, index=True, nullable=False)

    members: Mapped[list["User"]] = relationship(back_populates="family")
```

- [ ] **Step 3: 更新 models/__init__.py**

```python
from app.models.user import User, UserRole
from app.models.family import Family

__all__ = ["User", "UserRole", "Family"]
```

- [ ] **Step 4: 提交**

```bash
cd D:/01-code/study-buddy
git add backend/app/models/
git commit -m "feat(backend): add User and Family SQLAlchemy models"
```

---

### Task 3: Alembic 初始化与首次迁移

**Files:**
- Create: `backend/alembic.ini`
- Create: `backend/alembic/env.py`

- [ ] **Step 1: 初始化 Alembic**

```bash
cd D:/01-code/study-buddy/backend
pip install -r requirements.txt
alembic init alembic
```

- [ ] **Step 2: 修改 alembic/env.py 的 target_metadata**

在 `env.py` 中找到 `target_metadata = None`，替换为：

```python
from app.database import Base
from app.models import User, Family  # noqa: F401 — ensure models registered
target_metadata = Base.metadata
```

- [ ] **Step 3: 修改 alembic.ini 中的 sqlalchemy.url**

将 `sqlalchemy.url = driver://user:pass@localhost/dbname` 替换为：

```
sqlalchemy.url = postgresql://postgres:postgres@localhost:5432/studybuddy
```

- [ ] **Step 4: 生成首次迁移**

```bash
cd D:/01-code/study-buddy/backend
alembic revision --autogenerate -m "create users and families tables"
```

Expected: 生成迁移文件，包含 `users` 和 `families` 表的 `create_table` 操作。

- [ ] **Step 5: 执行迁移**

```bash
alembic upgrade head
```

Expected: 无报错，表创建成功。

- [ ] **Step 6: 提交**

```bash
cd D:/01-code/study-buddy
git add backend/alembic/ backend/alembic.ini
git commit -m "feat(backend): initialize Alembic with users and families migration"
```

---

### Task 4: JWT 安全工具

**Files:**
- Create: `backend/app/core/security.py`
- Create: `backend/app/schemas/token.py`

- [ ] **Step 1: 创建 security.py**

```python
# backend/app/core/security.py
from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": subject, "exp": expire}, settings.SECRET_KEY, algorithm="HS256")

def decode_access_token(token: str) -> str | None:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload.get("sub")
    except jwt.JWTError:
        return None
```

- [ ] **Step 2: 创建 token schema**

```python
# backend/app/schemas/token.py
from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
```

- [ ] **Step 3: 提交**

```bash
cd D:/01-code/study-buddy
git add backend/app/core/security.py backend/app/schemas/token.py
git commit -m "feat(backend): add JWT security utilities and token schema"
```

---

### Task 5: User 和 Family 的 Pydantic Schemas

**Files:**
- Create: `backend/app/schemas/user.py`
- Create: `backend/app/schemas/family.py`

- [ ] **Step 1: 创建 user schemas**

```python
# backend/app/schemas/user.py
import uuid

from pydantic import BaseModel

from app.models.user import UserRole

class UserRegister(BaseModel):
    phone: str
    password: str
    role: UserRole

class UserLogin(BaseModel):
    phone: str
    password: str

class UserOut(BaseModel):
    id: uuid.UUID
    phone: str
    role: UserRole
    family_id: uuid.UUID | None = None

    model_config = {"from_attributes": True}
```

- [ ] **Step 2: 创建 family schemas**

```python
# backend/app/schemas/family.py
import uuid

from pydantic import BaseModel

class FamilyBind(BaseModel):
    code: str

class FamilyOut(BaseModel):
    id: uuid.UUID
    code: str

    model_config = {"from_attributes": True}
```

- [ ] **Step 3: 提交**

```bash
cd D:/01-code/study-buddy
git add backend/app/schemas/
git commit -m "feat(backend): add User and Family Pydantic schemas"
```

---

### Task 6: User 和 Family CRUD 操作

**Files:**
- Create: `backend/app/crud/user.py`
- Create: `backend/app/crud/family.py`

- [ ] **Step 1: 创建 user CRUD**

```python
# backend/app/crud/user.py
import uuid

from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.core.security import hash_password

def get_user_by_phone(db: Session, phone: str) -> User | None:
    return db.query(User).filter(User.phone == phone).first()

def get_user_by_id(db: Session, user_id: uuid.UUID) -> User | None:
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, phone: str, password: str, role: UserRole) -> User:
    user = User(phone=phone, hashed_password=hash_password(password), role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def update_user_family(db: Session, user: User, family_id: uuid.UUID) -> User:
    user.family_id = family_id
    db.commit()
    db.refresh(user)
    return user
```

- [ ] **Step 2: 创建 family CRUD**

```python
# backend/app/crud/family.py
import random
import string
import uuid

from sqlalchemy.orm import Session

from app.models.family import Family

def _generate_code() -> str:
    return "".join(random.choices(string.digits, k=6))

def create_family(db: Session) -> Family:
    code = _generate_code()
    while db.query(Family).filter(Family.code == code).first():
        code = _generate_code()
    family = Family(code=code)
    db.add(family)
    db.commit()
    db.refresh(family)
    return family

def get_family_by_code(db: Session, code: str) -> Family | None:
    return db.query(Family).filter(Family.code == code).first()

def get_family_by_id(db: Session, family_id: uuid.UUID) -> Family | None:
    return db.query(Family).filter(Family.id == family_id).first()
```

- [ ] **Step 3: 提交**

```bash
cd D:/01-code/study-buddy
git add backend/app/crud/
git commit -m "feat(backend): add User and Family CRUD operations"
```

---

### Task 7: 依赖注入

**Files:**
- Create: `backend/app/core/deps.py`

- [ ] **Step 1: 创建 deps.py**

```python
# backend/app/core/deps.py
import uuid

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.user import User, UserRole
from app.core.security import decode_access_token
from app.crud.user import get_user_by_id

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token_sub: str = Depends(lambda: None)) -> User:
    # 实际由下面的 _get_token_sub 调用
    pass

def get_current_user_dependency(
    db: Session = Depends(get_db),
    authorization: str = Depends(lambda: None),
) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing token")
    token = authorization.removeprefix("Bearer ")
    user_id = decode_access_token(token)
    if not user_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")
    user = get_user_by_id(db, uuid.UUID(user_id))
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found")
    return user

def require_parent(user: User = Depends(get_current_user_dependency)) -> User:
    if user.role != UserRole.PARENT:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Parent access required")
    return user

def require_student(user: User = Depends(get_current_user_dependency)) -> User:
    if user.role != UserRole.STUDENT:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Student access required")
    return user
```

- [ ] **Step 2: 提交**

```bash
cd D:/01-code/study-buddy
git add backend/app/core/deps.py
git commit -m "feat(backend): add dependency injection for auth and DB session"
```

---

### Task 8: 认证 API

**Files:**
- Create: `backend/app/api/v1/auth.py`
- Modify: `backend/app/main.py`

- [ ] **Step 1: 创建 auth.py 路由**

```python
# backend/app/api/v1/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud import user as user_crud
from app.crud import family as family_crud
from app.core.security import verify_password, create_access_token
from app.core.deps import get_db, get_current_user_dependency, require_parent
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
    # 家长注册时自动创建家庭
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
def bind_family(body: FamilyBind, user: User = Depends(require_parent), db: Session = Depends(get_db)):
    if user.family_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Already bound to a family")
    family = family_crud.get_family_by_code(db, body.code)
    if not family:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Family code not found")
    user_crud.update_user_family(db, user, family.id)
    return family

@router.get("/me", response_model=UserOut)
def get_me(user: User = Depends(get_current_user_dependency)):
    return user
```

- [ ] **Step 2: 更新 main.py 挂载路由**

```python
# backend/app/main.py
from fastapi import FastAPI

from app.api.v1.auth import router as auth_router

app = FastAPI(title="作业陪伴助手", version="0.1.0")

app.include_router(auth_router, prefix="/api/v1")

@app.get("/health")
def health_check():
    return {"status": "ok"}
```

- [ ] **Step 3: 手动验证 API**

```bash
cd D:/01-code/study-buddy/backend
uvicorn app.main:app --reload
```

打开 `http://localhost:8000/docs`，测试：
1. `POST /api/v1/auth/register` — 注册家长，应返回 token
2. `POST /api/v1/auth/login` — 登录，应返回 token
3. `GET /api/v1/auth/me` — 带 Bearer token，返回用户信息

- [ ] **Step 4: 提交**

```bash
cd D:/01-code/study-buddy
git add backend/
git commit -m "feat(backend): add auth API — register, login, bind, me"
```

---

### Task 9: 学生绑定家庭 API

**Files:**
- Modify: `backend/app/api/v1/auth.py`

- [ ] **Step 1: 添加学生绑定路由**

在 `auth.py` 中添加：

```python
from app.core.deps import require_student

@router.post("/student-bind", response_model=FamilyOut)
def student_bind_family(body: FamilyBind, user: User = Depends(require_student), db: Session = Depends(get_db)):
    if user.family_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Already bound to a family")
    family = family_crud.get_family_by_code(db, body.code)
    if not family:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Family code not found")
    user_crud.update_user_family(db, user, family.id)
    return family
```

- [ ] **Step 2: 提交**

```bash
cd D:/01-code/study-buddy
git add backend/
git commit -m "feat(backend): add student family bind endpoint"
```
