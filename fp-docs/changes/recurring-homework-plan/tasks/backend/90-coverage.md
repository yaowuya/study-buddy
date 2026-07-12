# Coverage Matrix

| Source | Requirement / Boundary | Tasks | Verification |
| --- | --- | --- | --- |
| `proposal.md` §1 | 独立计划/词条模型，Task 可空来源与每计划日期唯一 | `backend-001`, `backend-002` | `python -m pytest tests/test_homework_plan_models.py -v` |
| `proposal.md` §2 | 家长创建、活动列表、详情、完整编辑、删除；家庭隔离 | `backend-004`, `backend-007`, `backend-008` | `python -m pytest tests/test_homework_plan_crud.py tests/test_homework_plans_api.py -v` |
| `proposal.md` §2 | 编辑/删除不改变已生成快照 | `backend-004`, `backend-008` | `python -m pytest tests/test_homework_plans_api.py::test_patch_conflict_and_snapshot_isolation tests/test_homework_plans_api.py::test_delete_is_idempotent_and_stops_future_generation -v` |
| `proposal.md` §3 | 截至 min(end,today) 补齐全部遗漏，幂等并发安全 | `backend-005`, `backend-006`, `backend-009` | `python -m pytest tests/test_homework_plan_materializer.py -v`; `TEST_POSTGRES_URL="$DATABASE_URL" python -m pytest tests/test_homework_plan_concurrency.py -v` |
| `proposal.md` §3 | Task 字段与听写词条生成时复制 | `backend-005` | `python -m pytest tests/test_homework_plan_materializer.py::test_backfills_missing_dates_idempotently -v` |
| `proposal.md` §3 | 部分失败保留既有成果、下次重试且不阻塞展示 | `backend-005`, `backend-009` | `python -m pytest tests/test_homework_plans_api.py::test_materialize_returns_structured_partial_result -v` |
| `proposal.md` §4 | 今日仍走 Task API；week/month/custom 服务端日期规则；听写校验 | `backend-003`, `backend-007` | `python -m pytest tests/test_homework_plan_schemas.py tests/test_tasks.py -v` |
| `proposal.md` §5 | 活动计划卡所需状态、范围、剩余/总日、生成数、今日状态和听写数据 | `backend-003`, `backend-004`, `backend-007` | `python -m pytest tests/test_homework_plans_api.py::test_parent_lists_and_gets_plan -v` |
| `proposal.md` §6 | 完整编辑、已开始起日锁定、乐观冲突、删除语义 | `backend-003`, `backend-004`, `backend-008` | `python -m pytest tests/test_homework_plans_api.py -k 'patch or delete' -v` |
| `design/backend/01-domain-and-api.md` §1–3 | 模板/实例分离、显式同步、按计划事务、模型与迁移 | `backend-001`, `backend-002`, `backend-005`, `backend-009` | `python -m pytest tests/test_homework_plan_models.py tests/test_homework_plan_materializer.py tests/test_homework_plans_api.py -v` |
| `design/backend/01-domain-and-api.md` §4 | Create/Update/Out/同步 Schema 精确契约 | `backend-003` | `python -m pytest tests/test_homework_plan_schemas.py -v` |
| `design/backend/01-domain-and-api.md` §5–6 | 六个端点、角色、家庭、400/403/404/409/422、同步 200 | `backend-007`, `backend-008`, `backend-009` | `python -m pytest tests/test_homework_plans_api.py -v` |
| `design/backend/01-domain-and-api.md` §7–8 | Task/Submission/Dictation 兼容，OpenAPI 路由注册 | `backend-003`, `backend-007`, `backend-009` | `rm -f test.db && python -m pytest tests/ -v` |
| `design/backend/02-materialization-and-consistency.md` §1 | 配置业务时区和服务端 today | `backend-001`, `backend-003`, `backend-007`, `backend-009` | `python -m pytest tests/test_homework_plan_schemas.py::test_business_date_uses_configured_timezone -v` |
| `design/backend/02-materialization-and-consistency.md` §2–4 | 候选含过期遗漏计划、日期集合差、无 N+1、完整快照 | `backend-005` | `python -m pytest tests/test_homework_plan_materializer.py -v` |
| `design/backend/02-materialization-and-consistency.md` §5 | 单计划原子、不同计划隔离、失败 Session 可继续 | `backend-005` | `python -m pytest tests/test_homework_plan_materializer.py -k 'rollback or failure' -v` |
| `design/backend/02-materialization-and-consistency.md` §6–8 | 统一行锁、唯一冲突、编辑/删除竞争提交顺序 | `backend-006` | `TEST_POSTGRES_URL="$DATABASE_URL" python -m pytest tests/test_homework_plan_concurrency.py -v` |
| `design/backend/02-materialization-and-consistency.md` §9 | 缩短不删实例、延长可生成、未开始可改起日 | `backend-004`, `backend-005`, `backend-008` | `python -m pytest tests/test_homework_plan_crud.py tests/test_homework_plan_materializer.py -k 'range or snapshot' -v` |
| `design/backend/02-materialization-and-consistency.md` §10 | 同步汇总和稳定错误码，部分失败 HTTP 200 | `backend-003`, `backend-005`, `backend-009` | `python -m pytest tests/test_homework_plans_api.py::test_materialize_returns_structured_partial_result -v` |
| `design/backend/02-materialization-and-consistency.md` §11–12 | 聚合/N+1/范围保护、结构化脱敏日志 | `backend-003`, `backend-004`, `backend-005` | `python -m pytest tests/test_homework_plan_crud.py tests/test_homework_plan_materializer.py -k 'query_count or maximum or failure' -v` |
| Backend boundary | 数据模型与迁移 | `backend-001`, `backend-002` | `python -m pytest tests/test_homework_plan_models.py -v` |
| Backend boundary | service/business logic | `backend-004`, `backend-005`, `backend-006` | `python -m pytest tests/test_homework_plan_crud.py tests/test_homework_plan_materializer.py -v` |
| Backend boundary | serializer/schema | `backend-003` | `python -m pytest tests/test_homework_plan_schemas.py -v` |
| Backend boundary | API handler/router | `backend-007`, `backend-008`, `backend-009` | `python -m pytest tests/test_homework_plans_api.py -v` |
| Backend boundary | IAM/permission/family isolation | `backend-007`, `backend-008`, `backend-009` | `python -m pytest tests/test_homework_plans_api.py -k 'student or family or cross' -v` |
| Backend boundary | 导入、兼容和全量回归 | `backend-001`, `backend-007`, `backend-009` | `rm -f test.db && python -m pytest tests/ -v` |

## Design Gaps

- None. 后端设计已覆盖 proposal 的后端范围；前端条件展示与页面职责由 frontend plan 所有，不在本计划重复。
