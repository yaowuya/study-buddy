# 后端管理员系统 — 执行计划

## 任务总览

| # | 任务 | 依赖 | 预计 |
|---|------|------|------|
| B1 | Model: Admin 模型 + User/Family/Task 加 is_deleted/is_active | — | 5min |
| B2 | Alembic 迁移 | B1 | 3min |
| B3 | Schema: pagination + admin + admin user/family/task | B1 | 5min |
| B4 | CRUD: admin + 软删除过滤改造 | B1 | 5min |
| B5 | Deps: require_admin 权限守卫 | B1 | 3min |
| B6 | API: admin/auth 登录/me/改密 | B3,B4,B5 | 5min |
| B7 | API: admin/users 管理 | B3,B4,B5 | 5min |
| B8 | API: admin/families 管理 | B3,B4,B5 | 5min |
| B9 | API: admin/tasks 管理 + stats | B3,B4,B5 | 5min |
| B10 | main.py: lifespan 种子 + 路由注册 + CORS | B6-B9 | 3min |
| B11 | auth.py: 登录禁用检查 | B4 | 3min |
| B12 | 测试: admin 全套 | B10 | 10min |
| B13 | 数据库迁移执行 + 冒烟测试 | B12 | 3min |

---

### 任务 B1：Model — Admin 模型 + 现有模型加字段

**Files:**
- 创建：`app/models/admin.py`
- 修改：`app/models/user.py`, `app/models/family.py`, `app/models/task.py`
- 修改：`app/models/__init__.py`

**Reasoning:** 模型层是所有上层代码的基础，必须先建好才能写 CRUD 和 API。软删除/禁用字段同时加，一次性完成 schema 变更。

- [ ] **步骤 1：创建 Admin 模型**

```python
# app/models/admin.py
import uuid
from datetime import datetime

from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.db_types import GUID
from app.database import Base


class Admin(Base):
    __tablename__ = "admins"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(128), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
```

- [ ] **步骤 2：User 模型加 is_active + is_deleted**

在 `app/models/user.py` 的 User 类中新增：
```python
is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
```

- [ ] **步骤 3：Family 模型加 is_deleted**

在 `app/models/family.py` 的 Family 类中新增：
```python
is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
```

- [ ] **步骤 4：Task 模型加 is_deleted**

在 `app/models/task.py` 的 Task 类中新增：
```python
is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
```

- [ ] **步骤 5：__init__.py 导入 Admin**

```python
from app.models.admin import Admin  # noqa: F401
```

- [ ] **步骤 6：提交**

```bash
git add app/models/admin.py app/models/user.py app/models/family.py app/models/task.py app/models/__init__.py
git commit -m "新增 Admin 模型，User/Family/Task 加 is_deleted/is_active 字段"
```

---

### 任务 B2：Alembic 迁移

**Files:**
- 生成：`alembic/versions/xxx_add_admins_table_and_soft_delete_fields.py`

**Reasoning:** 模型改完立即生成迁移脚本，保证数据库 schema 与代码同步。

- [ ] **步骤 1：生成迁移脚本**

```bash
alembic revision --autogenerate -m "add admins table and soft delete fields"
```

- [ ] **步骤 2：检查生成的迁移脚本**

确认包含：
- CREATE TABLE admins
- users 表 ADD is_active, is_deleted
- families 表 ADD is_deleted
- tasks 表 ADD is_deleted

- [ ] **步骤 3：提交**

```bash
git add alembic/versions/
git commit -m "新增 Alembic 迁移：admins 表 + 软删除字段"
```

---

### 任务 B3：Schema — pagination + admin + admin user/family/task

**Files:**
- 创建：`app/schemas/pagination.py`
- 创建：`app/schemas/admin.py`

**Reasoning:** Schema 是 API 的输入输出契约，先定义好才能写 API 层。分页 schema 为所有管理端列表接口共用。

- [ ] **步骤 1：创建分页 Schema**

```python
# app/schemas/pagination.py
from typing import Generic, TypeVar, List

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class PaginatedResponse(BaseModel, Generic[T]):
    total: int
    items: List[T]
    page: int
    page_size: int
```

- [ ] **步骤 2：创建 Admin Schema**

```python
# app/schemas/admin.py
import uuid
from datetime import datetime

from pydantic import BaseModel


class AdminLogin(BaseModel):
    username: str
    password: str


class AdminOut(BaseModel):
    id: uuid.UUID
    username: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class AdminPasswordChange(BaseModel):
    old_password: str
    new_password: str


class AdminUserOut(BaseModel):
    id: uuid.UUID
    phone: str
    role: str
    family_id: uuid.UUID | None = None
    is_active: bool
    is_deleted: bool

    model_config = {"from_attributes": True}


class AdminUserDetailOut(AdminUserOut):
    family_code: str | None = None
    task_count: int = 0


class AdminUserUpdate(BaseModel):
    role: str | None = None
    is_active: bool | None = None


class AdminFamilyOut(BaseModel):
    id: uuid.UUID
    code: str
    member_count: int = 0
    is_deleted: bool

    model_config = {"from_attributes": True}


class AdminFamilyDetailOut(AdminFamilyOut):
    members: list[AdminUserOut] = []


class AdminTaskOut(BaseModel):
    id: uuid.UUID
    family_id: uuid.UUID
    type: str
    title: str
    status: str
    date: str
    subject: str | None = None
    is_deleted: bool

    model_config = {"from_attributes": True}


class AdminTaskDetailOut(AdminTaskOut):
    desc: str | None = None
    duration: int | None = None
    submission: dict | None = None
    dictation_items: list[dict] = []


class AdminStatsOut(BaseModel):
    total_users: int
    total_families: int
    today_tasks: int
    pending_submissions: int
```

- [ ] **步骤 3：提交**

```bash
git add app/schemas/pagination.py app/schemas/admin.py
git commit -m "新增管理端 Schema：分页、Admin、用户/家庭/任务输出"
```

---

### 任务 B4：CRUD — admin + 软删除过滤改造

**Files:**
- 创建：`app/crud/admin.py`
- 修改：`app/crud/user.py`, `app/crud/family.py`, `app/crud/task.py`

**Reasoning:** CRUD 是业务逻辑核心，先实现数据访问层才能写 API。软删除过滤改造现有 CRUD 确保用户端接口不受影响。

- [ ] **步骤 1：创建 admin CRUD**

```python
# app/crud/admin.py
import uuid

from sqlalchemy.orm import Session

from app.models.admin import Admin
from app.core.security import hash_password


def get_admin_by_username(db: Session, username: str) -> Admin | None:
    return db.query(Admin).filter(Admin.username == username).first()


def get_admin_by_id(db: Session, admin_id: uuid.UUID) -> Admin | None:
    return db.query(Admin).filter(Admin.id == admin_id).first()


def seed_admin(db: Session) -> None:
    """幂等插入默认管理员"""
    if not db.query(Admin).first():
        admin = Admin(username="admin", hashed_password=hash_password("admin123"))
        db.add(admin)
        db.commit()


def update_admin_password(db: Session, admin: Admin, new_hashed_password: str) -> Admin:
    admin.hashed_password = new_hashed_password
    db.commit()
    db.refresh(admin)
    return admin
```

- [ ] **步骤 2：改造 user CRUD — 加 is_deleted 过滤**

`app/crud/user.py` 中：
- `get_user_by_phone`: 追加 `.filter(User.is_deleted == False)`
- `get_user_by_id`: 追加 `.filter(User.is_deleted == False)`

- [ ] **步骤 3：改造 family CRUD — 加 is_deleted 过滤**

`app/crud/family.py` 中：
- `get_family_by_code`: 追加 `.filter(Family.is_deleted == False)`
- `get_family_by_id`: 追加 `.filter(Family.is_deleted == False)`

- [ ] **步骤 4：改造 task CRUD — 加 is_deleted 过滤**

`app/crud/task.py` 中：
- `get_family_tasks_by_date`: 追加 `.filter(Task.is_deleted == False)`
- `get_task_by_id`: 追加 `.filter(Task.is_deleted == False)`

- [ ] **步骤 5：提交**

```bash
git add app/crud/admin.py app/crud/user.py app/crud/family.py app/crud/task.py
git commit -m "新增 Admin CRUD，现有 CRUD 加软删除过滤"
```

---

### 任务 B5：Deps — require_admin 权限守卫

**Files:**
- 修改：`app/core/deps.py`

**Reasoning:** 权限守卫是所有管理端接口的统一入口，必须在写 API 之前完成。JWT subject 用 `admin:` 前缀区分用户端和管理端。

- [ ] **步骤 1：新增 require_admin**

在 `app/core/deps.py` 中新增：

```python
from app.models.admin import Admin

def require_admin(request: Request, db: Session = Depends(get_db)) -> Admin:
    authorization = request.headers.get("Authorization")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing token")
    token = authorization.removeprefix("Bearer ")
    payload = decode_access_token(token)
    if not payload or not payload.startswith("admin:"):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Admin access required")
    admin_id = uuid.UUID(payload.removeprefix("admin:"))
    admin = db.query(Admin).filter(Admin.id == admin_id, Admin.is_active == True).first()
    if not admin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Admin not found or inactive")
    return admin
```

- [ ] **步骤 2：提交**

```bash
git add app/core/deps.py
git commit -m "新增 require_admin 权限守卫，JWT admin: 前缀区分"
```

---

### 任务 B6：API — admin/auth 登录/me/改密

**Files:**
- 创建：`app/api/v1/admin/auth.py`

**Reasoning:** 认证是管理端的第一入口，先实现登录才能测试其他接口。

- [ ] **步骤 1：实现 auth 路由**

```python
# app/api/v1/admin/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_admin
from app.core.security import verify_password, create_access_token, hash_password
from app.models.admin import Admin
from app.crud import admin as admin_crud
from app.schemas.admin import AdminLogin, AdminOut, AdminPasswordChange
from app.schemas.token import Token

router = APIRouter(prefix="/auth", tags=["admin-auth"])


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
def admin_change_password(body: AdminPasswordChange, admin: Admin = Depends(require_admin), db: Session = Depends(get_db)):
    if not verify_password(body.old_password, admin.hashed_password):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Old password is incorrect")
    admin_crud.update_admin_password(db, admin, hash_password(body.new_password))
    return {"ok": True}
```

- [ ] **步骤 2：提交**

```bash
git add app/api/v1/admin/auth.py
git commit -m "新增管理端认证接口：登录/me/改密"
```

---

### 任务 B7：API — admin/users 用户管理

**Files:**
- 创建：`app/api/v1/admin/users.py`

**Reasoning:** 用户管理是管理端核心功能，支持分页+筛选+软删除。

- [ ] **步骤 1：实现 users 路由**

```python
# app/api/v1/admin/users.py
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.deps import get_db, require_admin
from app.models.admin import Admin
from app.models.user import User
from app.models.family import Family
from app.models.task import Task
from app.schemas.admin import AdminUserOut, AdminUserDetailOut, AdminUserUpdate
from app.schemas.pagination import PaginatedResponse

router = APIRouter(prefix="/users", tags=["admin-users"])


@router.get("/", response_model=PaginatedResponse[AdminUserOut])
def list_users(
    page: int = 1, page_size: int = 20,
    phone: str | None = None, role: str | None = None, is_active: bool | None = None,
    admin: Admin = Depends(require_admin), db: Session = Depends(get_db),
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
    task_count = db.query(Task).filter(Task.family_id == user.family_id).count() if user.family_id else 0
    return AdminUserDetailOut(
        id=user.id, phone=user.phone, role=user.role, family_id=user.family_id,
        is_active=user.is_active, is_deleted=user.is_deleted,
        family_code=family_code, task_count=task_count,
    )


@router.patch("/{user_id}", response_model=AdminUserOut)
def update_user(user_id: uuid.UUID, body: AdminUserUpdate, admin: Admin = Depends(require_admin), db: Session = Depends(get_db)):
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
```

- [ ] **步骤 2：提交**

```bash
git add app/api/v1/admin/users.py
git commit -m "新增管理端用户管理接口：列表/详情/修改/软删除"
```

---

### 任务 B8：API — admin/families 家庭管理

**Files:**
- 创建：`app/api/v1/admin/families.py`

- [ ] **步骤 1：实现 families 路由**

```python
# app/api/v1/admin/families.py
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.deps import get_db, require_admin
from app.models.admin import Admin
from app.models.family import Family
from app.models.user import User
from app.schemas.admin import AdminFamilyOut, AdminFamilyDetailOut, AdminUserOut
from app.schemas.pagination import PaginatedResponse

router = APIRouter(prefix="/families", tags=["admin-families"])


@router.get("/", response_model=PaginatedResponse[AdminFamilyOut])
def list_families(
    page: int = 1, page_size: int = 20, code: str | None = None,
    admin: Admin = Depends(require_admin), db: Session = Depends(get_db),
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
    member_outs = [AdminUserOut(id=m.id, phone=m.phone, role=m.role, family_id=m.family_id, is_active=m.is_active, is_deleted=m.is_deleted) for m in members]
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
```

- [ ] **步骤 2：提交**

```bash
git add app/api/v1/admin/families.py
git commit -m "新增管理端家庭管理接口：列表/详情/软删除"
```

---

### 任务 B9：API — admin/tasks 作业管理 + stats

**Files:**
- 创建：`app/api/v1/admin/tasks.py`

- [ ] **步骤 1：实现 tasks + stats 路由**

```python
# app/api/v1/admin/tasks.py
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

router = APIRouter(prefix="/tasks", tags=["admin-tasks"])


@router.get("/", response_model=PaginatedResponse[AdminTaskOut])
def list_tasks(
    page: int = 1, page_size: int = 20,
    family_id: uuid.UUID | None = None, status: str | None = None,
    date_from: date | None = None, date_to: date | None = None,
    admin: Admin = Depends(require_admin), db: Session = Depends(get_db),
):
    query = db.query(Task)
    if family_id:
        query = query.filter(Task.family_id == family_id)
    if status:
        query = query.filter(Task.status == status)
    if date_from:
        query = query.filter(Task.date >= date_from)
    if date_to:
        query = query.filter(Task.date <= date_to)
    total = query.count()
    items = query.order_by(Task.date.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return PaginatedResponse(total=total, items=items, page=page, page_size=page_size)


@router.get("/stats", response_model=AdminStatsOut)
def get_stats(admin: Admin = Depends(require_admin), db: Session = Depends(get_db)):
    today = date.today()
    total_users = db.query(User).count()
    total_families = db.query(Family).count()
    today_tasks = db.query(Task).filter(Task.date == today).count()
    pending_submissions = db.query(Submission).filter(Submission.is_correct == None).count()
    return AdminStatsOut(
        total_users=total_users, total_families=total_families,
        today_tasks=today_tasks, pending_submissions=pending_submissions,
    )


@router.get("/{task_id}", response_model=AdminTaskDetailOut)
def get_task(task_id: uuid.UUID, admin: Admin = Depends(require_admin), db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Task not found")
    submission_data = None
    if task.submission:
        s = task.submission
        submission_data = {"is_correct": s.is_correct, "comment": s.comment, "submitted_at": s.submitted_at.isoformat()}
    dictation_data = [{"content": d.content, "speed": d.speed, "pause_interval": d.pause_interval} for d in task.dictation_items]
    return AdminTaskDetailOut(
        id=task.id, family_id=task.family_id, type=task.type, title=task.title,
        status=task.status, date=str(task.date), subject=task.subject, is_deleted=task.is_deleted,
        desc=task.desc, duration=task.duration, submission=submission_data, dictation_items=dictation_data,
    )


@router.delete("/{task_id}")
def delete_task(task_id: uuid.UUID, admin: Admin = Depends(require_admin), db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Task not found")
    task.is_deleted = True
    db.commit()
    return {"ok": True}
```

- [ ] **步骤 2：提交**

```bash
git add app/api/v1/admin/tasks.py
git commit -m "新增管理端作业管理接口：列表/详情/软删除/统计"
```

---

### 任务 B10：main.py — 路由注册 + lifespan 种子 + CORS

**Files:**
- 修改：`app/main.py`
- 修改：`app/core/config.py`
- 修改：`.env`
- 创建：`app/api/v1/admin/__init__.py`

**Reasoning:** 所有 API 文件写完后，注册路由和启动种子才能让整个系统运行起来。

- [ ] **步骤 1：创建 admin __init__.py**

```python
# app/api/v1/admin/__init__.py
from fastapi import APIRouter
from .auth import router as auth_router
from .users import router as users_router
from .families import router as families_router
from .tasks import router as tasks_router

router = APIRouter(prefix="/admin", tags=["admin"])
router.include_router(auth_router, prefix="/auth")
router.include_router(users_router, prefix="/users")
router.include_router(families_router, prefix="/families")
router.include_router(tasks_router, prefix="/tasks")
```

- [ ] **步骤 2：修改 main.py**

- 改用 lifespan 替代无启动逻辑
- 注册 admin 路由
- 种子管理员

- [ ] **步骤 3：修改 config.py CORS**

```python
CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:5174"]
```

- [ ] **步骤 4：修改 .env CORS**

- [ ] **步骤 5：提交**

```bash
git add app/api/v1/admin/__init__.py app/main.py app/core/config.py .env
git commit -m "注册管理端路由，lifespan 种子管理员，CORS 加 5174"
```

---

### 任务 B11：auth.py — 登录禁用检查

**Files:**
- 修改：`app/api/v1/auth.py`

**Reasoning:** User 模型加了 is_active，登录接口必须检查，否则禁用用户仍能登录。

- [ ] **步骤 1：在 login 函数中新增 is_active 检查**

验证密码后：
```python
if not user.is_active:
    raise HTTPException(status.HTTP_403_FORBIDDEN, "Account disabled")
```

- [ ] **步骤 2：提交**

```bash
git add app/api/v1/auth.py
git commit -m "用户登录新增 is_active 禁用检查"
```

---

### 任务 B12：测试 — admin 全套

**Files:**
- 创建：`tests/test_admin.py`

**Reasoning:** 测试覆盖所有管理端接口，确保认证、分页、软删除、权限隔离正确。

- [ ] **步骤 1：写测试**

覆盖场景：
1. 管理员登录（成功/失败/禁用）
2. 管理员 me 接口
3. 管理员改密
4. 非管理员 token 访问 admin 接口被拒
5. 用户列表（分页 + 筛选）
6. 用户详情
7. 用户修改（角色/状态）
8. 用户软删除
9. 家庭列表/详情/软删除
10. 任务列表/详情/软删除/统计
11. 软删除后用户端不可见

- [ ] **步骤 2：运行测试验证通过**

```bash
.venv/Scripts/python -m pytest tests/test_admin.py -v
```

- [ ] **步骤 3：运行全量测试**

```bash
rm -f test.db && .venv/Scripts/python -m pytest tests/ -v
```

- [ ] **步骤 4：提交**

```bash
git add tests/test_admin.py
git commit -m "新增管理端接口测试"
```

---

### 任务 B13：数据库迁移执行 + 冒烟测试

**Reasoning:** 代码和测试都通过后，执行真实数据库迁移并验证。

- [ ] **步骤 1：执行 Alembic 迁移**

```bash
alembic upgrade head
```

- [ ] **步骤 2：验证表结构**

```bash
mysql -u root -proot -e "USE studybuddy; SHOW TABLES; DESCRIBE admins;"
```

- [ ] **步骤 3：启动服务验证**

```bash
uvicorn app.main:app --reload
```

访问 `http://localhost:8000/docs` 确认 admin 接口出现在 Swagger 中。
