# 周期作业计划 Backend Implementation Plan

> **For agentic workers:** REQUIRED FLOW: Use `fp-execute` to implement this plan task-by-task. Only task markers use checkbox syntax for tracking; substeps are plain ordered instructions.

**Goal:** 提供家庭隔离的周期作业计划生命周期与显式、幂等、可部分失败的作业实例补生成，同时保持现有 Task、听写、提交和批改链路兼容。

**Architecture:** 新增独立 HomeworkPlan 模板与模板词条；Task 仅以可空外键追踪来源。API 管理模板，materializer 按计划事务和统一行锁生成 Task/DictationItem 快照；`GET /tasks` 保持纯查询，客户端显式调用 materialize。

**Tech Stack:** Python 3.11+（`StrEnum`）、FastAPI、Pydantic v2、SQLAlchemy 2.x ORM、Alembic、pytest；生产数据库兼容 PostgreSQL/MySQL，测试使用 SQLite。

## Global Constraints

- API 前缀固定 `/api/v1`；计划路由为 `/homework-plans`，现有 `/tasks`、Submission、批改、听写契约不改。
- 管理端点使用 `require_parent`；materialize 使用 `get_current_user`；家庭来自 JWT 用户，未绑定家庭返回 400，跨家庭/不存在统一 404。
- `GET /tasks` 不写数据库，只返回普通 Task；学生不得读取或管理计划模板。
- 业务日期由 `settings.BUSINESS_TIMEZONE` 的 `ZoneInfo` 计算，默认 `Asia/Shanghai`；禁止用客户端日期或直接截断 UTC 时间戳。
- week/month 分别为含服务端今天的 7/30 个连续自然日；custom 起日不得早于今天且止日不得早于起日；范围最多 `MAX_HOMEWORK_PLAN_DAYS=366`，超限 422，不得静默截断。
- `HomeworkPlanUpdate` 虽使用 PATCH，但完整替换所有可编辑字段和词条，并必须携带 `updated_at`；冲突返回 409。已开始计划的 `start_date` 锁定。
- 计划词条去除首尾空白、不能为空，并在同一计划内按 Unicode `casefold()` 后唯一；请求顺序写入 `position`。
- `UNIQUE(source_plan_id, date)` 不含 `is_deleted`；普通任务的来源为 NULL；历史任务不回填。
- 创建/编辑/删除/生成按计划 ID 加 `SELECT FOR UPDATE`，锁内复查家庭、删除及范围。每计划本轮生成原子提交，不同计划故障隔离；不得吞掉非幂等键 IntegrityError。
- 快照复制 Task 的 type/title/desc/duration/subject 和有序听写内容；之后编辑、缩短或删除计划不得修改或删除已生成实例。
- 同步逐计划失败仍返回 HTTP 200；客户端错误只允许 `materialization_failed`、`plan_changed`、`plan_unavailable`，不得暴露 SQL、堆栈、JWT 或听写正文。
- 候选计划和模板词条一次查询、每计划一次已有日期查询，禁止逐日 exists 与逐日 commit；活动列表 generated_count 使用聚合查询。
- 不新增第三方依赖；迁移的新非空列必须带安全 server_default 或分阶段建立；现有测试全部保持通过。
- SQLite 测试不能代替 PostgreSQL 锁证明；并发验收测试在 `TEST_POSTGRES_URL` 未配置时 skip，配置时必须执行。

## File Structure

| Path | Action | Responsibility |
| --- | --- | --- |
| `app/core/config.py` | modify | 业务时区与计划最大天数配置 |
| `app/models/homework_plan.py` | create | 计划与模板听写持久化模型 |
| `app/models/task.py` | modify | Task 来源关系与唯一约束 |
| `app/models/__init__.py` | modify | 注册新模型供 Alembic 元数据发现 |
| `app/schemas/homework_plan.py` | create | 创建、完整更新、输出和同步契约 |
| `app/schemas/task.py` | modify | 兼容性暴露可空来源 ID |
| `app/crud/homework_plan.py` | create | 家庭范围计划 CRUD、锁定与活动聚合查询 |
| `app/services/__init__.py` | create | 服务包声明 |
| `app/services/homework_plan_materializer.py` | create | 日期展开、每计划事务、快照与结果汇总 |
| `app/api/v1/homework_plans.py` | create | 计划管理和显式同步 HTTP 编排 |
| `app/main.py` | modify | 注册计划路由 |
| `alembic/versions/<revision>_add_homework_plans.py` | create | 表、外键、索引和 Task 来源列迁移 |
| `tests/test_homework_plan_models.py` | create | 模型约束、迁移元数据与 Task 兼容测试 |
| `tests/test_homework_plan_schemas.py` | create | 日期预设和字段校验测试 |
| `tests/test_homework_plan_crud.py` | create | 生命周期、隔离、聚合与快照隔离测试 |
| `tests/test_homework_plan_materializer.py` | create | 日期算法、幂等、失败隔离及听写快照测试 |
| `tests/test_homework_plan_concurrency.py` | create | PostgreSQL 锁与竞争集成测试 |
| `tests/test_homework_plans_api.py` | create | 管理、权限、同步和纯 GET API 测试 |
| `tests/test_tasks.py` | modify | 一次性作业与 source_plan_id 回归 |
