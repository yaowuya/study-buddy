# Frontend Interface Ledger

任务通过 `FAPI-*`、`FSTORE-*`、`FCOMP-*`、`FROUTE-*`、`FUX-*`、`FSTYLE-*` 引用本文件；契约正文只在此处维护。

## API Contracts

### FAPI-01 — Types

```ts
type PlanRangeType = 'week' | 'month' | 'custom'
type PlanStatus = 'upcoming' | 'active'
type MaterializePlanStatus = 'success' | 'failed'
interface DictationItemInput { content: string }
interface HomeworkPlanCreateParams {
  type: 'school' | 'home'; title: string; desc?: string | null
  duration?: number | null; subject?: string | null; range_type: PlanRangeType
  start_date?: string; end_date?: string; dictation_items: DictationItemInput[]
}
interface HomeworkPlanUpdateParams {
  type: 'school' | 'home'; title: string; desc: string | null
  duration: number | null; subject: string | null; start_date: string
  end_date: string; dictation_items: DictationItemInput[]; updated_at: string
}
interface HomeworkPlanSummary {
  id: string; type: 'school' | 'home'; title: string; desc: string | null
  duration: number | null; subject: string | null; start_date: string; end_date: string
  status: PlanStatus; has_dictation: boolean; dictation_count: number
  total_days: number; generated_count: number; remaining_days: number | null
  days_until_start: number | null; today_generated: boolean; updated_at: string
}
interface HomeworkPlanDetail extends HomeworkPlanSummary {
  dictation_items: Array<{ id?: string; content: string }>
}
interface MaterializePlanResult {
  plan_id: string; created_dates: string[]; status: MaterializePlanStatus; error: string | null
}
interface MaterializeResult { created_count: number; plans: MaterializePlanResult[] }
```

### FAPI-02 — Requests

| Function | Request |
| --- | --- |
| `createHomeworkPlan(data)` | `POST /homework-plans` with `HomeworkPlanCreateParams` |
| `listActiveHomeworkPlans()` | `GET /homework-plans` |
| `getHomeworkPlan(id)` | `GET /homework-plans/${encodeURIComponent(id)}` |
| `updateHomeworkPlan(id,data)` | `PATCH /homework-plans/${encodeURIComponent(id)}` |
| `deleteHomeworkPlan(id)` | `DELETE /homework-plans/${encodeURIComponent(id)}` |
| `materializeHomeworkPlans()` | `POST /homework-plans/materialize` |

Contract checks: no function accepts family ID; payload preserves ordered dictation items; API module has no Toast/navigation; 409/422/404 remain distinguishable through current request error.

## Store Contracts

### FSTORE-01 — Homework plans store

State: `activePlans`, `currentPlan`, `listLoading`, `detailLoading`, `saving`, `deleting`, `syncing`, `syncWarning`.

Actions: `fetchActivePlans`, `fetchPlan`, `createPlan`, `updatePlan`, `deletePlan`, `materialize`, `clearCurrentPlan`, `reset`.

- CRUD delegates to FAPI-02; update replaces matching card/current detail, delete removes matching card.
- Every loading flag resets in `finally`.
- `materialize` converts request rejection to `syncWarning` and resolves; any result row with `failed` sets “部分计划作业生成失败，请稍后重试”; reentry shares one in-flight Promise.
- `reset` clears family-scoped data and warnings; `auth.logout()` calls it before navigation.
- Students may call only `materialize`; no student page calls list/detail/create/update/delete.

### FSTORE-02 — Page ordering

Parent Dashboard `onShow`: await materialize; then concurrently fetch today tasks and active plans; finally start existing 30-second task sync. Student Home: await materialize, then fetch today tasks. Errors from materialize never prevent the latter. Existing timer does not materialize.

## Component Contracts

### FCOMP-01 — DictationConfig

Props: `enabled:boolean`, `words:string[]`, `disabled?:boolean`, `error?:string`.
Events: `update:enabled`, `update:words`, `clear-error`.
Header always renders; body renders only when enabled. Add trims, rejects empty and exact normalized duplicate, preserves order; disabled blocks all mutations. Component has no API. Error has text adjacent to body and clears after a relevant edit.

### FCOMP-02 — HomeworkPlanCard

Props: `plan:HomeworkPlanSummary`, `busy?:boolean`; emits `edit(planId)`, `delete(planId)` only. Status maps `active→进行中`, `upcoming→即将开始`; dictation is a separate feature badge. Shows range, remaining/start context, `generated_count/total_days`, progress, today status, subject/dictation count/duration, optional two-line desc. Never exposes Task completion/submission/grading actions. Busy disables both actions.

## Route and Page Contracts

### FROUTE-01 — Edit route

Register `pages/parent/homework-plan-edit` in `pages.json`, navigate with `?id=<encoded UUID>`, no tab bar/BottomNav. Missing ID, non-parent, 403 or 404 returns to role-appropriate page; 404 also refreshes plans.

### FROUTE-02 — Creation flow

`today` default. `week/month/custom` are the only plan API range types. Success routes to `/pages/parent/dashboard`; copy is “今日作业已发布” or “作业计划已创建”. Submission lock displays “发布中…”.

### FROUTE-03 — Edit flow

Load detail before rendering form, store normalized initial snapshot, and clear current detail on unload. Started means `start_date <= localToday`; lock its start date. Save sends full FAPI-01 update with original `updated_at`. Success Toast “计划修改已保存” and returns. 409 shows conflict plus reload; 422 stays inline; network failure preserves form.

## Interaction Contracts

### FUX-01 — Dates and validation

Use a pure local-date utility (local year/month/day, calendar addition, inclusive day count). Summaries show today-only, inclusive 7-day, inclusive 30-day, or actual custom range. Leaving custom clears custom date errors. Complete validation occurs on submit/save; field edits clear corresponding errors; first invalid field is scrolled/focused when UniApp supports it.

### FUX-02 — Dirty return and delete

Dirty comparison normalizes trim, null empty desc/duration, ordered trimmed words, disabled dictation to empty submitted words, and `YYYY-MM-DD`. Dirty back uses ConfirmModal warning: title “放弃修改”, desc “尚未保存的修改将会丢失。”, cancel “继续编辑”, confirm “放弃修改”. Delete uses title “删除这个计划？”, desc “删除后将停止生成后续作业，已经生成的作业仍会保留。”, cancel “取消”, confirm “确认删除”.

### FUX-03 — Dashboard states

Plan section is locally loading/empty/error/data. Empty text “暂无进行中的作业计划” and “去布置”; no-cache error has retry; cached refresh failure retains cards and warning. Delete confirmation is owned by Dashboard; success removes card and Toasts “计划已删除，已有作业不受影响”. Materialize warning appears at most once per page-show lifecycle.

## Style and Responsive Contracts

### FSTYLE-01 — Existing visual continuity

Use `variables.scss`; no new global token. Plan card: existing lowest surface, 24px radius/padding, 16px vertical gap, Dashboard shadow. Subject icon 30px and existing subject classes/mapping. Content radius/padding 16px/20px. Header flex gap 8px; title 16/22px 700 with ellipsis; badges 4px 10px, 12px and flex children. Actions ≥44px high; edit uses subject action color, delete is low-emphasis danger.

### FSTYLE-02 — Page placement

Creation uses existing rounded field cards, mint dictation card, gradient publish button and existing BottomNav; custom dates adapt row→column if 375px text overflows. Dashboard appends divider and plan section after completed/pending Task content, with bottom spacer preserving floating nav clearance. Edit page uses existing AppBar/form cards/save button, separated low-emphasis delete, and safe-area spacer.

### FSTYLE-03 — Visual verification sources

Trace checks to `design/frontend/02-components-and-visual-contract.md` Visual Checks, `prototype.html`, and current `task-create.vue`, `dashboard.vue`, `BottomNav.vue`, `ConfirmModal.vue`, `variables.scss`. Verify at 375×812 and 768×1024; inspect computed styles, accessibility tree, console, server logs and failed network requests rather than screenshot alone.
