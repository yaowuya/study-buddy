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


# ─── User schemas ───

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


# ─── Family schemas ───

class AdminFamilyOut(BaseModel):
    id: uuid.UUID
    code: str
    member_count: int = 0
    is_deleted: bool

    model_config = {"from_attributes": True}


class AdminFamilyDetailOut(AdminFamilyOut):
    members: list[AdminUserOut] = []


# ─── Task schemas ───

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


# ─── Stats schema ───

class AdminStatsOut(BaseModel):
    total_users: int
    total_families: int
    today_tasks: int
    pending_submissions: int
