# 作业陪伴助手 (Study Buddy)

家庭作业协作工具 — 家长发布任务（含听写），学生完成，家长批改。

## 功能

- **家长端**：发布任务、配置听写词组与语速、批改作业、查看错题本
- **学生端**：查看今日任务、听写模式（本地 TTS 朗读）、提交作业、完成激励
- **家庭绑定**：6 位连接码关联家长与学生
- **角色分离**：家长创建/批改，学生执行/提交

## 技术栈

| 层 | 技术 |
|---|---|
| 后端 | FastAPI + SQLAlchemy 2.x + PostgreSQL + JWT |
| 客户端 | UniApp + Vue 3 + TypeScript + Pinia |
| TTS | 设备本地语音合成（APP: plus.speech, H5: SpeechSynthesis） |
| 同步 | 30 秒轮询 |

## 项目结构

```
study-buddy/
├── app/
│   ├── api/v1/         # 路由（auth, tasks, dictation, submissions, mistakes）
│   ├── core/           # 配置、JWT、依赖注入
│   ├── models/         # SQLAlchemy 模型
│   ├── schemas/        # Pydantic 请求/响应模型
│   ├── crud/           # 数据库操作
│   └── main.py         # 入口
├── tests/              # 单元测试（SQLite 内存数据库）
├── alembic/            # 数据库迁移
├── requirements.txt
├── client/             # UniApp 客户端
│   └── src/
│       ├── api/            # 请求封装与接口模块
│       ├── stores/         # Pinia 状态管理
│       ├── composables/    # 组合式函数（useTTS）
│       ├── pages/          # 页面（auth/parent/student）
│       └── utils/          # 工具函数
└── docs/               # 需求文档与设计规范
```

## 快速开始

### 前置要求

- Python 3.11+
- Node.js 18+
- PostgreSQL（默认 `postgres:root@localhost:5432/studybuddy`）

### 后端

```bash
# 创建虚拟环境
python -m venv venv

# 安装依赖
pip install -r requirements.txt         # Windows
# source venv/bin/activate && pip install -r requirements.txt  # Linux/Mac

# 数据库迁移
alembic upgrade head

# 启动开发服务器
python -m app.main
# 或
uvicorn app.main:app --reload

# 运行测试
rm -f test.db && python -m pytest tests/ -v
```

启动后访问 http://localhost:8000/docs 查看 API 文档。

### 客户端

```bash
cd client

# 安装依赖
npm install --legacy-peer-deps

# H5 开发模式
npm run dev:h5

# 微信小程序
npm run dev:mp-weixin

# 构建
npm run build:h5
```

## API 概览

| 模块 | 接口 | 说明 |
|------|------|------|
| 认证 | `POST /api/v1/auth/register` | 注册（自动创建家庭） |
| | `POST /api/v1/auth/login` | 登录 |
| | `GET /api/v1/auth/me` | 获取当前用户 |
| | `GET /api/v1/auth/family` | 获取家庭连接码 |
| | `POST /api/v1/auth/bind` | 家长绑定家庭 |
| | `POST /api/v1/auth/student-bind` | 学生绑定家庭 |
| 任务 | `POST /api/v1/tasks/` | 创建任务 |
| | `GET /api/v1/tasks/` | 查询任务列表 |
| | `GET /api/v1/tasks/{id}` | 获取任务详情 |
| | `PATCH /api/v1/tasks/{id}/status` | 更新任务状态 |
| | `DELETE /api/v1/tasks/{id}` | 删除任务 |
| 听写 | `POST /api/v1/dictation/` | 创建听写词组 |
| | `GET /api/v1/dictation/{task_id}` | 获取听写词组 |
| 提交 | `POST /api/v1/submissions/` | 提交作业 |
| | `GET /api/v1/submissions/` | 查询提交列表 |
| | `POST /api/v1/submissions/{id}/grade` | 批改作业 |
| 错题 | `GET /api/v1/mistakes/` | 查询错题列表 |
| | `POST /api/v1/mistakes/{id}/archive` | 归档错题 |

## 许可证

MIT
