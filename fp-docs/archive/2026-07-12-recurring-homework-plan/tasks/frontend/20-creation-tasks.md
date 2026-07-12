# Creation Tasks

- [x] **Task frontend-004: 抽取条件渲染的听写配置组件**

  **Files:** `client/src/components/DictationConfig.vue`, `client/tests/components/DictationConfig.spec.ts`

  **Reasoning:** 创建和编辑必须共享关闭态不渲染、词条规范化与禁用语义；独立无 API 组件可先用红测固定行为，避免两页漂移。

  **Depends on:** frontend-001

  **Interfaces:** Consumes FCOMP-01/FSTYLE-02；Produces reusable controlled component；Contract checks 覆盖 closed/open/disabled、trim/empty/duplicate/delete、error/clear-error 和精确 event payload。

  **Red:** shallow mount `enabled=false`，断言找不到输入、说明、tags；开启后添加 `'  apple  '` 发出 `['apple']`，重复不发出；disabled 点击不发出。运行 `cd client && npm test -- --run tests/components/DictationConfig.spec.ts`；预期失败：`Failed to resolve import "@/components/DictationConfig.vue"`。

  **Template / Script / Style:** Template 仅 Header（图标、标题、可访问开关）+ `v-if="enabled"` Body（input、添加、tags、说明、inline error）；Script 用 props/emits，不直接改 props、不请求 API；Style 从当前 `task-create.vue` 搬移 mint 卡、toggle、tag、44px 输入/操作样式，不新增 token，disabled 同时体现属性和视觉。

  **Green / Build:** `cd client && npm test -- --run tests/components/DictationConfig.spec.ts && npm run type-check && npm run build:h5`。

  **Visual / UX Checks:** 来源 design Visual Checks 1–3/15：375×812 检查关闭后 Body 不占空间，开启后 tags 换行、删除点击区可操作、错误有文字且不只靠颜色；inspect 确认现有 mint/rounded 样式。

  **Chinese Commit:** `重构：抽取条件听写配置组件`

- [x] **Task frontend-005: 扩展布置页时间范围、校验和提交分流**

  **Files:** `client/src/pages/parent/task-create.vue`, `client/tests/pages/task-create.spec.ts`

  **Reasoning:** 布置页是创建入口，需保持 today 默认和原两步 API，同时把多日请求原子提交给计划 API；条件听写必须替换当前“仅降低透明度”的关闭态。

  **Depends on:** frontend-002, frontend-004, backend-007

  **Interfaces:** Consumes FAPI-01/FAPI-02, FCOMP-01, FROUTE-02, FUX-01, FSTYLE-02；Produces four-range creation UI and branching submit；Contract checks 验证请求互斥、日期/词条/时长字段错误、防重复、成功文案与导航。

  **Red:** mount page，断言默认“今日作业”且无日期 picker/听写 body；选择 week 显示包含今天 7 日摘要并只调用 `createHomeworkPlan`；today 只调用 `createTask`/可选 dictation；custom 非法日期显示 inline error；双击只发一请求。运行 `cd client && npm test -- --run tests/pages/task-create.spec.ts`；预期至少失败于找不到“作业时间计划”且 week 控件不存在。

  **Template / Script / Style:** Template 在科目卡前加入 rounded picker 卡、custom 两个 date picker、摘要、inline errors；用 `DictationConfig` 替换原听写 DOM，按钮文本随 submitting 为“发布中…”；Script 增 `rangeType/startDate/endDate/errors/submitting`，使用本地日期工具，today 保留现有 payload，多日构造 FAPI-01；Style 复用 `.card/.field-input/.submit-btn`，日期 row 在窄屏纵向，删除已搬迁听写重复样式，按确认原型移除 AppBar 左菜单但保留占位居中。

  **Green / Build:** `cd client && npm test -- --run tests/pages/task-create.spec.ts && npm run type-check && npm run build:h5`。

  **Visual / UX Checks:** 来源 proposal 4、design Visual Checks 1–3/6/14/16：预览 today/week/month/custom，确认 custom 才渲染日期；听写关闭无 Body；375×812 无溢出且软键盘下按钮/输入可达；布置页无活动计划；BottomNav 视觉不变。

  **Chinese Commit:** `功能：支持布置周期作业计划`
