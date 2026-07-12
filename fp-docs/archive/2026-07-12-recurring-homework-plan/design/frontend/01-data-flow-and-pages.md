# Frontend：数据流与页面

## 第一部分：架构决策

### 决策 1：视觉来源

- **选择**：已确认 `prototype.html` 决定新增交互和信息架构；现有 `task-create.vue`、`dashboard.vue` 与 `BottomNav.vue` 决定真实视觉 token 和组件样式。
- **理由**：原型已完成产品审阅，现有代码是当前产品视觉事实，二者结合可避免重新设计和样式漂移。

### 决策 2：计划状态独立管理

- **选择**：新增独立 homework plans Store，现有 tasks Store 继续只管理具体作业。
- **理由**：计划模板和可执行作业具有不同权限、生命周期和刷新策略。

### 决策 3：显式同步后查询

- **选择**：页面 `onShow` 先调用专用 materialize POST，再请求现有作业列表；家长额外请求活动计划。
- **理由**：匹配后端纯 GET 契约，且同步失败不会阻塞已有作业查询。

## 第二部分：客户端模块

### 新增 API

```text
client/src/api/homework-plans.ts
```

建议类型：

```ts
type PlanRangeType = 'week' | 'month' | 'custom'
type PlanStatus = 'upcoming' | 'active'
type MaterializeStatus = 'success' | 'failed'

interface HomeworkPlanCreateParams { ... }
interface HomeworkPlanUpdateParams { ... }
interface HomeworkPlanSummary { ... }
interface HomeworkPlanDetail { ... }
interface MaterializeResult { ... }
```

方法：

- `createHomeworkPlan(payload)`
- `listActiveHomeworkPlans()`
- `getHomeworkPlan(id)`
- `updateHomeworkPlan(id, payload)`
- `deleteHomeworkPlan(id)`
- `materializeHomeworkPlans()`

复用现有 `request` 封装、JWT 注入和统一错误模型，不在模块中直接操作 UI。

### 新增 Store

```text
client/src/stores/homework-plans.ts
```

状态：

```ts
activePlans: HomeworkPlanSummary[]
currentPlan: HomeworkPlanDetail | null
listLoading: boolean
detailLoading: boolean
saving: boolean
deleting: boolean
syncing: boolean
syncWarning: string | null
```

动作：

```ts
fetchActivePlans()
fetchPlan(id)
createPlan(payload)
updatePlan(id, payload)
deletePlan(id)
materialize()
clearCurrentPlan()
```

规则：

- 所有 loading flag 在 `finally` 恢复；
- `materialize()` 对部分失败设置 `syncWarning`，但解析为已完成请求；
- 更新成功后替换 `currentPlan`，并按 ID 更新或重新加载 `activePlans`；
- 删除成功后立即从 `activePlans` 移除；
- 退出账号时清理计划状态，避免跨账号家庭数据残留；
- 学生端不调用活动计划列表、详情或管理动作。

## 第三部分：作业页面加载编排

### 家长 Dashboard

现有 `onShow` 调整为有序异步流程：

```text
onShow
  → await plansStore.materialize()
       ├─ 全部成功：继续
       ├─ 部分失败：记录 warning，继续
       └─ 请求失败：转换为非阻塞 warning，继续
  → 并发：tasksStore.fetchTodayTasks() + plansStore.fetchActivePlans()
  → syncStore.start()
```

要求：

- materialize 完成后再获取具体作业，确保列表包含新实例；
- 具体作业和活动计划可以并发查询；
- 计划列表失败只影响底部区域；
- 同步失败只提示，不清空缓存作业；
- 防止 `onShow` 重入时重复提交：`syncing` 为 true 时复用或跳过本轮；
- 现有 30 秒 sync 继续只请求具体作业，不主动 materialize；
- 页面卸载继续停止现有同步机制。

### 学生 Home

进入学生作业页面时：

```text
onShow
  → await plansStore.materialize() 或独立轻量 sync action
  → tasksStore.fetchTodayTasks()
```

学生只需要同步能力，不需要计划状态。为避免学生 bundle/权限语义混淆，可把 `materializeHomeworkPlans` 直接由 student home 调用，或允许 Store 暴露唯一无管理数据的 `materialize()`；实现计划选择与现有模式最一致的方式。

同步失败仍继续获取已有作业。

## 第四部分：布置页面

路径：`/pages/parent/task-create`。

### 表单状态

新增：

```ts
rangeType: 'today' | 'week' | 'month' | 'custom'
startDate: string
endDate: string
```

默认：

- `rangeType = 'today'`
- 日期字段可初始化但仅 custom 时参与请求与校验；
- 听写 `enabled = false`，词条为空。

### 时间范围交互

- 使用移动端兼容的选择控件表现下拉选择；
- `today`：摘要为仅发布今天一份作业；
- `week`：即时展示含今天的 7 日摘要；
- `month`：即时展示含今天的 30 日摘要；
- `custom`：显示开始/结束日期控件和摘要；
- 离开 custom 时隐藏日期控件并清除日期错误；
- 客户端日期摘要仅用于预览，服务端为最终权威。

### 提交分流

```text
if rangeType == today:
  createTask(existing payload)
  if dictation enabled:
    createDictationItems(task.id, words)
else:
  createHomeworkPlan(plan payload including words)
```

- 今日作业保持现有两步 API，避免扩大已有 Task API；
- 多日计划把听写词条作为计划创建请求的一部分，保证模板原子保存；
- 创建中禁用重复提交并显示“发布中…”；
- 今日成功提示“今日作业已发布”；
- 计划成功提示“作业计划已创建”；
- 成功后进入家长 Dashboard；
- 若计划创建成功但今天实例化警告，仍返回 Dashboard，由页面 materialize 重试。

### 校验

- 标题非空；
- 时长为空或正整数；
- custom 起止日期完整；
- 开始日期不早于客户端今天（服务端再次校验）；
- 结束日期不早于开始日期；
- 听写开启时至少一个词条；
- 错误显示在所属卡片字段下方。

## 第五部分：家长作业页面

路径保持 `/pages/parent/dashboard`。

页面顺序：

1. 现有 AppBar；
2. 今日概览；
3. 家庭码；
4. 待完成作业；
5. 已完成作业；
6. 分隔区；
7. 进行中的作业计划；
8. 足够 bottom spacer；
9. 现有 `BottomNav`。

活动计划状态：

- `listLoading` 且无缓存：显示与页面一致的轻量加载态；
- 加载成功有数据：按服务端顺序渲染计划卡；
- 加载成功为空：显示简洁空态和“去布置”操作；
- 加载失败且无缓存：显示局部错误和重试；
- 有缓存但刷新失败：保留卡片并显示非阻塞提示。

## 第六部分：计划编辑页面

建议路径：

```text
/pages/parent/homework-plan-edit?id=<uuid>
```

注册到 `client/src/pages.json`，不加入底部主导航。

### 加载

```text
onLoad(query)
  → 校验 id
  → fetchPlan(id)
  → 请求成功后构建 form 和 initialSnapshot
```

- 加载完成前显示 loading，不闪现默认空表单；
- 404 返回作业页面并提示计划不存在或已不可访问；
- 403 属于异常权限状态，提示后返回；
- 页面销毁时 `clearCurrentPlan()`。

### 表单

包含：

- 实际起止日期；
- 科目；
- 标题；
- 听写开关和词条；
- 作业要求；
- 预计时长；
- 加载时 `updated_at`。

已开始计划禁用开始日期；未开始计划允许修改。编辑页显示实际范围，不把存储日期反推成预设后再重新计算。

### 规范化快照与脏状态

建立序列化前规范化函数：

- trim 文本；
- 空描述/时长统一为 null；
- 词条 trim 且保持顺序；
- 听写关闭时用于提交的词条为空，但本地临时词条在离开前保留；
- 日期使用 `YYYY-MM-DD`。

`isDirty` 比较当前规范化表单和 initialSnapshot，而不是依赖单个 touched flag。

### 返回

- 无修改直接返回；
- 有修改打开 `ConfirmModal`：标题“放弃修改？”，说明“尚未保存的修改将会丢失”；
- “继续编辑”关闭弹窗；
- “放弃修改”返回 Dashboard；
- 保存中禁止返回，避免不确定提交状态。

### 保存

- 完整校验后提交完整更新 payload；
- 使用 `updated_at` 乐观并发 token；
- 保存中禁用重复提交；
- 成功后更新 Store、Toast“计划修改已保存”并返回；
- 409 显示“计划已被其他家长修改，请刷新后重试”，提供重新加载；
- 422 映射字段错误；
- 网络错误保留用户表单。

### 删除

编辑页底部提供低强调危险操作。确认内容：

- 标题：“删除这个计划？”；
- 说明：“删除后将停止生成后续作业，已经生成的作业仍会保留。”；
- 取消/确认删除。

成功后移除 Store 条目、提示“计划已删除，已有作业不受影响”并返回 Dashboard。

## 第七部分：路由与权限

- 家长专用页面入口只从家长 Dashboard 展示；
- 后端权限是最终防线，客户端隐藏入口不替代鉴权；
- 编辑页加载时若当前角色不是家长，直接返回其角色首页；
- 所有计划 API 不传 family ID；
- 登出时清空 Store；
- 现有 auth Store 与导航方式保持不变。

## 第八部分：错误和通知

| 场景 | UI 行为 |
| --- | --- |
| 同步部分失败 | 作业照常展示；一次非阻塞提示“部分计划作业生成失败，请稍后重试” |
| 同步整体失败 | 作业照常查询；提示同步失败 |
| 活动计划列表失败 | 计划区域局部重试，不影响今日作业 |
| 创建/保存 422 | 字段下方错误并定位第一个错误 |
| 保存 409 | 冲突提示与刷新入口 |
| 删除失败 | 保留页面/卡片并 Toast 错误 |
| 计划 404 | 返回 Dashboard 并刷新计划 |

避免 `onShow`、同步和列表请求同时产生重复 Toast；Store 暴露 warning，由页面在一次生命周期中消费。

## 第九部分：测试策略

### API/Store

- 计划 CRUD 参数和响应映射；
- loading 状态 finally 恢复；
- materialize 部分失败转 warning；
- 删除后列表移除；
- 更新后对应卡替换；
- logout 清空状态。

### 创建页面

- 默认 today；
- 预设范围摘要；
- custom 显隐和日期错误；
- 听写条件渲染、去重和必填；
- 今日与计划请求分流；
- 防重复提交。

### Dashboard/Student Home

- materialize 在 fetch tasks 前；
- materialize 失败仍 fetch tasks；
- 家长额外 fetch plans；
- 学生不 fetch plan management data；
- 计划区 loading/empty/error/data；
- syncStore 定时刷新不触发 materialize。

### 编辑页面

- 详情回填；
- 已开始日期禁用；
- 规范化脏状态；
- 返回确认；
- 409 处理；
- 听写关闭提交空词条；
- 删除确认和返回。

## 第十部分：应用验收

- 多日发布创建计划，不创建模板型 Task；
- 打开作业页先同步再看到新生成实例；
- 同步失败时旧作业仍可用；
- 布置页没有活动计划；
- 家长 Dashboard 底部有活动计划；
- 学生端只看到具体作业；
- 编辑保存只改变计划卡和未来实例；
- 删除计划后卡片消失、已有作业保留；
- 现有一次性作业、听写、提交和批改流程不回归。
