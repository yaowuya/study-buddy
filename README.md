# 作业陪伴助手 (Study Buddy)

家庭作业协作工具 — 家长发布任务（含听写），学生完成，家长批改。

当前版本：**1.2.0**

## 功能

- **家长端**：发布任务、配置听写词组与语速、批改作业、查看错题本、作业历史
- **学生端**：查看今日任务、听写模式（本地 TTS 朗读）、提交作业、完成激励
- **周期作业计划**：按周、月或自定义日期每天生成任务，支持补生成、编辑未来任务和停止计划
- **管理后台**：用户管理、家庭管理、作业管理、仪表盘统计（Web PC 端）
- **家庭绑定**：6 位连接码关联家长与学生
- **角色分离**：家长创建/批改，学生执行/提交

## 技术栈

| 层 | 技术 |
|----|------|
| 后端 | FastAPI + SQLAlchemy 2.x + MySQL + JWT |
| 客户端 | UniApp + Vue 3 + TypeScript + Pinia |
| 管理后台 | Vue 3 + Ant Design Vue 4 + Vite + Pinia |
| TTS | 百度 TTS（APP）/ SpeechSynthesis（H5） |
| 同步 | 30 秒轮询 |
| 部署 | Docker + Gunicorn + Uvicorn |

## 项目结构

```
study-buddy/
├── app/                    # 后端 FastAPI 应用
│   ├── api/v1/             # 路由（auth, tasks, dictation, homework_plans, submissions, mistakes）
│   │   └── admin/          # 管理端路由（users, families, tasks, auth）
│   ├── core/               # 配置、JWT、依赖注入
│   ├── models/             # SQLAlchemy 模型
│   ├── schemas/            # Pydantic 请求/响应模型
│   ├── crud/               # 数据库操作
│   ├── services/           # 服务层（homework_plan_materializer）
│   └── main.py             # 入口（含管理后台静态文件挂载）
├── alembic/                # 数据库迁移脚本
├── tests/                  # 单元测试（SQLite 内存数据库）
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── client/                 # UniApp 移动端
│   └── src/
│       ├── api/            # 请求封装与接口模块
│       ├── stores/         # Pinia 状态管理
│       ├── pages/          # 页面（auth/parent/student）
│       └── utils/          # 工具函数
├── admin/                  # 管理后台前端源码（Vue 3）
│   └── src/
│       ├── api/            # 管理端接口封装
│       ├── views/          # 页面（login/dashboard/users/families/tasks）
│       ├── stores/         # auth store
│       └── router/         # 路由
├── static/
│   └── admin-dist/         # 管理后台构建产物（随代码提交，后端直接托管）
└── docs/                   # 需求文档与设计规范
```

## 快速开始

### 前置要求

- Python 3.11+
- Node.js 18+
- MySQL 8.0+（默认连接：`mysql+pymysql://root:root@localhost:3306/studybuddy`）

### 后端

```bash
# 创建虚拟环境并激活
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/Mac

# 安装依赖
pip install -r requirements.txt

# 配置环境变量（复制示例文件后按需修改）
cp .env.example .env

# 创建数据库
mysql -u root -p -e "CREATE DATABASE studybuddy DEFAULT CHARACTER SET utf8mb4;"

# 执行数据库迁移
alembic upgrade head

# 启动开发服务器
uvicorn app.main:app --reload
```

启动后：
- API 文档：http://localhost:8000/docs
- 管理后台：http://localhost:8000/admin/（默认账号 `admin`，密码由 `ADMIN_INITIAL_PASSWORD` 环境变量控制）

### 管理后台（仅开发时需要构建）

```bash
cd admin
npm install
npm run dev        # 开发模式（http://localhost:5174，代理到后端）
npm run build      # 构建 → 输出到 static/admin-dist/，提交即可生效
```

### UniApp 客户端

```bash
cd client
npm install --legacy-peer-deps
npm run dev:h5          # H5 开发
npm run dev:mp-weixin   # 微信小程序开发
npm run build:h5        # H5 构建
```

### Docker 部署

Docker 部署后端 API 与已提交的 `static/admin-dist` 管理后台构建产物；UniApp 客户端需要从 `client/` 单独构建。Compose 继续连接外部 MySQL，不包含数据库服务。

镜像名固定为 `studybuddy-api:1.2.0`，容器名固定为 `studybuddy-api`。

```bash
# 在服务器上
mkdir -p /data/logs/studybuddy

# 配置生产环境变量
cp .env.example .env
# 修改 .env 中的 DATABASE_URL、SECRET_KEY、ADMIN_INITIAL_PASSWORD 等
# DATABASE_URL 示例：mysql+pymysql://studybuddy:请替换为强密码@host.docker.internal:3306/studybuddy

docker compose up -d --build
docker compose ps
curl http://localhost:8000/health
```

预期健康响应：

```json
{"status":"ok","version":"1.2.0"}
```

#### 从旧版本升级

```bash
git pull
pip install -r requirements.txt   # 非 Docker 部署
docker compose down
docker compose up -d --build
docker compose ps
```

## API 概览

### 用户端

| 模块 | 接口 | 说明 |
|------|------|------|
| 认证 | `POST /api/v1/auth/register` | 注册（家长自动创建家庭） |
| | `POST /api/v1/auth/login` | 登录 |
| | `GET /api/v1/auth/me` | 获取当前用户 |
| | `POST /api/v1/auth/bind` | 家长绑定家庭 |
| | `POST /api/v1/auth/student-bind` | 学生绑定家庭 |
| 任务 | `POST /api/v1/tasks/` | 创建任务 |
| | `GET /api/v1/tasks/` | 查询任务列表 |
| | `PATCH /api/v1/tasks/{id}/status` | 更新任务状态 |
| | `DELETE /api/v1/tasks/{id}` | 删除任务 |
| 作业计划 | `POST /api/v1/homework-plans/` | 创建周期作业计划 |
| | `GET /api/v1/homework-plans/` | 查询当前家庭活动计划 |
| | `GET /api/v1/homework-plans/{id}` | 获取计划详情 |
| | `PATCH /api/v1/homework-plans/{id}` | 更新未来任务模板 |
| | `DELETE /api/v1/homework-plans/{id}` | 停止计划后续生成 |
| | `POST /api/v1/homework-plans/materialize` | 补生成截至今天的计划任务 |
| 听写 | `POST /api/v1/dictation/` | 创建听写词组 |
| | `GET /api/v1/dictation/{task_id}` | 获取听写词组 |
| 提交 | `POST /api/v1/submissions/` | 提交作业 |
| | `POST /api/v1/submissions/{id}/grade` | 批改作业 |
| 错题 | `GET /api/v1/mistakes/` | 查询错题列表 |
| | `POST /api/v1/mistakes/{id}/archive` | 归档错题 |

### 管理端（需管理员 JWT）

| 模块 | 接口 | 说明 |
|------|------|------|
| 认证 | `POST /api/v1/admin/auth/login` | 管理员登录 |
| | `GET /api/v1/admin/auth/me` | 获取当前管理员 |
| | `PATCH /api/v1/admin/auth/password` | 修改密码 |
| 用户 | `GET /api/v1/admin/users/` | 用户列表（分页+筛选） |
| | `PATCH /api/v1/admin/users/{id}` | 修改用户角色/状态 |
| | `DELETE /api/v1/admin/users/{id}` | 软删除用户 |
| 家庭 | `GET /api/v1/admin/families/` | 家庭列表 |
| | `DELETE /api/v1/admin/families/{id}` | 软删除家庭（级联） |
| 作业 | `GET /api/v1/admin/tasks/` | 任务列表（分页+筛选） |
| | `GET /api/v1/admin/tasks/stats` | 仪表盘统计数据 |
| | `DELETE /api/v1/admin/tasks/{id}` | 软删除任务 |

## 许可证

MIT
