# Editing Tasks

- [x] **Task frontend-009: 注册家长计划编辑路由与权限入口**

  **Files:** `client/src/pages.json`, `client/src/pages/parent/homework-plan-edit.vue`, `client/tests/pages/homework-plan-edit.spec.ts`

  **Reasoning:** 先交付可编译、受角色和 ID 保护的二级页面骨架，稳定路由/加载/卸载边界，再在下一任务填完整表单，避免 Dashboard 指向无效页面。

  **Depends on:** frontend-003, frontend-004, frontend-007, backend-008

  **Interfaces:** Consumes FROUTE-01/FROUTE-03/FSTYLE-02；Produces registered edit page with guarded detail load and cleanup；Contract checks 验证无 ID、非家长、404/403 导航，loading 前不渲染 form，unload clear。

  **Red:** mount with route query ID，断言先显示“加载中”且无表单；resolve detail 后出现标题；missing ID/non-parent 不 fetch；unmount 调 clear。运行 `cd client && npm test -- --run tests/pages/homework-plan-edit.spec.ts`；预期失败：`Failed to resolve import "@/pages/parent/homework-plan-edit.vue"`。

  **Template / Script / Style:** Template 固定 AppBar（返回、居中“编辑作业计划”）、loading/error shell、详情成功后的 form slot/container，明确不导入 BottomNav；Script `onLoad/onUnload`、role/id guard、fetch/404/403 路由；Style 复用现有白色 AppBar、organic page、safe-area bottom，不先实现保存字段。

  **Green / Build:** `cd client && npm test -- --run tests/pages/homework-plan-edit.spec.ts && npm run type-check && npm run build:h5`。

  **Visual / UX Checks:** 来源 design Visual Checks 10/12/16：加载阶段不闪空字段；AppBar 返回可达且标题居中；页面不存在 BottomNav；375×812 与 768×1024 安全区无横溢。

  **Chinese Commit:** `功能：注册作业计划编辑页面`

- [x] **Task frontend-010: 完成计划编辑、脏状态、冲突处理与删除流程**

  **Files:** `client/src/pages/parent/homework-plan-edit.vue`, `client/tests/pages/homework-plan-edit.spec.ts`

  **Reasoning:** 编辑必须是含乐观锁的完整替换，并清晰区分未保存返回、409 冲突、字段错误和删除保留实例；这是计划生命周期闭环。

  **Depends on:** frontend-009

  **Interfaces:** Consumes FAPI-01, FSTORE-01, FCOMP-01, FROUTE-03, FUX-01/FUX-02, FSTYLE-02；Produces full form/save/reload/delete behavior；Contract checks 覆盖回填、started lock、normalized dirty、dictation restore/empty submit、full payload、409/422/network、两个 ConfirmModal 和 operation locks。

  **Red:** 扩充 spec：详情回填实际日期；`start_date <= localToday` 时 picker disabled；空白/trim 不产生假 dirty；修改后 back 出现精确放弃文案；关闭听写提交 `[]`、未保存重开恢复词条；PATCH 含 `updated_at`；409 保留值并显示 reload；delete 精确确认/成功导航。运行 `cd client && npm test -- --run tests/pages/homework-plan-edit.spec.ts`；预期失败于保存按钮/日期字段/ConfirmModal 或 update action 不存在。

  **Template / Script / Style:** Template 用创建页相同科目 pills、标题/日期/说明/时长 cards、`DictationConfig`、开始锁定提示、409 panel+刷新、inline errors、进行态保存按钮、分离的低强调删除和两个 ConfirmModal；Script 建 form/initial normalized snapshot/computed isDirty/validation，返回拦截，full update，422 field map，409 reload，delete；Style 复用现有 cards/inputs/gradient，warning 复用 ConfirmModal 语义色，delete 不与保存等权，safe-area spacer。

  **Green / Build:** `cd client && npm test -- --run tests/pages/homework-plan-edit.spec.ts && npm run type-check && npm run build:h5`。

  **Visual / UX Checks:** 来源 proposal 6、design Visual Checks 10–11/14–17：回填前无闪烁；started 开始日期明确禁用；两个弹窗文案逐字一致；保存/删除中文进行态；409 有刷新且不覆盖；375×812 软键盘下当前输入和保存可达；无 BottomNav，删除与保存分离。

  **Chinese Commit:** `功能：完成作业计划编辑与删除流程`
