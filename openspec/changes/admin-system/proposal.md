# 提案：后端管理员系统

## 背景

当前系统只有 `parent` / `student` 两种角色，所有接口按 `family_id` 隔离。缺少全局管理视角，运营人员无法查看和管理全平台的用户、家庭、作业数据。

## 目标

新增管理员（admin）模块，提供 PC 端后台管理接口，支持对全平台用户、家庭、作业进行查看和管理。

## 范围

### 包含

1. **独立 admins 表** — 与 users 表隔离，管理员有独立的登录接口
2. **管理员认证** — `POST /api/v1/admin/auth/login`，JWT 复用现有 `core/security.py`
3. **管理员权限守卫** — `require_admin` 依赖，所有 `/admin/` 接口统一鉴权
4. **用户管理** — 全局用户列表（分页）、用户详情、修改角色、禁用/启用
5. **家庭管理** — 全局家庭列表（分页）、家庭详情（含成员）、删除家庭
6. **作业管理** — 全局任务列表（分页，支持按家庭/状态/日期筛选）、任务详情（含提交与听写条目）、删除任务
7. **分页机制** — 统一 `PaginationParams` + `PaginatedResponse` schema

### 不包含

- 管理员注册接口（管理员由数据库种子或命令行创建）
- 错题、听写条目的独立全局管理入口（通过任务详情查看）
- 管理员操作审计日志
- PC 端前端页面（仅提供后端 API）

## 技术方案概要

| 维度 | 方案 |
|------|------|
| 数据模型 | 新增 `Admin` 模型，独立 `admins` 表 |
| 认证 | 复用 JWT，新增 `require_admin` 依赖 |
| 接口前缀 | `/api/v1/admin/` |
| 分页 | `?page=1&page_size=20`，返回 `{total, items, page, page_size}` |
| 筛选 | 用户：按手机号/角色；家庭：按邀请码；任务：按家庭/状态/日期范围 |

## 数据模型

### admins 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID (PK) | 管理员 ID |
| username | VARCHAR(50) UNIQUE | 登录用户名 |
| hashed_password | VARCHAR(128) | 加密密码 |
| is_active | BOOLEAN DEFAULT TRUE | 是否启用 |
| created_at | DATETIME | 创建时间 |

## 接口清单

### 认证

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/admin/auth/login` | 管理员登录，返回 JWT |

### 用户管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/admin/users/` | 用户列表（分页 + 筛选） |
| GET | `/api/v1/admin/users/{id}` | 用户详情 |
| PATCH | `/api/v1/admin/users/{id}` | 修改用户（角色、启用状态） |
| DELETE | `/api/v1/admin/users/{id}` | 删除用户 |

### 家庭管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/admin/families/` | 家庭列表（分页 + 筛选） |
| GET | `/api/v1/admin/families/{id}` | 家庭详情（含成员列表） |
| DELETE | `/api/v1/admin/families/{id}` | 删除家庭 |

### 作业管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/admin/tasks/` | 任务列表（分页 + 筛选） |
| GET | `/api/v1/admin/tasks/{id}` | 任务详情（含提交、听写条目） |
| DELETE | `/api/v1/admin/tasks/{id}` | 删除任务 |

## 种子数据

通过 Alembic 迁移或启动脚本插入默认管理员：

- username: `admin` / password: `admin123`（首次登录后应修改）

## 影响分析

- **现有接口无影响** — 所有 `/admin/` 接口为新增，不修改现有路由
- **数据库** — 新增 `admins` 表，需 Alembic 迁移
- **依赖** — 复用现有 `core/security.py`（JWT、bcrypt），无新外部依赖
