# AGENTS.md

This file provides guidance to Codex (Codex.ai/code) when working with code in this repository.

## 开发规范

- Git commit message 使用中文

## Project Overview

作业陪伴助手 (Study Buddy) — a family education collaboration tool. Parents assign tasks (including dictation with TTS), students complete them, parents grade. Two roles: parent (task creator/reviewer) and student (task executor).

## Development Commands

### Backend (FastAPI)

```bash
# Install deps (venv already at venv/)
pip install -r requirements.txt

# Run dev server
uvicorn app.main:app --reload

# Run all tests (uses SQLite in-memory, no PG needed)
rm -f test.db && python -m pytest tests/ -v

# Run single test
python -m pytest tests/test_api.py::test_register_parent -v

# Database migration
alembic revision --autogenerate -m "description"
alembic upgrade head
```

### PostgreSQL Connection

- User: `postgres`, Password: `root`, DB: `studybuddy`, Port: 5432
- Config in `app/core/config.py` (overridable via `.env`)

## Backend Architecture

Layered structure with strict separation: **models → schemas → crud → api**

```
app/
├── api/v1/        # FastAPI routers (auth, tasks, dictation, submissions, mistakes)
├── core/          # config.py, security.py (JWT/bcrypt), deps.py (DI)
├── models/        # SQLAlchemy 2.x models (User, Family, Task, DictationItem, Submission, Mistake)
├── schemas/       # Pydantic v2 request/response models
├── crud/          # Database operations (one file per model)
└── database.py    # Engine/session + Base class
```

**Key patterns:**
- All API endpoints use JWT auth via `Depends(get_current_user)`, `Depends(require_parent)`, or `Depends(require_student)` from `core/deps.py`
- All data is scoped to `user.family_id` — cross-family access returns 404
- UUID primary keys everywhere (PostgreSQL + SQLAlchemy `Mapped[uuid.UUID]`)
- Alembic for migrations; models registered via `models/__init__.py` imports in `alembic/env.py`

**API prefix:** `/api/v1/`

## Client (Planned, not yet implemented)

UniApp (Vue 3 + TypeScript + Pinia). See `docs/tech-stack.md` and `docs/superpowers/plans/2026-05-10-client-*.md`.

## Design Specs

- `docs/requirements.md` — full product requirements from Stitch UI analysis
- `docs/tech-stack.md` — technology choices and rationale
- `docs/superpowers/specs/2026-05-10-study-buddy-design.md` — design spec
- `docs/superpowers/plans/` — implementation plans (5 files)

## Apifox MCP Notes

Project: **学伴app** (ID: `8244027`), configured in `.mcp.json` as `apifox-new-mcp`.

**Creating endpoints — critical rules:**
1. **Must include `headers` parameter** with `{"X-Project-Id": "8244027"}` in every `createHttpEndpoint` call, otherwise returns validation error
2. **Cannot omit `body` parameter** — at minimum provide `method`, `name`, `path`, `tags`
3. **`requestBody`, `parameters`, `responses` fields accept JSON strings** (not objects) — stringify complex schemas before passing
4. **Locale**: add `queryParams: {"locale": "zh-CN"}` for Chinese UI
5. **Created endpoints are skeletons** — they get path/method/tags but request/response schemas are empty. To populate full schemas, import `openapi.json` via Apifox UI (导入 → OpenAPI/Swagger) instead of creating one-by-one
6. **Parallel calls fail** — `headers` param gets dropped when multiple `createHttpEndpoint` calls are made in parallel. Create endpoints one at a time sequentially
7. **500 errors** on complex `requestBody`/`responses` — simplify to minimal body first, then update with `updateHttpEndpoint` if needed
