# 部署配置 — 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 使用 Docker Compose 编排 Nginx + FastAPI + PostgreSQL，实现一键部署到阿里云 ECS。

**Architecture:** 三容器编排。Nginx 反向代理 API，FastAPI 通过 Gunicorn+Uvicorn 运行，PostgreSQL 数据持久化。

**Tech Stack:** Docker, Docker Compose, Nginx, Gunicorn, Uvicorn

**前置:** `2026-05-10-backend-business.md` 已完成

---

### Task 1: 后端 Dockerfile

**Files:**
- Create: `backend/Dockerfile`
- Create: `backend/.dockerignore`

- [ ] **Step 1: 创建 Dockerfile**

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000"]
```

- [ ] **Step 2: 创建 .dockerignore**

```
__pycache__
*.pyc
.venv
.env
alembic/versions/__pycache__
```

- [ ] **Step 3: 在 requirements.txt 中补充 gunicorn**

添加：
```
gunicorn==22.0.0
```

- [ ] **Step 4: 提交**

```bash
cd D:/01-code/study-buddy
git add backend/
git commit -m "feat(backend): add Dockerfile and .dockerignore"
```

---

### Task 2: Nginx 配置

**Files:**
- Create: `deploy/nginx/default.conf`
- Create: `deploy/nginx/Dockerfile`

- [ ] **Step 1: 创建 Nginx 配置**

```nginx
# deploy/nginx/default.conf
upstream api {
    server api:8000;
}

server {
    listen 80;
    server_name _;

    client_max_body_size 10M;

    location /api/ {
        proxy_pass http://api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /health {
        proxy_pass http://api;
    }

    location /docs {
        proxy_pass http://api;
    }

    location /openapi.json {
        proxy_pass http://api;
    }
}
```

- [ ] **Step 2: 创建 Nginx Dockerfile**

```dockerfile
# deploy/nginx/Dockerfile
FROM nginx:alpine
COPY default.conf /etc/nginx/conf.d/default.conf
```

- [ ] **Step 3: 提交**

```bash
cd D:/01-code/study-buddy
git add deploy/
git commit -m "feat(deploy): add Nginx config and Dockerfile"
```

---

### Task 3: Docker Compose

**Files:**
- Create: `docker-compose.yml`
- Create: `backend/.env.example`

- [ ] **Step 1: 创建 .env.example**

```
# backend/.env.example
DATABASE_URL=postgresql://postgres:postgres@db:5432/studybuddy
SECRET_KEY=change-me-in-production
```

- [ ] **Step 2: 创建 docker-compose.yml**

```yaml
# docker-compose.yml
version: "3.8"

services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: studybuddy
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  api:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://postgres:postgres@db:5432/studybuddy
      SECRET_KEY: change-me-in-production
    depends_on:
      db:
        condition: service_healthy
    ports:
      - "8000:8000"

  nginx:
    build: ./deploy/nginx
    ports:
      - "80:80"
    depends_on:
      - api

volumes:
  postgres_data:
```

- [ ] **Step 3: 提交**

```bash
cd D:/01-code/study-buddy
git add docker-compose.yml backend/.env.example
git commit -m "feat(deploy): add Docker Compose with Nginx, API, and PostgreSQL"
```

---

### Task 4: 本地验证部署

- [ ] **Step 1: 构建并启动**

```bash
cd D:/01-code/study-buddy
docker compose up --build
```

- [ ] **Step 2: 执行数据库迁移**

```bash
docker compose exec api alembic upgrade head
```

- [ ] **Step 3: 验证 API 可访问**

```bash
curl http://localhost/health
```

Expected: `{"status":"ok"}`

- [ ] **Step 4: 验证 OpenAPI 文档**

浏览器打开 `http://localhost/docs`，确认所有 API 端点可见。

- [ ] **Step 5: 提交最终状态**

```bash
cd D:/01-code/study-buddy
git add -A
git commit -m "chore: verify full stack deployment"
```
