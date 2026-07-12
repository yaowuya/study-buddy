# Dashboard and Materialization Tasks

- [x] **Task frontend-006: 实现纯展示作业计划卡**

  **Files:** `client/src/components/HomeworkPlanCard.vue`, `client/tests/components/HomeworkPlanCard.spec.ts`

  **Reasoning:** 计划卡信息密度和语义不同于 Task 卡；独立纯组件能固定“计划而非可提交作业”的边界，并让 Dashboard 只负责状态和操作。

  **Depends on:** frontend-002

  **Interfaces:** Consumes FCOMP-02/FSTYLE-01；Produces semantic plan card；Contract checks 覆盖两种状态、听写有无、四类科目/默认、描述/时长可选、progress clamp、长标题、busy 和 emits。

  **Red:** mount active/upcoming fixtures，断言状态、`3/7`、today 状态、metadata；断言不存在“提交/完成/批改”；busy 点击不 emit。运行 `cd client && npm test -- --run tests/components/HomeworkPlanCard.spec.ts`；预期失败：`Failed to resolve import "@/components/HomeworkPlanCard.vue"`。

  **Template / Script / Style:** Template 按 Header→TintedContent→Actions，badge 为 flex child，描述 `v-if`；Script 仅 computed label/progress/subject icon 和 emit；Style 精确复用 FSTYLE-01，metadata wrap、desc 两行 clamp、操作 min-height 44px，小屏可隐藏重复听写 badge 但 metadata 保留。

  **Green / Build:** `cd client && npm test -- --run tests/components/HomeworkPlanCard.spec.ts && npm run type-check && npm run build:h5`。

  **Visual / UX Checks:** 来源 design Visual Checks 7–9/14/15：375×812 用超长标题、双 badge、多 metadata 验证无横溢；inspect 24px card、30px icon、16px content radius、20px content padding、科目配色与现有 Task 卡一致；空 desc 无间隙。

  **Chinese Commit:** `功能：新增作业计划概览卡片`

- [x] **Task frontend-007: 扩展家长 Dashboard 同步编排和活动计划管理区**

  **Files:** `client/src/pages/parent/dashboard.vue`, `client/tests/pages/dashboard.spec.ts`

  **Reasoning:** 家长页面必须先补生成再展示新 Task，并在既有全部作业之后独立处理计划 loading/empty/error/cache/data 和编辑/删除；局部失败不能破坏今日作业。

  **Depends on:** frontend-003, frontend-006, backend-009

  **Interfaces:** Consumes FSTORE-01/FSTORE-02, FROUTE-01, FUX-03, FSTYLE-02；Produces ordered parent onShow, plan section, edit navigation and Dashboard-owned delete confirmation；Contract checks 验证 materialize→并发 fetch→sync start、失败继续、区域状态、ConfirmModal 文案、删除成功/失败。

  **Red:** mock stores，触发 onShow 并记录 call order；让 materialize reject/resolve warning，均断言 fetchTodayTasks；断言 plan section 在 completed section 后、四种状态、edit URL、删除确认后调用 store。运行 `cd client && npm test -- --run tests/pages/dashboard.spec.ts`；预期失败于页面未调用 `useHomeworkPlansStore` 且不存在“进行中的作业计划”。

  **Template / Script / Style:** Template 在具体作业 section 后追加 divider、标题、局部 loading/empty+去布置/error+重试/cards、缓存 warning、delete ConfirmModal；Script 把 onShow 改为 async orchestrator，消费一次 warning，edit navigateTo，delete 锁定目标 ID；Style 只新增 section state/plan list/spacer，禁止修改 Hero、Task card、dictation modal、BottomNav 规则。

  **Green / Build:** `cd client && npm test -- --run tests/pages/dashboard.spec.ts && npm run type-check && npm run build:h5`。

  **Visual / UX Checks:** 来源 design Visual Checks 4–9/12–13/17：对比改前 Hero DOM、圆角、mint、32px padding、Task badge；滚到底部验证计划区和卡片后 nav 不遮挡；empty/error 不改变今日内容；删除弹窗文案精确；console/server/failed requests 无未处理错误。

  **Chinese Commit:** `功能：在家长作业页管理活动计划`

- [x] **Task frontend-008: 为学生作业页加入非阻塞补生成编排**

  **Files:** `client/src/pages/student/home.vue`, `client/tests/pages/student-home.spec.ts`

  **Reasoning:** 学生打开作业页也必须补齐遗漏实例，但不得获得计划模板列表或管理入口；失败时仍显示缓存和普通 Task。

  **Depends on:** frontend-003, backend-009

  **Interfaces:** Consumes FSTORE-01/FSTORE-02；Produces student materialize-before-fetch flow；Contract checks 验证只调用 materialize/fetch tasks、不调用任何管理 action、失败继续且无计划 DOM。

  **Red:** mock stores，断言 onShow 顺序 `materialize` 后 `fetchTodayTasks`；materialize rejection/warning 时仍 fetch；搜索渲染文本不存在“作业计划/编辑计划”。运行 `cd client && npm test -- --run tests/pages/student-home.spec.ts`；预期失败：首个调用是 `fetchTodayTasks` 或 materialize 从未调用。

  **Template / Script / Style:** Template 不变；Script 仅加入 plans Store 和 async onShow 编排/一次非阻塞 warning，保留现有普通作业、同步和生命周期；Style 不变。

  **Green / Build:** `cd client && npm test -- --run tests/pages/student-home.spec.ts && npm run type-check && npm run build:h5`。

  **Visual / UX Checks:** 来源 proposal Out of Scope“学生不管理模板”和 design Visual Check 6：学生页面仅出现普通 Task；同步失败时缓存卡可操作；无计划卡、编辑/删除入口或布局漂移。

  **Chinese Commit:** `功能：学生端加载时补齐计划作业`
