# 后端业务 API — 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现任务、听写、提交、批改、错题本全部业务 API。

**Architecture:** 每个业务模块遵循 models → schemas → crud → api 的分层。所有接口需 JWT 鉴权，操作限于用户所属家庭。

**Tech Stack:** FastAPI, SQLAlchemy 2.x, Alembic

**前置:** `2026-05-10-backend-foundation.md` 已完成

---

## File Structure

```
backend/app/
├── models/
│   ├── task.py
│   ├── dictation_item.py
│   ├── submission.py
│   └── mistake.py
├── schemas/
│   ├── task.py
│   ├── dictation_item.py
│   ├── submission.py
│   └── mistake.py
├── crud/
│   ├── task.py
│   ├── dictation_item.py
│   ├── submission.py
│   └── mistake.py
├── api/v1/
│   ├── tasks.py
│   ├── dictation.py
│   ├── submissions.py
│   └── mistakes.py
```

---

### Task 1: Task 模型与迁移

**Files:**
- Create: `backend/app/models/task.py`
- Modify: `backend/app/models/__init__.py`

- [ ] **Step 1: 创建 Task 模型**

```python
# backend/app/models/task.py
import uuid
from datetime import date
from enum import StrEnum

from sqlalchemy import String, Date, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

class TaskType(StrEnum):
    SCHOOL = "school"
    HOME = "home"

class TaskStatus(StrEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    GRADED = "graded"

class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    family_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("families.id"), nullable=False, index=True)
    type: Mapped[TaskType] = mapped_column(String(10), nullable=False)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    desc: Mapped[str | None] = mapped_column(Text, nullable=True)
    duration: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 预计耗时（分钟）
    status: Mapped[TaskStatus] = mapped_column(String(20), default=TaskStatus.PENDING, nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    subject: Mapped[str | None] = mapped_column(String(20), nullable=True)  # 语文/数学/英语

    dictation_items: Mapped[list["DictationItem"]] = relationship(back_populates="task", cascade="all, delete-orphan")
    submission: Mapped["Submission | None"] = relationship(back_populates="task", uselist=False)
```

- [ ] **Step 2: 更新 models/__init__.py**

```python
from app.models.user import User, UserRole
from app.models.family import Family
from app.models.task import Task, TaskType, TaskStatus

__all__ = ["User", "UserRole", "Family", "Task", "TaskType", "TaskStatus"]
```

- [ ] **Step 3: 生成并执行迁移**

```bash
cd D:/01-code/study-buddy/backend
alembic revision --autogenerate -m "create tasks table"
alembic upgrade head
```

- [ ] **Step 4: 提交**

```bash
cd D:/01-code/study-buddy
git add backend/
git commit -m "feat(backend): add Task model and migration"
```

---

### Task 2: DictationItem 模型与迁移

**Files:**
- Create: `backend/app/models/dictation_item.py`
- Modify: `backend/app/models/__init__.py`

- [ ] **Step 1: 创建 DictationItem 模型**

```python
# backend/app/models/dictation_item.py
import uuid

from sqlalchemy import String, ForeignKey, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

class DictationItem(Base):
    __tablename__ = "dictation_items"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    task_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tasks.id"), nullable=False, index=True)
    content: Mapped[str] = mapped_column(String(200), nullable=False)
    speed: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)  # 语速倍率
    pause_interval: Mapped[int] = mapped_column(Integer, default=3, nullable=False)  # 停顿秒数

    task: Mapped["Task"] = relationship(back_populates="dictation_items")
```

- [ ] **Step 2: 更新 models/__init__.py**

添加 `from app.models.dictation_item import DictationItem` 和更新 `__all__`。

- [ ] **Step 3: 生成并执行迁移**

```bash
cd D:/01-code/study-buddy/backend
alembic revision --autogenerate -m "create dictation_items table"
alembic upgrade head
```

- [ ] **Step 4: 提交**

```bash
cd D:/01-code/study-buddy
git add backend/
git commit -m "feat(backend): add DictationItem model and migration"
```

---

### Task 3: Submission 和 Mistake 模型与迁移

**Files:**
- Create: `backend/app/models/submission.py`
- Create: `backend/app/models/mistake.py`
- Modify: `backend/app/models/__init__.py`

- [ ] **Step 1: 创建 Submission 模型**

```python
# backend/app/models/submission.py
import uuid
from datetime import datetime

from sqlalchemy import String, ForeignKey, Text, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

class Submission(Base):
    __tablename__ = "submissions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    task_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tasks.id"), unique=True, nullable=False, index=True)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_correct: Mapped[bool | None] = mapped_column(Boolean, nullable=True)  # None=未批改
    submitted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    task: Mapped["Task"] = relationship(back_populates="submission")
```

- [ ] **Step 2: 创建 Mistake 模型**

```python
# backend/app/models/mistake.py
import uuid

from sqlalchemy import String, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

class Mistake(Base):
    __tablename__ = "mistakes"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    task_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tasks.id"), nullable=False, index=True)
    subject: Mapped[str | None] = mapped_column(String(20), nullable=True)
    archived: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    task: Mapped["Task"] = relationship()
```

- [ ] **Step 3: 更新 models/__init__.py**

```python
from app.models.user import User, UserRole
from app.models.family import Family
from app.models.task import Task, TaskType, TaskStatus
from app.models.dictation_item import DictationItem
from app.models.submission import Submission
from app.models.mistake import Mistake

__all__ = [
    "User", "UserRole", "Family",
    "Task", "TaskType", "TaskStatus",
    "DictationItem", "Submission", "Mistake",
]
```

- [ ] **Step 4: 生成并执行迁移**

```bash
cd D:/01-code/study-buddy/backend
alembic revision --autogenerate -m "create submissions and mistakes tables"
alembic upgrade head
```

- [ ] **Step 5: 提交**

```bash
cd D:/01-code/study-buddy
git add backend/
git commit -m "feat(backend): add Submission and Mistake models and migration"
```

---

### Task 4: Task Schemas + CRUD + API

**Files:**
- Create: `backend/app/schemas/task.py`
- Create: `backend/app/crud/task.py`
- Create: `backend/app/api/v1/tasks.py`
- Modify: `backend/app/main.py`

- [ ] **Step 1: 创建 task schemas**

```python
# backend/app/schemas/task.py
import uuid
from datetime import date

from pydantic import BaseModel

from app.models.task import TaskType, TaskStatus

class TaskCreate(BaseModel):
    type: TaskType
    title: str
    desc: str | None = None
    duration: int | None = None
    date: date
    subject: str | None = None

class TaskUpdateStatus(BaseModel):
    status: TaskStatus

class TaskOut(BaseModel):
    id: uuid.UUID
    type: TaskType
    title: str
    desc: str | None = None
    duration: int | None = None
    status: TaskStatus
    date: date
    subject: str | None = None

    model_config = {"from_attributes": True}
```

- [ ] **Step 2: 创建 task CRUD**

```python
# backend/app/crud/task.py
import uuid
from datetime import date

from sqlalchemy.orm import Session

from app.models.task import Task, TaskStatus

def create_task(db: Session, family_id: uuid.UUID, **kwargs) -> Task:
    task = Task(family_id=family_id, **kwargs)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

def get_family_tasks_by_date(db: Session, family_id: uuid.UUID, task_date: date) -> list[Task]:
    return db.query(Task).filter(Task.family_id == family_id, Task.date == task_date).order_by(Task.date).all()

def get_task_by_id(db: Session, task_id: uuid.UUID) -> Task | None:
    return db.query(Task).filter(Task.id == task_id).first()

def update_task_status(db: Session, task: Task, status: TaskStatus) -> Task:
    task.status = status
    db.commit()
    db.refresh(task)
    return task

def delete_task(db: Session, task: Task) -> None:
    db.delete(task)
    db.commit()
```

- [ ] **Step 3: 创建 tasks API**

```python
# backend/app/api/v1/tasks.py
import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user_dependency, require_parent
from app.models.user import User
from app.crud import task as task_crud
from app.schemas.task import TaskCreate, TaskUpdateStatus, TaskOut

router = APIRouter(prefix="/tasks", tags=["tasks"])

def _check_family(user: User):
    if not user.family_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Not bound to a family")

@router.post("/", response_model=TaskOut)
def create_task(body: TaskCreate, user: User = Depends(require_parent), db: Session = Depends(get_db)):
    _check_family(user)
    return task_crud.create_task(db, family_id=user.family_id, **body.model_dump())

@router.get("/", response_model=list[TaskOut])
def list_tasks(task_date: date, user: User = Depends(get_current_user_dependency), db: Session = Depends(get_db)):
    _check_family(user)
    return task_crud.get_family_tasks_by_date(db, user.family_id, task_date)

@router.get("/{task_id}", response_model=TaskOut)
def get_task(task_id: uuid.UUID, user: User = Depends(get_current_user_dependency), db: Session = Depends(get_db)):
    _check_family(user)
    task = task_crud.get_task_by_id(db, task_id)
    if not task or task.family_id != user.family_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Task not found")
    return task

@router.patch("/{task_id}/status", response_model=TaskOut)
def update_status(task_id: uuid.UUID, body: TaskUpdateStatus, user: User = Depends(get_current_user_dependency), db: Session = Depends(get_db)):
    _check_family(user)
    task = task_crud.get_task_by_id(db, task_id)
    if not task or task.family_id != user.family_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Task not found")
    return task_crud.update_task_status(db, task, body.status)

@router.delete("/{task_id}")
def delete_task(task_id: uuid.UUID, user: User = Depends(require_parent), db: Session = Depends(get_db)):
    _check_family(user)
    task = task_crud.get_task_by_id(db, task_id)
    if not task or task.family_id != user.family_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Task not found")
    task_crud.delete_task(db, task)
    return {"ok": True}
```

- [ ] **Step 4: 更新 main.py**

在 `main.py` 中添加：

```python
from app.api.v1.tasks import router as tasks_router
app.include_router(tasks_router, prefix="/api/v1")
```

- [ ] **Step 5: 提交**

```bash
cd D:/01-code/study-buddy
git add backend/
git commit -m "feat(backend): add Task CRUD API"
```

---

### Task 5: DictationItem Schemas + CRUD + API

**Files:**
- Create: `backend/app/schemas/dictation_item.py`
- Create: `backend/app/crud/dictation_item.py`
- Create: `backend/app/api/v1/dictation.py`
- Modify: `backend/app/main.py`

- [ ] **Step 1: 创建 dictation_item schemas**

```python
# backend/app/schemas/dictation_item.py
import uuid

from pydantic import BaseModel

class DictationItemCreate(BaseModel):
    content: str
    speed: float = 1.0
    pause_interval: int = 3

class DictationItemBatch(BaseModel):
    task_id: uuid.UUID
    items: list[DictationItemCreate]

class DictationItemOut(BaseModel):
    id: uuid.UUID
    task_id: uuid.UUID
    content: str
    speed: float
    pause_interval: int

    model_config = {"from_attributes": True}
```

- [ ] **Step 2: 创建 dictation_item CRUD**

```python
# backend/app/crud/dictation_item.py
import uuid

from sqlalchemy.orm import Session

from app.models.dictation_item import DictationItem

def create_items(db: Session, task_id: uuid.UUID, items: list[dict]) -> list[DictationItem]:
    created = []
    for item_data in items:
        item = DictationItem(task_id=task_id, **item_data)
        db.add(item)
        created.append(item)
    db.commit()
    for item in created:
        db.refresh(item)
    return created

def get_items_by_task(db: Session, task_id: uuid.UUID) -> list[DictationItem]:
    return db.query(DictationItem).filter(DictationItem.task_id == task_id).order_by(DictationItem.id).all()

def delete_items_by_task(db: Session, task_id: uuid.UUID) -> None:
    db.query(DictationItem).filter(DictationItem.task_id == task_id).delete()
    db.commit()
```

- [ ] **Step 3: 创建 dictation API**

```python
# backend/app/api/v1/dictation.py
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user_dependency
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
def create_dictation_items(body: DictationItemBatch, user: User = Depends(get_current_user_dependency), db: Session = Depends(get_db)):
    _get_family_task(db, body.task_id, user)
    return dictation_crud.create_items(db, body.task_id, [i.model_dump() for i in body.items])

@router.get("/{task_id}", response_model=list[DictationItemOut])
def get_dictation_items(task_id: uuid.UUID, user: User = Depends(get_current_user_dependency), db: Session = Depends(get_db)):
    _get_family_task(db, task_id, user)
    return dictation_crud.get_items_by_task(db, task_id)
```

- [ ] **Step 4: 更新 main.py**

```python
from app.api.v1.dictation import router as dictation_router
app.include_router(dictation_router, prefix="/api/v1")
```

- [ ] **Step 5: 提交**

```bash
cd D:/01-code/study-buddy
git add backend/
git commit -m "feat(backend): add DictationItem CRUD API"
```

---

### Task 6: Submission Schemas + CRUD + API

**Files:**
- Create: `backend/app/schemas/submission.py`
- Create: `backend/app/crud/submission.py`
- Create: `backend/app/api/v1/submissions.py`
- Modify: `backend/app/main.py`

- [ ] **Step 1: 创建 submission schemas**

```python
# backend/app/schemas/submission.py
import uuid
from datetime import datetime

from pydantic import BaseModel

class SubmissionCreate(BaseModel):
    task_id: uuid.UUID

class SubmissionGrade(BaseModel):
    is_correct: bool
    comment: str | None = None

class SubmissionOut(BaseModel):
    id: uuid.UUID
    task_id: uuid.UUID
    comment: str | None = None
    is_correct: bool | None = None
    submitted_at: datetime

    model_config = {"from_attributes": True}
```

- [ ] **Step 2: 创建 submission CRUD**

```python
# backend/app/crud/submission.py
import uuid

from sqlalchemy.orm import Session

from app.models.submission import Submission

def create_submission(db: Session, task_id: uuid.UUID) -> Submission:
    sub = Submission(task_id=task_id)
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return sub

def get_submission_by_task(db: Session, task_id: uuid.UUID) -> Submission | None:
    return db.query(Submission).filter(Submission.task_id == task_id).first()

def grade_submission(db: Session, submission: Submission, is_correct: bool, comment: str | None) -> Submission:
    submission.is_correct = is_correct
    submission.comment = comment
    db.commit()
    db.refresh(submission)
    return submission
```

- [ ] **Step 3: 创建 submissions API**

```python
# backend/app/api/v1/submissions.py
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user_dependency, require_parent
from app.models.user import User
from app.models.task import TaskStatus
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

@router.post("/", response_model=SubmissionOut)
def submit_task(body: SubmissionCreate, user: User = Depends(get_current_user_dependency), db: Session = Depends(get_db)):
    task = _get_family_task(db, body.task_id, user)
    if task.status == TaskStatus.SUBMITTED or task.status == TaskStatus.GRADED:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Task already submitted")
    existing = submission_crud.get_submission_by_task(db, body.task_id)
    if existing:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Submission already exists")
    sub = submission_crud.create_submission(db, body.task_id)
    task_crud.update_task_status(db, task, TaskStatus.SUBMITTED)
    return sub

@router.post("/{submission_id}/grade", response_model=SubmissionOut)
def grade_submission(submission_id: uuid.UUID, body: SubmissionGrade, user: User = Depends(require_parent), db: Session = Depends(get_db)):
    sub = db.query(Submission).filter(Submission.id == submission_id).first()
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
```

注意：需要导入 `Submission` 模型，在文件顶部添加 `from app.models.submission import Submission`。

- [ ] **Step 4: 更新 main.py**

```python
from app.api.v1.submissions import router as submissions_router
app.include_router(submissions_router, prefix="/api/v1")
```

- [ ] **Step 5: 提交**

```bash
cd D:/01-code/study-buddy
git add backend/
git commit -m "feat(backend): add Submission API with grading and auto-mistake"
```

---

### Task 7: Mistake Schemas + CRUD + API

**Files:**
- Create: `backend/app/schemas/mistake.py`
- Create: `backend/app/crud/mistake.py`
- Create: `backend/app/api/v1/mistakes.py`
- Modify: `backend/app/main.py`

- [ ] **Step 1: 创建 mistake schemas**

```python
# backend/app/schemas/mistake.py
import uuid

from pydantic import BaseModel

class MistakeOut(BaseModel):
    id: uuid.UUID
    task_id: uuid.UUID
    subject: str | None = None
    archived: bool

    model_config = {"from_attributes": True}
```

- [ ] **Step 2: 创建 mistake CRUD**

```python
# backend/app/crud/mistake.py
import uuid

from sqlalchemy.orm import Session

from app.models.mistake import Mistake

def create_mistake(db: Session, task_id: uuid.UUID, subject: str | None) -> Mistake:
    mistake = Mistake(task_id=task_id, subject=subject)
    db.add(mistake)
    db.commit()
    db.refresh(mistake)
    return mistake

def get_family_mistakes(db: Session, family_id: uuid.UUID, subject: str | None = None, archived: bool | None = None) -> list[Mistake]:
    from app.models.task import Task
    q = db.query(Mistake).join(Task, Mistake.task_id == Task.id).filter(Task.family_id == family_id)
    if subject:
        q = q.filter(Mistake.subject == subject)
    if archived is not None:
        q = q.filter(Mistake.archived == archived)
    return q.order_by(Mistake.id.desc()).all()

def archive_mistake(db: Session, mistake: Mistake) -> Mistake:
    mistake.archived = True
    db.commit()
    db.refresh(mistake)
    return mistake

def get_mistake_by_id(db: Session, mistake_id: uuid.UUID) -> Mistake | None:
    return db.query(Mistake).filter(Mistake.id == mistake_id).first()
```

- [ ] **Step 3: 创建 mistakes API**

```python
# backend/app/api/v1/mistakes.py
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user_dependency, require_parent
from app.models.user import User
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
    from app.crud.task import get_task_by_id
    task = get_task_by_id(db, mistake.task_id)
    if not task or task.family_id != user.family_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Mistake not found")
    return mistake_crud.archive_mistake(db, mistake)
```

- [ ] **Step 4: 更新 main.py（最终版）**

```python
# backend/app/main.py
from fastapi import FastAPI

from app.api.v1.auth import router as auth_router
from app.api.v1.tasks import router as tasks_router
from app.api.v1.dictation import router as dictation_router
from app.api.v1.submissions import router as submissions_router
from app.api.v1.mistakes import router as mistakes_router

app = FastAPI(title="作业陪伴助手", version="0.1.0")

app.include_router(auth_router, prefix="/api/v1")
app.include_router(tasks_router, prefix="/api/v1")
app.include_router(dictation_router, prefix="/api/v1")
app.include_router(submissions_router, prefix="/api/v1")
app.include_router(mistakes_router, prefix="/api/v1")

@app.get("/health")
def health_check():
    return {"status": "ok"}
```

- [ ] **Step 5: 启动并验证所有 API**

```bash
cd D:/01-code/study-buddy/backend
uvicorn app.main:app --reload
```

打开 `http://localhost:8000/docs`，完整测试业务流程：
1. 注册家长 → 获取 token
2. 创建任务 → POST `/api/v1/tasks/`
3. 创建听写词组 → POST `/api/v1/dictation/`
4. 查询今日任务 → GET `/api/v1/tasks/?date=2026-05-10`
5. 提交任务 → POST `/api/v1/submissions/`
6. 批改 → POST `/api/v1/submissions/{id}/grade` (is_correct=false)
7. 查看错题 → GET `/api/v1/mistakes/`

- [ ] **Step 6: 提交**

```bash
cd D:/01-code/study-buddy
git add backend/
git commit -m "feat(backend): add Mistake API and finalize all business routes"
```
