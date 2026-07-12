# Foundation Tasks

- [x] **Task frontend-001: 建立可执行的前端单元测试基线与本地日期工具**

  **Files:** `client/package.json`, `client/vite.config.ts`, `client/tests/setup.ts`, `client/src/utils/local-date.ts`, `client/tests/utils/local-date.spec.ts`

  **Reasoning:** 当前没有 test 脚本，日期代码使用 UTC `toISOString()`，会在非 UTC 时区错误决定业务“今天”。先建立最小 Vitest/Vue Test Utils/jsdom 基线和可复用本地自然日函数，后续所有页面红测才可执行。

  **Depends on:** none

  **Interfaces:** Consumes FUX-01；Produces `localToday()`, `addCalendarDays(date,n)`, `inclusiveDays(start,end)`, `formatRangeSummary(...)`；Contract checks 覆盖月末/闰日、7/30 天包含今天、无 UTC 偏移。

  **Red:** 先新增 spec，断言 `localToday(new Date(2026,6,11,0,30)) === '2026-07-11'`、`addCalendarDays('2026-02-27',2)==='2026-03-01'`、week 结束为 `2026-07-17`。运行 `cd client && npm test -- --run tests/utils/local-date.spec.ts`；预期失败：`npm error Missing script: "test"`（添加脚本后则因 `@/utils/local-date` 不存在失败）。

  **Template / Script / Style:** Template 无；Script 在 `vite.config.ts` 复用 UniApp Vite 插件和 `@` alias，package 增加 `test: vitest`、Vitest、Vue Test Utils、jsdom，纯函数使用本地 Date 构造/解析；Style 无。

  **Green / Build:** `cd client && npm test -- --run tests/utils/local-date.spec.ts && npm run type-check && npm run build:h5`；预期全部退出码 0。

  **Visual / UX Checks:** 无新增 DOM；以设计数据流第 4/6 部分为追踪源，人工核对 week/month 摘要端点分别为 today+6/today+29，避免跨时区日期跳变。

  **Chinese Commit:** `测试：建立前端测试基线和本地日期工具`

- [x] **Task frontend-002: 实现作业计划 API 类型与请求映射**

  **Files:** `client/src/api/homework-plans.ts`, `client/tests/api/homework-plans.spec.ts`

  **Reasoning:** 页面与 Store 需要单一、强类型、无 UI 副作用的服务端契约消费者；先固定路径、方法、payload 和响应，防止页面各自拼请求。

  **Depends on:** frontend-001

  **Interfaces:** Consumes FAPI-01/FAPI-02；Produces 六个 typed API functions；Contract checks 验证 URL 编码、HTTP verb、原样 payload、无 `family_id`、有序词条。

  **Red:** mock `@/api/request`，逐个调用六函数并断言准确参数。运行 `cd client && npm test -- --run tests/api/homework-plans.spec.ts`；预期失败：`Failed to resolve import "@/api/homework-plans"`。

  **Template / Script / Style:** Template 无；Script 导出 FAPI-01 全部 interface/type，调用现有泛型 `request<T>`，不 catch、不 Toast、不导航；Style 无。

  **Green / Build:** `cd client && npm test -- --run tests/api/homework-plans.spec.ts && npm run type-check && npm run build:h5`；预期退出码 0。

  **Visual / UX Checks:** 无 DOM；对照 backend design API 表确认管理接口仅供家长页面调用，materialize 可由两角色调用，DevTools 请求不得出现 family ID。

  **Chinese Commit:** `功能：新增作业计划 API 契约`

- [x] **Task frontend-003: 实现独立计划 Store、同步去重与登出清理**

  **Files:** `client/src/stores/homework-plans.ts`, `client/src/stores/auth.ts`, `client/tests/stores/homework-plans.spec.ts`

  **Reasoning:** 模板不能污染普通作业缓存；页面需要一致的 loading、局部更新、非阻塞同步警告和跨账号清理。

  **Depends on:** frontend-002

  **Interfaces:** Consumes FAPI-02/FSTORE-01；Produces `useHomeworkPlansStore` actions/state 和 auth logout reset；Contract checks 包括所有 finally、同一 in-flight Promise、部分失败 warning、更新替换、删除移除、logout 清空。

  **Red:** mock API 与 `uni.reLaunch`，断言 rejected list/detail/save/delete 后 flag=false；并发两次 materialize 只调用 API 一次；failed row 设置指定 warning 且 resolve；logout 清空计划。运行 `cd client && npm test -- --run tests/stores/homework-plans.spec.ts`；预期失败：`Failed to resolve import "@/stores/homework-plans"`。

  **Template / Script / Style:** Template 无；Script 用 Pinia setup store/ref，实现模块级或 store 内 `syncPromise` 并在 finally 清除，`reset()` 不导航；auth Store 静态 import 并在 token 清除前 reset；Style 无。

  **Green / Build:** `cd client && npm test -- --run tests/stores/homework-plans.spec.ts && npm run type-check && npm run build:h5`；预期退出码 0。

  **Visual / UX Checks:** 以设计数据流第 2/8 部分为源：同步错误只进入 `syncWarning`，不得触发 Store 内 Toast；切换家庭账号后不得短暂显示旧计划。

  **Chinese Commit:** `功能：新增作业计划状态管理`
