# Frontend：组件与视觉交互契约

## UI Settings Source

- Settings read: `fp-docs/settings/frontend.md` / `fp-docs/settings/prototype-style.md` / `fp-docs/settings/agent.md` 均不存在。
- Existing references: `client/src/pages/parent/task-create.vue`、`client/src/pages/parent/dashboard.vue`、`client/src/components/BottomNav.vue`、`client/src/components/ConfirmModal.vue`、`client/src/static/styles/variables.scss`。
- Confirmed tokens/components: 使用现有 organic 色彩、科目配色、卡片、AppBar、表单、Toast、ConfirmModal 和 BottomNav。
- Unknowns requiring user confirmation: 无；新增交互已通过确认原型确定，最终实现仍需本地预览验收。

## UX Settings Source

- Settings read: 项目 FeaturePilot UX settings 不存在。
- Existing interaction references: 已确认 `prototype.html`，现有创建/编辑表单、`ConfirmModal`、`uni.showToast` 和页面导航代码。
- Confirmed UX rules: 提交时完整校验、字段旁错误、保存/删除防重、危险操作确认、未保存返回确认、同步失败非阻塞。
- Open interaction questions: 无。

## 第一部分：组件策略

### DictationConfig

建议新增：

```text
client/src/components/DictationConfig.vue
```

用途：创建页与计划编辑页复用听写配置逻辑。

Props：

```ts
enabled: boolean
words: string[]
disabled?: boolean
error?: string
```

Events：

```ts
update:enabled
update:words
clear-error
```

行为：

- Header 始终显示图标、标题和开关；
- `enabled = false` 时输入、词条和说明不进入渲染树；
- 开启后显示词条输入、添加按钮、Tags 和说明；
- 添加时 trim；
- 空内容不添加；
- 已存在规范化相同词条不重复添加；
- 删除操作至少具有现有 tag close 的点击区域；
- disabled 时开关、输入、添加和删除均不可操作；
- 组件只管理值与展示，不调用后端。

为控制本次范围，现有单次作业编辑页是否迁移至该组件不是上线阻塞，但创建页不得再保留一套行为不一致的关闭态。

### HomeworkPlanCard

建议新增：

```text
client/src/components/HomeworkPlanCard.vue
```

Props：

```ts
plan: HomeworkPlanSummary
busy?: boolean
```

Events：

```ts
edit(planId)
delete(planId)
```

卡片不在内部调用 API。Dashboard 负责导航和确认弹窗，Store 负责请求。

结构：

```text
Card
├── Header
│   ├── SubjectIconCircle
│   ├── Title
│   ├── StatusBadge
│   └── DictationBadge? 
├── SubjectTintedContent
│   ├── Frequency
│   ├── RangeContext
│   ├── ProgressBar
│   ├── GeneratedSummary
│   ├── MetadataChips
│   └── DescriptionPreview?
└── Actions
    ├── EditPlan
    └── Delete (low emphasis)
```

卡片语义：

- `status = active` → “进行中”；
- `status = upcoming` → “即将开始”；
- 听写是功能标签，不替代状态；
- 不显示未开始/已完成等 Task 执行状态；
- 不显示提交、批改或完成按钮；
- 不显示“自动补齐”等实现说明。

### 页面局部组件

时间计划选择可先保留在 `task-create.vue` 与编辑页的表单组合中；若重复明显，执行阶段可抽取 `HomeworkPlanScheduleFields.vue`，但必须保持创建与编辑差异：编辑已开始计划时开始日期禁用，且展示实际存储范围。

## 第二部分：视觉 token 与现有模式

不得在本功能中建立新的设计 token。使用 `variables.scss` 和相邻页面已有值。

### 页面与卡片

- 页面背景沿用 `$color-organic-bg`；
- 普通任务/计划卡背景沿用 `$color-organic-surface-container-lowest`；
- Card 圆角 24px；
- Card padding 24px（现有 Dashboard task card）；
- Card 阴影 `0 12px 32px rgba(0,0,0,0.06)`；
- 卡片纵向 gap 16px；
- 页面水平边距沿用 `$spacing-margin`（当前为 24px）。

### 科目配色

| 科目 | 图标/操作背景 | 内容背景 | 文字 |
| --- | --- | --- | --- |
| 语文 | `$color-soft-lilac` | 同色 30% | `#4e453c` / dark green |
| 数学 | `$color-pale-peach` | 同色 30% | `#4e453c` / dark green |
| 英语 | `$color-mint-green-bright` | `$color-mint-light` | `$color-dark-green` |
| 科学 | `$color-soft-lilac` | 同色 30% | `$color-dark-green` |
| 默认 | 现有 organic container | 现有 container | existing variant |

计划卡复用 `subjectIcon()` 的现有映射或抽取共享 helper，避免 Task 与 Plan 科目图标分叉。

### Header 与 Badge

- Header 使用 Flex，align center，gap 8px；
- 科目图标圆 30×30px；
- 标题 16px/22px、700、深绿色，`flex:1; min-width:0`；
- 标题过长 ellipsis，不挤压 badge；
- Badge 4px 10px、full radius、12px；
- 状态 Badge 是 Header 末端 flex child，不使用绝对定位；
- 听写 Badge 位于状态前或后，顺序全局一致；
- 小屏若两 badge 无法容纳，优先保持状态并把听写信息留在 metadata，不允许标题溢出。

### 计划内容区

- 圆角 16px、padding 20px；
- “每天 1 份”为主操作信息，14–16px、700；
- 日期范围 14px、700；
- 进度轨道 full radius，颜色来自当前科目或 dark green，不引入新色；
- 生成摘要 12–14px variant；
- metadata 可换行，不横向滚动；
- 描述最多两行，空时不渲染并回收空间。

### 操作

- 编辑为主次层级中的主要卡片操作，使用现有科目 action background；
- 删除为低强调危险文字/按钮，不与编辑等权重；
- 点击区域不小于 44px 高；
- busy 时两个操作均禁用，避免重复请求。

## 第三部分：页面视觉连续性

### 布置页

复用当前：

- 固定居中 AppBar（按确认原型不显示左菜单按钮）；
- 每字段一个 rounded card；
- subject pills；
- field input/textarea；
- dictation mint card；
- 绿色渐变发布按钮；
- 原 `BottomNav`。

时间范围控件：

- 使用与 field input 相同的容器背景、圆角和内边距；
- 下拉箭头不得依赖 Web-only 伪元素作为 UniApp 唯一实现；
- custom 日期在控件下方出现；
- 375px 下可双列，若实际 picker 文本溢出则切为纵向；
- 摘要使用现有 mint/light surface，不创造强调色。

### Dashboard

必须保留当前：

- 固定 AppBar 的头像、标题和退出入口；
- Hero `40px 120px 40px 120px` 非对称圆角；
- Hero `$color-mint-light`、32px padding、现有进度结构；
- 家庭码；
- Pending/Done Task 卡原 DOM 次序和 badge 位置；
- 现有悬浮胶囊 `BottomNav`。

新增计划区放在所有具体作业内容之后。以 section divider 分隔；标题使用现有 section label 层级。

不得为了新增计划重写 Hero、Task Card 或 BottomNav。原型中的这些区域只用于展示布局，执行必须以真实组件代码为准。

### 编辑页

- 二级全屏页面，白色/现有 appbar；
- 左侧返回按钮，标题居中；
- 不渲染 BottomNav；
- 表单卡复用创建页样式；
- 顶部警示使用现有 surface/semantic 颜色；若无 warning token，优先复用现有 ConfirmModal warning 视觉；
- 保存按钮复用发布主按钮；
- 删除入口与保存按钮分离；
- bottom spacer 覆盖设备安全区。

## 第四部分：交互契约

### 表单校验

- 首次完整校验发生于发布/保存；
- 用户修改错误字段后清除该字段错误；
- 日期变化立即重算日期关系；
- 错误紧随字段/字段组，含明确文案；
- 不仅依赖红色；
- 失败后滚动并聚焦第一个错误（UniApp 能力允许范围内）。

### 听写关闭

- 创建页关闭时不提交词条；
- 编辑页切换关闭时暂存本地词条，避免误触即丢失；
- 保存关闭状态后服务端模板词条被替换为空；
- 若用户再次打开且尚未保存，恢复暂存词条；
- 已生成 Task 听写不受影响。

### 未保存返回

使用 `ConfirmModal`：

- type 使用项目现有 warning；
- title “放弃修改”；
- desc “尚未保存的修改将会丢失。”；
- cancel “继续编辑”；
- confirm “放弃修改”；
- 无 dirty state 不弹窗；
- 保存中屏蔽返回。

### 删除确认

使用 `ConfirmModal`：

- 语义为 danger/warning，取决于组件现有可用类型；
- title “删除这个计划？”；
- desc “删除后将停止生成后续作业，已经生成的作业仍会保留。”；
- cancel “取消”；
- confirm “确认删除”；
- 确认中禁用重复操作。

### 通知

- 成功使用现有 `uni.showToast`；
- 字段错误使用 inline 文案，不只 Toast；
- materialize warning 每次进入最多提示一次；
- 局部计划加载错误在区域内重试；
- 409 提供刷新动作，不自动覆盖本地修改。

### Loading 与 Empty

- 页面详情 loading 时不展示未回填表单；
- 活动计划 loading 不阻塞今日作业；
- 无活动计划显示“暂无进行中的作业计划”，可提供去布置入口；
- 同步中不阻塞缓存作业交互；
- 保存/删除按钮展示中文进行态。

## Visual Source

- **类型**：已确认 HTML 原型 + UI/UX spec helper + existing page code。
- **来源**：`fp-docs/changes/recurring-homework-plan/prototype.html`、`client/src/pages/parent/task-create.vue`、`client/src/pages/parent/dashboard.vue`、`client/src/components/BottomNav.vue`、`client/src/components/ConfirmModal.vue`、`client/src/static/styles/variables.scss`。
- **可信边界**：原型确认时间选择、条件听写、计划卡、完整编辑和页面归属；真实代码确认颜色、尺寸、排版、圆角、阴影、导航和现有组件行为。H5/移动端最终渲染、原生 picker 和安全区仍需 local viewer 验证。

## UI 组件树与 Figma 解析映射

本功能无 Figma；此表将确认原型区域映射到项目组件和流式布局。

| 设计区域/节点 | 目标 DOM/组件层级 | 项目组件 | 布局策略 | 关键 token/尺寸 | 备注 |
| --- | --- | --- | --- | --- | --- |
| 布置页时间计划 | Card → Picker/Select → ConditionalDates → Summary | 页面字段组 | Column；日期 Row/自适应 Column | field 12px radius；Card 24px | 原型确定交互 |
| 听写设置 | DictationConfig → Header + ConditionalBody | 新增 `DictationConfig` | Header Row，Body Column | 现有 dictation mint card | 关闭时 Body 不渲染 |
| Dashboard 计划区 | Section → HomeworkPlanCard[] | 新增卡片 | Column list，16px gap | section label / divider | 位于具体作业后 |
| 计划卡 Header | Icon + Title + Status + Feature | HomeworkPlanCard 内部 | Flex；Title flex 1 | icon 30；badge 4×10 | 禁止 absolute badge |
| 计划内容 | TintedContent → Progress/Metadata/Desc | HomeworkPlanCard 内部 | Column；chips wrap | radius 16；padding 20 | 科目现有配色 |
| 编辑页 | AppBar + Scroll Cards + Save + Delete | ConfirmModal + 表单组件 | 全屏 Column/scroll | 创建页 card/input token | 无 BottomNav |
| 未保存确认 | Modal title/desc/actions | `ConfirmModal` | 组件既有布局 | warning | 脏表单才显示 |
| 删除确认 | Modal title/desc/actions | `ConfirmModal` | 组件既有布局 | danger/warning | 文案说明保留实例 |
| 底部导航 | Float Nav → Item → IconWrap + Label | `BottomNav` | 现有 fixed flex | bottom 24；min 280 | 直接复用，不重建 |

## Visual Checks

- [ ] 布置页默认显示“今日作业”，自定义日期字段不存在于可见布局（来源：确认原型）。
- [ ] 选择 custom 才出现起止日期，切回后错误清除（来源：确认原型/UX 契约）。
- [ ] 听写关闭时输入、词条和说明不进入渲染树（来源：确认 PRD/原型）。
- [ ] Dashboard Hero DOM、非对称圆角、mint 背景、32px padding 和进度条无回归（来源：`dashboard.vue`）。
- [ ] 现有 Task 状态 badge 保持标题行末端 flex child，不绝对定位（来源：`dashboard.vue`）。
- [ ] 活动计划仅在家长 Dashboard 底部，不在布置页或学生页面（来源：确认原型）。
- [ ] 计划状态与听写功能标签可区分，标题过长不挤压状态（来源：确认原型 + 现有 header pattern）。
- [ ] 计划内容区使用对应科目现有配色，metadata 自动换行（来源：`dashboard.vue`）。
- [ ] 描述最多两行；空描述不留下空白块（来源：确认设计）。
- [ ] 编辑页回填完成前不闪空表单，且不展示 BottomNav（来源：确认原型/UX）。
- [ ] 未保存返回和删除均使用 `ConfirmModal` 且文案一致（来源：现有组件 + PRD）。
- [ ] `BottomNav` 保持 bottom 24px、min-width 280px、pill blur 和 active icon wrap（来源：`BottomNav.vue`）。
- [ ] 页面 bottom spacer 使最后一张计划卡不被 BottomNav 遮挡（来源：现有布局约束）。
- [ ] 375px 宽度下日期、badge、metadata 和按钮无横向溢出（来源：移动端目标）。
- [ ] 深浅文字及错误状态不只依靠颜色表达（来源：可访问性约束）。
- [ ] 软键盘打开时保存操作和当前输入可访问（来源：移动表单 UX）。
- [ ] H5 预览无控制台错误、失败网络请求或未处理 Promise（来源：项目验证要求）。

## 第五部分：组件测试

### DictationConfig

- disabled/closed/open 渲染；
- trim、空值、重复值；
- 删除和事件 payload；
- error 显示与清除；
- 编辑关闭后本地词条保留。

### HomeworkPlanCard

- active/upcoming 状态；
- 有/无听写；
- 各科目 token；
- 有/无描述和时长；
- 长标题与多 metadata；
- edit/delete event；
- busy 禁用。

### Visual integration

用项目 preview 工具启动 H5：

1. 检查创建页四种范围；
2. 检查听写显隐；
3. 检查 Dashboard 现有区域无回归；
4. 滚动到底部检查计划卡与悬浮导航；
5. 进入编辑页检查回填、确认弹窗和安全区；
6. 调整 mobile/tablet viewport；
7. 检查 console、server logs 和失败请求；
8. 用 inspect 核对关键 DOM 的计算样式，而非只凭截图。
