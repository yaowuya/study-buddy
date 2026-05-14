# Backend — Study Buddy (作业陪伴助手)

FastAPI + SQLAlchemy 2.x + PostgreSQL

## 快速开始

```bash
# 安装依赖（venv 已在 backend/venv）
./venv/Scripts/pip install -r requirements.txt

# 启动开发服务器
./venv/Scripts/uvicorn app.main:app --reload
```

## 数据库

**PostgreSQL 连接信息**

| 参数 | 值 |
|------|-----|
| User | postgres |
| Password | root |
| DB | studybuddy |
| Port | 5432 |

配置文件：`app/core/config.py`，可通过 `.env` 覆盖。

### 数据库迁移（Alembic）

```bash
# 检测 models 变化，自动生成迁移文件
./venv/Scripts/alembic revision --autogenerate -m "描述变更内容"

# 将迁移应用到数据库（升级到最新）
./venv/Scripts/alembic upgrade head

# 回滚一步
./venv/Scripts/alembic downgrade -1

# 查看当前版本
./venv/Scripts/alembic current

# 查看迁移历史
./venv/Scripts/alembic history
```

**典型工作流：** 修改 `app/models/` → `autogenerate` 生成迁移文件 → `upgrade head` 应用到数据库

迁移文件位于 `alembic/versions/`，每个文件包含 `upgrade()` 和 `downgrade()` 两个函数。

## 测试

```bash
# 运行全部测试（使用 SQLite 内存数据库，无需 PG）
rm -f test.db && ./venv/Scripts/python -m pytest tests/ -v

# 运行单个测试
./venv/Scripts/python -m pytest tests/test_api.py::test_register_parent -v
```

## 项目结构

```
app/
├── api/v1/        # FastAPI 路由（auth, tasks, dictation, submissions, mistakes）
├── core/          # config.py, security.py (JWT/bcrypt), deps.py (依赖注入)
├── models/        # SQLAlchemy 2.x 模型（User, Family, Task, DictationItem, Submission, Mistake）
├── schemas/       # Pydantic v2 请求/响应模型
├── crud/          # 数据库操作（每个模型一个文件）
└── database.py    # Engine/Session + Base 类
```

**API 前缀：** `/api/v1/`

**关键约定：**
- 所有接口通过 `Depends(get_current_user)` / `Depends(require_parent)` / `Depends(require_student)` 做 JWT 鉴权
- 所有数据按 `user.family_id` 隔离，跨家庭访问返回 404
- 主键统一使用 UUID
