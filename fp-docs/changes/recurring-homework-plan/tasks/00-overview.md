# Recurring Homework Plan Task Overview

## Canonical End Entrypoints

| End | Canonical entrypoint | Mode |
| --- | --- | --- |
| Backend | `backend/00-index.md` | split |
| Frontend | `frontend/00-index.md` | split |

## Cross-end Dependency Edges

| Downstream task | Depends on | Reason |
| --- | --- | --- |
| `frontend-005` | `backend-007` | 布置页提交分流依赖计划创建与生命周期 API 可用 |
| `frontend-007` | `backend-009` | 家长作业页同步编排与活动计划区依赖同步 API 和最终路由契约 |
| `frontend-008` | `backend-009` | 学生作业页补生成依赖允许学生调用的同步 API |
| `frontend-009` | `backend-008` | 编辑页面详情、权限与路由入口依赖计划详情/更新/删除 API |

## Cross-end Execution Stages

1. 后端 `backend-001`–`backend-009` 与前端基础 `frontend-001`–`frontend-004`、卡片 `frontend-006` 可按端内依赖推进。
2. `backend-007` 完成后执行 `frontend-005`，打通计划创建。
3. `backend-008` 完成后执行 `frontend-009`–`frontend-010`，打通详情、编辑与删除。
4. `backend-009` 完成后执行 `frontend-007`、`frontend-008`，打通家长与学生补生成流程。
5. 最后运行两端全量测试、H5 构建和浏览器视觉验收。

## Progress Totals

| End | Complete | Total |
| --- | ---: | ---: |
| Backend | 6 | 9 |
| Frontend | 0 | 10 |
| Overall | 6 | 19 |
