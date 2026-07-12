# Backend：领域模型与 API

## 第一部分：架构决策

### 决策 1：计划与作业分离

- **选择**：独立 `HomeworkPlan` 模板，按目标日期物化为普通 `Task` 快照。
- **理由**：保持现有不变量——每份可完成、提交和批改的作业都是具有稳定 UUID 的真实 `Task`；现有 Submission、听写、批改和历史链路无需理解计划。

### 决策 2：显式同步接口

- **选择**：通过专用幂等 POST 接口触发补生成，再调用现有 GET 作业列表。
- **理由**：避免 GET 产生数据库写入副作用，保持现有查询接口兼容并使同步结果可观测。

### 决策 3：按计划事务隔离

- **选择**：每个计划独立提交事务，一个计划失败不影响其他计划。
- **理由**：在家庭活动计划数量有限的前提下兼顾故障隔离和数据库往返成本。

### 决策 4：实例快照不可追随模板

- **选择**：生成时复制任务和听写内容；之后编辑或删除计划不修改实例。
- **理由**：确保学生看到、提交及家长批改的内容保持稳定。

## 第二部分：模块设计

### 新增模块

```text
app/
├── models/homework_plan.py
├── schemas/homework_plan.py
├── crud/homework_plan.py
├── services/homework_plan_materializer.py
└── api/v1/homework_plans.py
```

职责：

- `models/homework_plan.py`：计划及计划听写模板的持久化模型；
- `schemas/homework_plan.py`：计划命令、查询结果及同步结果契约；
- `crud/homework_plan.py`：家庭范围内的计划生命周期和活动查询；
- `services/homework_plan_materializer.py`：缺失日期计算、快照生成和结果汇总；
- `api/v1/homework_plans.py`：鉴权、输入校验、事务编排入口和响应映射。

### 修改模块

- `app/models/task.py`：增加可空来源计划外键及唯一约束；
- `app/models/__init__.py`：注册计划模型；
- `app/schemas/task.py`：可选暴露 `source_plan_id`，不改变既有字段语义；
- `app/main.py`：注册计划路由；
- `alembic/versions/`：新增计划表、来源字段、索引和约束。

## 第三部分：数据模型

### HomeworkPlan

表名建议：`homework_plans`。

| 字段 | 类型 | 约束与用途 |
| --- | --- | --- |
| `id` | UUID | 主键，默认生成 |
| `family_id` | UUID | 非空，外键 `families.id`，建立索引 |
| `created_by` | UUID | 非空，外键 `users.id`，记录创建家长 |
| `type` | String(10) | 非空，复用 `TaskType` 的 `school/home` 值 |
| `title` | String(100) | 非空 |
| `desc` | Text | 可空 |
| `duration` | Integer | 可空；非空时必须大于 0 |
| `subject` | String(20) | 可空，与现有 Task 一致 |
| `start_date` | Date | 非空，建立范围查询索引的一部分 |
| `end_date` | Date | 非空，必须不早于开始日期 |
| `is_deleted` | Boolean | 非空，默认 false，软删除 |
| `created_at` | DateTime(timezone) | 非空，服务端默认 |
| `updated_at` | DateTime(timezone) | 非空，更新时刷新；也作为乐观并发 token |

关系：

- `dictation_items`：一对多，模板词条随计划物理删除时级联；正常业务删除仅软删除计划；
- `tasks`：一对多，仅用于来源追踪，不对生成实例做 delete cascade。

计划是否开启听写由模板词条是否存在推导，不保存独立布尔字段，避免状态与词条不一致。

### HomeworkPlanDictationItem

表名建议：`homework_plan_dictation_items`。

| 字段 | 类型 | 约束与用途 |
| --- | --- | --- |
| `id` | UUID | 主键 |
| `plan_id` | UUID | 非空，外键 `homework_plans.id`，建立索引 |
| `content` | String(200) | 非空，去除首尾空白后不得为空 |
| `position` | Integer | 非空，用于稳定复制顺序 |

同一计划中的规范化 `content` 应避免重复。是否以数据库唯一约束实现由实现计划结合大小写语义确定；服务端必须校验重复。

### Task 扩展

新增：

```text
source_plan_id UUID NULL REFERENCES homework_plans(id)
```

并建立：

```text
UNIQUE (source_plan_id, date)
```

约束不包含 `is_deleted`，防止删除某个实例后再次生成同一计划同一日期的第二份作业。

普通一次性 Task 的 `source_plan_id = NULL`。PostgreSQL 和测试所用 SQLite 均允许普通 UNIQUE 中存在多行 NULL，因此既有任务互不冲突。

实例使用现有 `date` 作为计划目标日期，不再增加重复的 occurrence 字段。

### 迁移策略

1. 创建 `homework_plans`；
2. 创建 `homework_plan_dictation_items`；
3. 给 `tasks` 增加可空 `source_plan_id`；
4. 添加外键、查询索引和组合唯一约束；
5. 不回填历史任务，既有行保持 NULL；
6. 所有新非空字段使用安全 `server_default` 或分阶段建列，避免存量迁移失败；
7. 验证 PostgreSQL 升级和 SQLite 测试建表。

## 第四部分：Schema 契约

### 创建请求

`HomeworkPlanCreate`：

- `type`
- `title`
- `desc?`
- `duration?`
- `subject?`
- `range_type`: `week | month | custom`
- `start_date?`
- `end_date?`
- `dictation_items: list[DictationItemCreate] = []`

服务端规则：

- `week` 固定计算为含今天的连续 7 天；
- `month` 固定计算为含今天的连续 30 天；
- `custom` 必须提供起止日期；
- 多日计划不接受 `today`；今日作业继续使用现有 Task API；
- 客户端传入的预设日期不能覆盖服务端计算结果。

### 更新请求

`HomeworkPlanUpdate` 采用完整可编辑表单语义，并包含：

- 上述模板字段；
- 实际 `start_date`、`end_date`；
- 完整听写词条列表；
- `updated_at` 并发 token。

虽然 HTTP 方法使用 PATCH，服务端把可编辑模板视为一次完整替换，以避免遗漏字段和听写差异更新歧义。

### 输出结构

`HomeworkPlanOut` 提供持久字段和：

- `has_dictation`
- `dictation_count`
- `dictation_items`（详情接口；列表可按明确响应模型决定是否省略正文）
- `status`: `upcoming | active`
- `total_days`
- `generated_count`
- `remaining_days?`
- `days_until_start?`
- `today_generated`
- `updated_at`

派生数据由服务端基于业务日期和持久化实例计算，客户端不自行推断权威状态。

### 同步输出

```json
{
  "created_count": 3,
  "plans": [
    {
      "plan_id": "uuid",
      "created_dates": ["2026-07-09", "2026-07-10"],
      "status": "success",
      "error": null
    }
  ]
}
```

`error` 仅包含稳定、可面向客户端的错误代码，不暴露异常、SQL 或堆栈文本。

## 第五部分：API 契约

统一前缀建议：`/api/v1/homework-plans`。

| Method | Path | 角色 | 行为 |
| --- | --- | --- | --- |
| POST | `/` | 家长 | 创建计划；若今天生效，提交后实例化今天 |
| GET | `/` | 家长 | 返回当前家庭活动计划及卡片派生数据 |
| GET | `/{plan_id}` | 家长 | 返回计划完整详情和词条 |
| PATCH | `/{plan_id}` | 家长 | 乐观并发更新完整模板，不改实例 |
| DELETE | `/{plan_id}` | 家长 | 幂等软删除，保留实例 |
| POST | `/materialize` | 家长、学生 | 为当前家庭补齐截至今天的遗漏实例 |

### 家庭与角色权限

- 创建、列表、详情、编辑和删除使用 `require_parent`；
- 同步使用 `get_current_user`，允许学生和家长；
- 所有入口先确认用户已绑定家庭；
- 服务端从当前用户获取 `family_id`，不接受客户端家庭 ID；
- 单资源查询后校验 `plan.family_id == user.family_id`；
- 跨家庭或不存在资源统一返回 404。

### 创建行为

- 在一个事务中保存计划及模板词条；
- 若开始日期不晚于今天，计划提交后调用同一 materializer 为今天补建实例；
- 计划创建成功而当天实例化失败时，计划不得丢失；响应可返回创建成功并带同步警告，或创建后由页面专用同步接口重试；实现阶段必须选择一致行为。推荐先提交计划，再调用标准 materializer，使失败可重试且不会回滚有效计划。

### 编辑行为

- 对计划行加锁或以统一事务顺序读取；
- `updated_at` 与客户端 token 不同返回 409；
- 已开始计划拒绝修改 `start_date`；
- 未开始计划允许修改起止日期；
- `end_date` 不得早于今天，也不得早于开始日期；
- 替换模板词条时保持请求顺序；
- 不查询或更新既有实例内容；
- 缩短范围不删除已生成的超范围实例。

### 删除行为

- 对计划行使用与生成一致的锁顺序；
- 设置 `is_deleted = true` 并更新时间；
- 已删除计划重复 DELETE 视为幂等成功；
- 不删除计划模板来源记录或具体 Task；
- 不级联删除 Task 听写、提交、批改和错题数据。

## 第六部分：错误契约

| 场景 | 状态码 | 客户端行为 |
| --- | --- | --- |
| 未登录 | 401 | 进入登录流程 |
| 非家长管理计划 | 403 | 不展示管理入口并提示无权限 |
| 未绑定家庭 | 400 | 引导绑定家庭 |
| 资源不存在/跨家庭 | 404 | 返回作业页并刷新列表 |
| 请求字段或日期非法 | 422 | 映射到字段级错误 |
| `updated_at` 冲突 | 409 | 提示已被其他家长修改，刷新详情 |
| 单计划生成失败 | 同步结果 `failed` | 非阻塞提示并允许下次重试 |

## 第七部分：兼容性

- 现有 `POST /tasks` 继续创建一次性作业；
- 现有 `GET /tasks` 保持纯查询和具体作业语义；
- 现有状态更新、Submission、批改、Dictation API 均继续使用 Task UUID；
- 学生端不读取计划模板；
- Grading 和 History 继续处理具体 Task；
- 新增 `source_plan_id` 为可选字段，旧客户端可以忽略；
- 历史数据无需业务回填。

## 第八部分：接口与迁移验收

- OpenAPI 明确区分计划列表、详情、命令和同步响应；
- 所有管理端点都有家长与家庭隔离测试；
- Migration 在存量任务数据库上成功，旧任务可正常查询；
- 升级后现有 task API 测试全部通过；
- 创建/编辑计划不会让模板出现在普通 Task 列表；
- 删除计划不会破坏 Task 来源外键或现有提交。
