# Frontend Coverage and Verification

## Proposal Coverage

| Requirement | Owner tasks | Verification evidence |
| --- | --- | --- |
| 今日默认；week 7 日、month 30 日、custom 校验；今日/计划分流 | frontend-001, frontend-002, frontend-005 | local-date 与 task-create specs；H5 四范围检查 |
| 听写默认关闭且关闭时 Body 完全隐藏；开启至少一词 | frontend-004, frontend-005, frontend-010 | DictationConfig 与两页面 specs；可访问树确认 |
| Dashboard 底部活动计划卡、进度、状态、编辑和低强调删除 | frontend-006, frontend-007 | card/dashboard specs；mobile/tablet visual check |
| 完整编辑；started 锁开始日期；只影响未来；脏返回；删除保留实例 | frontend-009, frontend-010 | edit specs；ConfirmModal 文案与网络请求检查 |
| 家长/学生加载先补生成；失败不阻塞普通作业 | frontend-003, frontend-007, frontend-008 | Store 与页面 call-order/failure specs |
| 学生不查看/管理模板；布置页不展示活动计划 | frontend-005, frontend-008 | 页面 DOM 负断言与 H5 角色验收 |
| 普通 Task、听写、提交、批改保持兼容 | frontend-005, frontend-007, frontend-008 | 全测试/type-check/build；现有角色流程烟测 |

## Design Contract Coverage

| Contract | Owner tasks |
| --- | --- |
| FAPI-01/FAPI-02 | frontend-002, frontend-005, frontend-010 |
| FSTORE-01/FSTORE-02 | frontend-003, frontend-007, frontend-008, frontend-009 |
| FCOMP-01 | frontend-004, frontend-005, frontend-010 |
| FCOMP-02 | frontend-006, frontend-007 |
| FROUTE-01/FROUTE-02/FROUTE-03 | frontend-005, frontend-007, frontend-009, frontend-010 |
| FUX-01/FUX-02/FUX-03 | frontend-001, frontend-005, frontend-007, frontend-010 |
| FSTYLE-01/FSTYLE-02/FSTYLE-03 | frontend-004–frontend-010 |

## Automated Verification Matrix

| Layer | Exact command | Expected result |
| --- | --- | --- |
| Date utility | `cd client && npm test -- --run tests/utils/local-date.spec.ts` | local natural-day edge cases pass |
| API | `cd client && npm test -- --run tests/api/homework-plans.spec.ts` | six exact request mappings pass |
| Store | `cd client && npm test -- --run tests/stores/homework-plans.spec.ts` | flags, warning, dedupe, mutations and reset pass |
| Components | `cd client && npm test -- --run tests/components/DictationConfig.spec.ts tests/components/HomeworkPlanCard.spec.ts` | rendering, events, busy and semantic negatives pass |
| Pages | `cd client && npm test -- --run tests/pages/task-create.spec.ts tests/pages/dashboard.spec.ts tests/pages/student-home.spec.ts tests/pages/homework-plan-edit.spec.ts` | flows, ordering, role boundaries, errors and confirmations pass |
| Full client tests | `cd client && npm test -- --run` | all test files pass; no unhandled rejection |
| Types | `cd client && npm run type-check` | exit 0, no Vue/TS diagnostics |
| Production bundle | `cd client && npm run build:h5` | exit 0 and H5 output emitted |

## H5 Visual / UX Runbook

1. Run `cd client && npm run dev:h5`; open parent task-create at 375×812 and 768×1024.
2. Verify today default, week/month summaries, custom-only date controls, inline invalid-date messages and conditional dictation tree; inspect no horizontal overflow.
3. Publish today and confirm only `/tasks` (+ dictation when enabled); publish week/month/custom and confirm only `POST /homework-plans`, then Dashboard navigation and exact Toast.
4. On parent Dashboard, capture baseline/after comparison for AppBar, Hero asymmetric radius/mint/32px, family card, Task order/badges and BottomNav. Scroll after all Tasks to plan section; exercise loading, empty, error, cached warning and data.
5. Inspect a long-title/multi-metadata plan card: status remains visible, badges are flex children, metadata wraps, desc clamps to two lines, empty desc leaves no gap, progress and subject tint match server data/current Task palette.
6. Trigger materialize failure and confirm old Tasks remain interactive and warning occurs once; ensure 30-second task refresh sends no materialize request.
7. Open student Home: network order is materialize then tasks; no list/detail plan request and no plan UI.
8. Open edit page: no empty-form flash or BottomNav; validate started lock, dirty back modal, disabled dictation word restore, save payload/token, 409 reload, inline 422 and network preservation.
9. Trigger delete from Dashboard/edit: exact retention warning, busy lock, successful card removal/navigation; existing generated Task remains visible.
10. At both viewports inspect computed card/button/input dimensions and safe-area clearance; open keyboard to ensure current field and save remain reachable.
11. Check accessibility tree: errors include text, controls have discernible labels, status/dictation are textually distinguishable. Check browser console, dev-server logs and failed requests; expected zero uncaught errors/unhandled promises, with only intentionally mocked/induced API failures.

## Regression Boundary

- Parent today create still creates one ordinary Task and optional dictation items.
- Parent Dashboard ordinary pending/done cards, dictation preview and edit links remain functional.
- Student sees and submits only ordinary Task instances.
- Grading/history and `BottomNav` source are not redesigned.
- Source plan metadata, if added to `TaskOut`, remains optional and does not change existing render branches.

## Plan Integrity Review

- Canonical representation is split-only; `tasks/plan-frontend.md` and `tasks/00-overview.md` are absent.
- Manifest lists every sibling Markdown fragment once with exactly one context, interface, coverage and four tasks fragments.
- Ten stable task markers exist once each only in tasks-kind fragments; IDs are contiguous and every dependency references an existing earlier ID, with no cycle.
- Every task declares exact Files, Reasoning, Depends on, Interfaces, executable Red failure, Template/Script/Style, Green/Build, traceable Visual/UX Checks and Chinese Commit.
- No unresolved visual/interaction question or placeholder remains. Framework, commands, components and tokens are sourced from current client files or confirmed design.
- Proposal capabilities, complete confirmed frontend design, error states, responsive checks and ordinary-task compatibility are mapped above.
