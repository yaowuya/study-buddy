# 周期作业计划 — Frontend Context

## Goal

在不改变普通 Task 执行、提交、批改语义的前提下，为 UniApp 家长端加入周期计划创建、活动计划概览、完整编辑与删除；家长和学生进入作业页时先触发服务端补生成，再读取普通作业。新增 UI 延续现有 organic 视觉，活动计划只出现在家长 Dashboard 底部。

## Current Source Baseline

- 客户端为 Vue 3 + TypeScript + UniApp + Pinia；`client/package.json` 只有 `type-check` 与各平台 build/dev 命令，尚无单元测试脚本或测试依赖。
- `client/src/api/request.ts` 统一负责 `/api/v1` 请求、JWT 与错误抛出；新增 API 必须复用它。
- `client/src/stores/tasks.ts` 仅保存普通作业及今日缓存；不得混入模板。
- `task-create.vue` 当前始终 `POST /tasks`，听写关闭时仍渲染禁用内容；需要条件渲染和多日分流。
- `dashboard.vue` 当前 `onShow` 直接拉今日作业并启动 30 秒同步；新增流程须先 materialize，且不得改造现有 Hero、Task 卡和 BottomNav。
- `student/home.vue` 当前只取普通作业；只增加 materialize，不读取管理数据。
- `ConfirmModal.vue`、`BottomNav.vue` 和 `variables.scss` 是现有交互/视觉事实。
- FeaturePilot 的 `settings/agent.md`、`settings/frontend.md`、`settings/prototype-style.md` 均不存在；视觉依据为确认的 `prototype.html`、前端设计和上述现有源码。

## Global Constraints

1. API 前缀为 `/homework-plans`（`request` 已统一添加 `/api/v1`）；管理端点仅家长使用，`POST /homework-plans/materialize` 家长、学生均可用，客户端不发送 `family_id`。
2. `GET /tasks` 保持纯查询。作业页严格执行 `await materialize → fetchTodayTasks`；materialize 失败或部分失败仅警告，不阻断缓存和普通作业查询。
3. 今日范围仍使用现有 `createTask`，听写仍使用现有第二步 `createDictationItems`；week/month/custom 使用原子 `createHomeworkPlan`，不得创建模板型 Task。
4. 计划状态独立 Pinia Store；所有 loading 在 `finally` 清理；materialize 重入时复用同一 Promise；登出同步清空计划状态。
5. 日期按本地自然日生成 `YYYY-MM-DD`，不得用 UTC `toISOString()` 决定“今天”；week 为含今天 7 天、month 为含今天 30 天，服务端仍是权威。
6. custom 校验：起止完整、开始不早于今天、结束不早于开始；标题非空；时长为空或正整数；听写开启至少一个 trim 后词条。
7. 编辑使用详情返回的实际日期和 `updated_at`；已开始计划禁用开始日期；PATCH 是完整替换；409 不覆盖表单，422 映射字段错误。
8. 听写关闭时条件体不进入渲染树；编辑中关闭只影响提交词条，未保存前重新开启恢复本地词条。
9. 不新增设计 token。复用 `variables.scss`、Dashboard 科目映射、24px 卡片圆角/内边距、`0 12px 32px rgba(0,0,0,.06)` 阴影、24px 页面水平边距和现有表单/按钮模式。
10. Dashboard 保留 AppBar、Hero `40px 120px 40px 120px`、mint 背景、32px padding、家庭码、Task DOM 顺序和悬浮 BottomNav；计划区只能追加在所有具体作业之后。
11. 编辑页是无 BottomNav 的二级全屏页；返回和删除均复用 `ConfirmModal`；保存/删除期间禁用返回及重复操作。
12. 每个实现任务按 Red → Green → type-check/build → Visual/UX Checks → 中文 commit 执行；不得在红测失败前写产品实现。

## Planned File Structure

```text
client/
├── package.json                              # 增加 Vitest 脚本/依赖
├── vite.config.ts                           # Vitest + @ alias 配置
├── src/
│   ├── api/homework-plans.ts                # 计划 CRUD/materialize 类型与请求
│   ├── stores/homework-plans.ts             # 独立计划状态
│   ├── utils/local-date.ts                   # 本地日期与范围纯函数
│   ├── components/DictationConfig.vue        # 条件听写配置
│   ├── components/HomeworkPlanCard.vue       # 纯展示计划卡
│   ├── pages/parent/task-create.vue          # 时间范围、校验、提交分流
│   ├── pages/parent/dashboard.vue            # 同步编排、活动计划区、删除确认
│   ├── pages/parent/homework-plan-edit.vue   # 完整编辑/删除/脏状态
│   ├── pages/student/home.vue                # 非阻塞 materialize
│   ├── stores/auth.ts                        # logout 清计划状态
│   └── pages.json                            # 编辑页路由
└── tests/
    ├── setup.ts
    ├── api/homework-plans.spec.ts
    ├── stores/homework-plans.spec.ts
    ├── utils/local-date.spec.ts
    ├── components/DictationConfig.spec.ts
    ├── components/HomeworkPlanCard.spec.ts
    └── pages/{task-create,dashboard,student-home,homework-plan-edit}.spec.ts
```

## Execution Boundary

任务只修改客户端与客户端测试。后端须先提供 `05-interfaces.md` 中 API 契约；若实际 OpenAPI 字段或路径不同，先更新接口账本并调整消费者测试，不得猜测兼容层。普通作业、提交、批改、历史页和现有单次编辑页只做回归验证，不重构。
