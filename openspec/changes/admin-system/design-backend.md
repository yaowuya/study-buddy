# 后端管理员系统 — 技术方案设计

## 第一部分：架构决策

### 决策 1：管理员账号模型
- **选择**：独立 `admins` 表，与 `users` 表完全隔离
- **理由**：管理员与普通用户身份不同，登录方式不同（用户名 vs 手机号），避免在 User 模型加 role=admin 带来的混淆

### 决策 2：用户禁用机制
- **选择**：在 User 模型新增 `is_active` 字段（默认 True），软禁用
- **理由**：管理员可临时禁用问题用户，被禁用用户无法登录，数据保留可恢复

### 决策 3：默认管理员种子数据
- **选择**：启动脚本自动种子（docker-entrypoint.sh / main.py 启动时检查）
- **理由**：比 Alembic 数据迁移更灵活，重复执行幂等，容器重建自动初始化

### 决策 4：删除策略
- **选择**：全局软删除，User / Family / Task 均新增 `is_deleted` 字段
- **理由**：管理员误删可恢复，数据不丢失；现有用户端接口自动过滤 `is_deleted=True` 的记录

---

## 第二部分：技术方案详述

### 后端模块设计

新增文件清单（精确到文件级别）：

```
app/
├── models/
│   └── admin.py                 # 新增：Admin 模型
├── schemas/
│   ├── admin.py                 # 新增：Admin 登录/输出 schema
│   └── pagination.py            # 新增：分页通用 schema
├── crud/
│   └── admin.py                 # 新增：Admin CRUD（登录验证、种子）
├── api/v1/
│   └── admin/                   # 新增：管理员接口目录
│       ├── __init__.py          # 新增：汇总子路由
│       ├── auth.py              # 新增：管理员登录
│       ├── users.py             # 新增：用户管理
│       ├── families.py          # 新增：家庭管理
│       └── tasks.py             # 新增：作业管理
└── core/
    └── deps.py                  # 修改：新增 require_admin 依赖
```

修改文件清单：

```
app/models/__init__.py           # 修改：导入 Admin
app/models/user.py               # 修改：新增 is_active, is_deleted 字段
app/models/family.py             # 修改：新增 is_deleted 字段
app/models/task.py               # 修改：新增 is_deleted 字段
app/main.py                      # 修改：注册 admin 路由 + 启动种子
app/crud/user.py                 # 修改：查询过滤 is_deleted
app/crud/family.py               # 修改：查询过滤 is_deleted
app/crud/task.py                 # 修改：查询过滤 is_deleted
app/api/v1/auth.py               # 修改：登录时检查 is_active
```

### 数据模型

#### admins 表（新增）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK, default=uuid4 | 管理员 ID |
| username | VARCHAR(50) | UNIQUE, NOT NULL | 登录用户名 |
| hashed_password | VARCHAR(128) | NOT NULL | bcrypt 加密密码 |
| is_active | BOOLEAN | DEFAULT TRUE | 是否启用 |
| created_at | DATETIME | DEFAULT now() | 创建时间 |

#### users 表（修改）

新增字段：

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| is_active | BOOLEAN | DEFAULT TRUE | 是否启用（禁用后无法登录） |
| is_deleted | BOOLEAN | DEFAULT FALSE | 软删除标记 |

#### families 表（修改）

新增字段：

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| is_deleted | BOOLEAN | DEFAULT FALSE | 软删除标记 |

#### tasks 表（修改）

新增字段：

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| is_deleted | BOOLEAN | DEFAULT FALSE | 软删除标记 |

### 通用分页 Schema

```python
# app/schemas/pagination.py

class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

class PaginatedResponse(BaseModel, Generic[T]):
    total: int
    items: list[T]
    page: int
    page_size: int
```

### API 接口

#### 管理员认证

| 方法 | 路径 | 请求体 | 响应 | 说明 |
|------|------|--------|------|------|
| POST | `/api/v1/admin/auth/login` | `{username, password}` | `{access_token}` | 管理员登录，返回 JWT |
| GET | `/api/v1/admin/auth/me` | — | `AdminOut` | 获取当前管理员信息 |
| PATCH | `/api/v1/admin/auth/password` | `{old_password, new_password}` | `{ok: true}` | 修改管理员密码 |

**AdminOut**: id, username, is_active, created_at

#### 用户管理

| 方法 | 路径 | 参数 | 响应 | 说明 |
|------|------|------|------|------|
| GET | `/api/v1/admin/users/` | `page, page_size, phone?, role?, is_active?` | `PaginatedResponse[AdminUserOut]` | 用户列表 |
| GET | `/api/v1/admin/users/{id}` | — | `AdminUserDetailOut` | 用户详情（含家庭信息） |
| PATCH | `/api/v1/admin/users/{id}` | `{role?, is_active?}` | `AdminUserOut` | 修改用户 |
| DELETE | `/api/v1/admin/users/{id}` | — | `{ok: true}` | 软删除用户 |

**AdminUserOut**: id, phone, role, family_id, is_active, is_deleted
**AdminUserDetailOut**: 同 AdminUserOut + family 信息 (code) + 任务数统计

#### 家庭管理

| 方法 | 路径 | 参数 | 响应 | 说明 |
|------|------|------|------|------|
| GET | `/api/v1/admin/families/` | `page, page_size, code?` | `PaginatedResponse[AdminFamilyOut]` | 家庭列表 |
| GET | `/api/v1/admin/families/{id}` | — | `AdminFamilyDetailOut` | 家庭详情（含成员列表） |
| DELETE | `/api/v1/admin/families/{id}` | — | `{ok: true}` | 软删除家庭 |

**AdminFamilyOut**: id, code, member_count, is_deleted
**AdminFamilyDetailOut**: 同 AdminFamilyOut + 成员列表 [AdminUserOut]

#### 作业管理

| 方法 | 路径 | 参数 | 响应 | 说明 |
|------|------|------|------|------|
| GET | `/api/v1/admin/tasks/` | `page, page_size, family_id?, status?, date_from?, date_to?` | `PaginatedResponse[AdminTaskOut]` | 任务列表 |
| GET | `/api/v1/admin/tasks/{id}` | — | `AdminTaskDetailOut` | 任务详情 |
| DELETE | `/api/v1/admin/tasks/{id}` | — | `{ok: true}` | 软删除任务 |

**AdminTaskOut**: id, family_id, type, title, status, date, subject, is_deleted
**AdminTaskDetailOut**: 同 AdminTaskOut + submission + dictation_items

#### 统计接口

| 方法 | 路径 | 参数 | 响应 | 说明 |
|------|------|------|------|------|
| GET | `/api/v1/admin/stats` | — | `AdminStatsOut` | 仪表盘统计数据 |

**AdminStatsOut**: total_users, total_families, today_tasks, pending_submissions

### 业务逻辑要点

#### 1. require_admin 权限守卫

```python
# app/core/deps.py 新增

def require_admin(request: Request, db: Session = Depends(get_db)) -> Admin:
    authorization = request.headers.get("Authorization")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing token")
    token = authorization.removeprefix("Bearer ")
    # JWT payload 中区分用户类型：admin token 带 {"sub": "admin:<id>"}
    payload = decode_access_token(token)
    if not payload or not payload.startswith("admin:"):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Admin access required")
    admin_id = uuid.UUID(payload.removeprefix("admin:"))
    admin = db.query(Admin).filter(Admin.id == admin_id, Admin.is_active == True).first()
    if not admin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Admin not found or inactive")
    return admin
```

**JWT 区分策略**：管理员 token 的 subject 前缀为 `admin:`，用户 token 不变。这样 `get_current_user` 和 `require_admin` 互不干扰。

#### 2. 软删除过滤与级联规则

所有现有 CRUD 查询需追加 `.filter(X.is_deleted == False)` 条件：

- `crud/user.py`: `get_user_by_phone`, `get_user_by_id`
- `crud/family.py`: `get_family_by_code`, `get_family_by_id`
- `crud/task.py`: `get_family_tasks_by_date`, `get_task_by_id`

管理员接口则**不过滤** `is_deleted`，可查看已删除数据。

**级联规则（重要）**：

- 管理端 Family 软删除后，其下 User/Task 仍独立可见（它们有自己的 is_deleted 标记）
- 管理端 User 软删除后，其 Task 仍独立可见
- 用户端过滤时：如果 Task 的 Family 被软删除，该 Task 也不可见（JOIN families ON is_deleted=False）
- Submission / Mistake / DictationItem **不加** is_deleted 字段，跟随 Task 过滤：Task 被删除时其关联数据在用户端自动不可见，管理端通过 Task 详情查看

#### 3. 登录禁用检查

`app/api/v1/auth.py` 的 `login` 函数新增：验证密码后检查 `user.is_active`，若为 False 返回 403。

#### 4. 启动种子（使用 lifespan 替代已弃用的 on_event）

在 `app/main.py` 使用 FastAPI lifespan：

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup: 种子管理员
    db = SessionLocal()
    try:
        if not db.query(Admin).first():
            admin = Admin(username="admin", hashed_password=hash_password("admin123"))
            db.add(admin)
            db.commit()
    finally:
        db.close()
    yield

app = FastAPI(title="作业陪伴助手", version="0.1.0", lifespan=lifespan)
```

#### 5. 管理员登录接口

```python
# app/api/v1/admin/auth.py

@router.post("/login", response_model=Token)
def admin_login(body: AdminLogin, db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(Admin.username == body.username).first()
    if not admin or not verify_password(body.password, admin.hashed_password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")
    if not admin.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Admin account disabled")
    token = create_access_token(f"admin:{admin.id}")
    return Token(access_token=token)
```

### 路由注册

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

```python
# app/main.py 新增
from app.api.v1.admin import router as admin_router
app.include_router(admin_router, prefix="/api/v1")
```

### 数据库迁移

需要 Alembic 迁移：

1. 新增 `admins` 表
2. `users` 表新增 `is_active BOOLEAN DEFAULT TRUE` 和 `is_deleted BOOLEAN DEFAULT FALSE`
3. `families` 表新增 `is_deleted BOOLEAN DEFAULT FALSE`
4. `tasks` 表新增 `is_deleted BOOLEAN DEFAULT FALSE`

### CORS 配置

管理后台前端运行在 5174 端口，需在 `app/core/config.py` 和 `.env` 中添加：

```python
# config.py 默认值更新
CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:5174"]
```

### 新增文件完整清单

| 文件 | 说明 |
|------|------|
| `app/models/admin.py` | Admin 模型 |
| `app/schemas/admin.py` | AdminLogin, AdminOut, AdminPasswordChange |
| `app/schemas/pagination.py` | PaginationParams, PaginatedResponse[T] |
| `app/crud/admin.py` | get_admin_by_username, get_admin_by_id, seed_admin |
| `app/api/v1/admin/__init__.py` | 汇总子路由 |
| `app/api/v1/admin/auth.py` | 登录 / me / 改密 |
| `app/api/v1/admin/users.py` | 用户管理 CRUD |
| `app/api/v1/admin/families.py` | 家庭管理 CRUD |
| `app/api/v1/admin/tasks.py` | 作业管理 CRUD + stats |

### 修改文件完整清单

| 文件 | 修改内容 |
|------|----------|
| `app/models/__init__.py` | 导入 Admin |
| `app/models/user.py` | 新增 is_active, is_deleted 字段 |
| `app/models/family.py` | 新增 is_deleted 字段 |
| `app/models/task.py` | 新增 is_deleted 字段 |
| `app/main.py` | lifespan 种子 + 注册 admin 路由 |
| `app/core/config.py` | CORS_ORIGINS 加 5174 |
| `app/core/deps.py` | 新增 require_admin 依赖 |
| `app/crud/user.py` | 查询过滤 is_deleted |
| `app/crud/family.py` | 查询过滤 is_deleted |
| `app/crud/task.py` | 查询过滤 is_deleted |
| `app/api/v1/auth.py` | 登录检查 is_active |
| `.env` | CORS_ORIGINS 加 5174 |
