# 作业陪伴助手 — 技术选型文档

> 日期：2026-05-10

## 1. 技术栈总览

| 层级 | 技术 | 说明 |
|------|------|------|
| 后端框架 | FastAPI (Python) | 异步支持好，自动生成 OpenAPI 文档，开发效率高 |
| 数据库 | PostgreSQL | 结构化数据，JSON 字段支持灵活扩展，生产可靠 |
| ORM | SQLAlchemy 2.x + Alembic | 类型安全，迁移管理完善 |
| 认证 | JWT (python-jose) | 无状态，UniApp 适配简单 |
| 图片存储 | 服务器本地文件系统 | 简单直接，通过 FastAPI StaticFiles 提供访问 |
| 客户端框架 | UniApp (Vue 3) | 一套代码编译 iOS/Android/H5 |
| 客户端语言 | TypeScript | 类型安全，减少运行时错误 |
| 状态管理 | Pinia | Vue 3 官方推荐 |
| HTTP 客户端 | uni.request 封装 | 统一拦截器处理 JWT 注入和错误 |
| TTS | 设备本地 TTS | uni.createInnerAudioContext + 平台原生 speech，无网络依赖 |
| 数据同步 | 客户端定时轮询 | 30 秒间隔，实现简单，作业场景延迟可接受 |
| 部署 | 阿里云 ECS | Ubuntu 22.04，Docker Compose 编排 |
| 进程管理 | Gunicorn + Uvicorn | 多 worker，生产稳定 |
| 反向代理 | Nginx | HTTPS 终止，静态文件服务，图片文件代理 |

## 2. 后端架构

### 目录结构
```
backend/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── auth.py        # 注册、登录、家庭绑定
│   │   │   ├── tasks.py       # 任务 CRUD
│   │   │   ├── dictation.py   # 听写配置
│   │   │   ├── submissions.py # 作业提交、图片上传
│   │   │   └── mistakes.py    # 错题本
│   ├── core/
│   │   ├── config.py          # 环境变量配置
│   │   ├── security.py        # JWT 工具
│   │   └── deps.py            # 依赖注入（当前用户等）
│   ├── models/                # SQLAlchemy 模型
│   ├── schemas/               # Pydantic 请求/响应模型
│   ├── crud/                  # 数据库操作层
│   └── main.py
├── alembic/                   # 数据库迁移
├── uploads/                   # 作业照片本地存储目录
├── requirements.txt
└── Dockerfile
```

### 关键数据模型
```
User          — id, role(parent/student), family_code, hashed_password
Family        — id, code(唯一连接码), parent_id, student_id
Task          — id, family_id, type(school/home), title, desc, duration, need_photo, status, created_at
DictationItem — id, task_id, content, speed, pause_interval
Submission    — id, task_id, photo_path, comment, is_correct, submitted_at
MistakeBook   — id, task_id, subject, archived
```

## 3. 客户端架构

### 目录结构
```
client/
├── src/
│   ├── pages/
│   │   ├── auth/              # 登录、注册、绑定
│   │   ├── parent/            # 家长端页面
│   │   │   ├── dashboard/     # 今日任务总览
│   │   │   ├── task-create/   # 发布任务
│   │   │   ├── dictation-config/ # 听写配置
│   │   │   ├── grading/       # 作业批改
│   │   │   └── mistake-book/  # 错题本
│   │   └── student/           # 学生端页面
│   │       ├── home/          # 今日任务看板
│   │       ├── dictation/     # 听写模式
│   │       └── submit/        # 拍照提交
│   ├── stores/
│   │   ├── auth.ts
│   │   ├── tasks.ts
│   │   └── sync.ts            # 轮询逻辑
│   ├── api/                   # 接口封装
│   ├── composables/
│   │   └── useTTS.ts          # 本地 TTS 封装
│   └── utils/
├── manifest.json
└── pages.json
```

### 角色路由分离
- 登录后根据 `user.role` 跳转不同首页
- `parent/*` 路由守卫：仅 role=parent 可访问
- `student/*` 路由守卫：仅 role=student 可访问

## 4. 关键技术实现

### 4.1 本地 TTS（听写功能）

```typescript
// composables/useTTS.ts
// 使用 uni.createSpeechSynthesizer (APP) 或 SpeechSynthesis API (H5)
// 支持：语速控制、词间停顿、暂停/继续/跳词
```

各平台映射：
- iOS/Android App：`plus.speech` (uni-app 原生插件)
- H5：`window.speechSynthesis`
- 微信小程序：`wx.createSpeechRecognizer`（如需扩展）

### 4.2 轮询同步

```typescript
// stores/sync.ts
// 应用进入前台时启动，退到后台时暂停
// 间隔 30s，仅在 student 首页和 parent dashboard 激活
// 返回数据与本地 store diff，仅在有变化时触发 UI 更新
```

### 4.3 图片上传与访问

- 上传：`uni.chooseImage` → 压缩到 < 2MB → `multipart/form-data` POST
- 存储：`backend/uploads/{family_id}/{task_id}/{timestamp}.jpg`
- 访问：Nginx 代理 `/uploads/` 路径，需携带 JWT 验证（通过查询参数传 token）

### 4.4 离线缓存

- 使用 `uni.setStorageSync` 缓存当日任务列表
- 检测到网络断开时切换离线模式，操作记录写入本地队列
- 网络恢复时批量同步本地队列到服务器

## 5. 部署方案

```
阿里云 ECS (Ubuntu 22.04)
├── Docker Compose
│   ├── nginx         # 443/80，SSL 证书（Let's Encrypt）
│   ├── api           # FastAPI / Gunicorn + Uvicorn
│   └── db            # PostgreSQL 15
├── /data/uploads/    # 挂载卷，持久化图片
└── /data/postgres/   # 挂载卷，持久化数据库
```

### 备份策略
- PostgreSQL：每日 `pg_dump` 定时任务，保留 30 天
- uploads 目录：每周同步备份到阿里云 OSS（可选）

## 6. API 设计原则

- 版本前缀：`/api/v1/`
- 认证：所有接口需 `Authorization: Bearer <token>`（除登录/注册）
- 错误码：遵循 HTTP 语义（401 未认证，403 无权限，404 不存在，422 参数错误）
- 图片访问：`GET /uploads/{path}?token=<jwt>`

## 7. 技术决策记录

| 决策 | 选择 | 放弃的选项 | 原因 |
|------|------|-----------|------|
| TTS | 设备本地 | 讯飞/阿里云 TTS | 无网络依赖，零成本，学生端离线场景友好 |
| 同步 | 轮询 30s | WebSocket / SSE | 实现简单，作业场景不需要秒级实时性 |
| 图片存储 | 服务器本地 | 阿里云 OSS | 减少外部依赖，初期规模图片量可控 |
| 数据库 | PostgreSQL | SQLite / MongoDB | 多端并发写安全，云部署成熟，结构化数据契合 |
| 认证 | JWT | Session + Redis | 无状态，UniApp 客户端适配简单 |
