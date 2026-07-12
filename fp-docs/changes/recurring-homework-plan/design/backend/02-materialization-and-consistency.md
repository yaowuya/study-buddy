# Backend：实例化与一致性

## 第一部分：业务日期

服务端是“今天”的唯一权威来源。

- 作业目标日期使用 SQL `DATE`；
- 使用项目配置的业务时区计算 `today`；
- 客户端时间只用于展示，不决定补生成上限；
- 7 日和 30 日预设由服务端计算并校验；
- 设计不得以 UTC 时间戳直接截断得到业务日期；
- 若当前配置没有显式业务时区，实现计划必须先增加配置，并给出与当前部署地区一致的默认值。

## 第二部分：Materializer 服务

建议入口：

```python
materialize_family_plans(db, family_id, through_date) -> MaterializeResult
```

职责：

1. 查询当前家庭可能需要生成的计划；
2. 为每个计划建立独立事务边界；
3. 计算缺失目标日期；
4. 创建 Task 快照和 DictationItem 快照；
5. 汇总每个计划的创建日期与失败代码；
6. 不负责查询最终作业列表。

调用者在 materialize 返回后使用新的 Session 或已清理事务状态继续获取作业。

### 候选计划

应包含：

```text
family_id = current family
is_deleted = false
start_date <= through_date
```

即使 `end_date < today`，只要过去可能存在遗漏日期，也需要补齐到其结束日期。这一点区别于活动计划列表：活动列表只展示未过期计划，而补生成必须考虑历史遗漏。

目标上限：

```text
upper = min(plan.end_date, through_date)
```

若 `upper < plan.start_date`，跳过。

## 第三部分：缺失日期算法

对单个计划：

1. 生成 `[start_date, upper]` 的连续自然日集合；
2. 一次性查询该计划在范围内已有 Task 的日期；
3. 以集合差得到缺失日期；
4. 按日期升序创建。

伪代码：

```python
all_dates = date_range(plan.start_date, min(plan.end_date, today))
existing = set(select(Task.date).where(
    Task.source_plan_id == plan.id,
    Task.date.between(first, last),
))
missing = [day for day in all_dates if day not in existing]
```

不得对每个日期单独执行 exists 查询，避免 N+1。

## 第四部分：快照创建

每个缺失日期创建 Task：

- `family_id = plan.family_id`
- `type = plan.type`
- `title = plan.title`
- `desc = plan.desc`
- `duration = plan.duration`
- `status = pending`
- `date = target_date`
- `subject = plan.subject`
- `source_plan_id = plan.id`
- `is_deleted = false`

随后按 `position` 复制全部模板听写词条到普通 `DictationItem`。实例执行和 TTS 只能读取具体 Task 的词条，不回查计划模板。

若普通听写词条后续增加语速、停顿或其他参数，模板词条与复制逻辑必须同步覆盖这些可执行字段。

## 第五部分：事务边界

用户确认按计划分别提交。

建议顶层流程：

```text
for each plan id:
  begin plan transaction
    lock and reload plan
    validate family/deleted/range
    query existing dates
    create all missing Task snapshots
    copy all dictation snapshots
  commit
  append success result
on plan error:
  rollback this plan
  append failed result
continue next plan
```

同一计划本次所有缺失日期为原子操作：任一日期或词条失败，回滚该计划本轮全部新实例；已在此前调用中提交的实例不受影响。

不同计划互不回滚。

SQLAlchemy Session 在计划失败后必须显式 rollback，才能继续处理下一计划。设计实现时可采用每计划独立 Session 或清晰的 transaction/context 管理，禁止在 failed transaction 上继续查询。

## 第六部分：锁与竞争

### 锁顺序

创建/编辑/删除/生成对同一计划都遵循：

1. 以计划 ID 查询；
2. 对计划行 `SELECT ... FOR UPDATE`；
3. 重新校验家庭、删除状态和日期；
4. 再修改模板或创建实例；
5. 提交。

统一锁顺序避免：

- 生成读取旧模板而编辑已提交新模板；
- 删除提交后仍继续生成；
- 两个同步请求同时生成同一日期。

SQLite 测试不具备与 PostgreSQL 完全相同的行锁语义，因此：

- 单元/集成测试覆盖业务和唯一约束；
- PostgreSQL 并发行为需要至少一组真实数据库验证或明确的集成测试环境；
- 不可仅凭 SQLite 并发测试宣称锁正确。

### 唯一约束最终防线

`UNIQUE(source_plan_id, date)` 是最终幂等保证。应用层查询只减少冲突，不能替代约束。

在计划行锁有效且所有写路径遵循锁协议时，冲突应少见；若仍遇唯一冲突：

- 回滚到安全事务边界；
- 查询已有实例；
- 若已有实例属于同一计划和日期，将其视为幂等已存在；
- 不再次复制听写词条；
- 其他完整性错误按计划失败处理。

不得吞掉无法证明为该幂等键的 IntegrityError。

## 第七部分：编辑与生成一致性

### 编辑先获得锁

- 编辑更新模板并提交；
- 后续生成获得锁并读取新模板；
- 已存在实例保持旧快照。

### 生成先获得锁

- 生成使用当时模板创建全部缺失实例并提交；
- 编辑等待后更新模板；
- 本轮生成实例保持旧快照，下一轮使用新模板。

这形成明确的提交顺序，不出现半数实例使用旧模板、半数使用新模板的情况。

## 第八部分：删除与生成一致性

### 删除先提交

同步获得锁后读取到 `is_deleted = true`，直接跳过。

### 生成先提交

本轮已生成的实例属于删除前发生的有效快照，保留；删除随后标记计划，之后不再生成。

DELETE 与 materialize 必须使用相同锁协议。仅在 API 层先检查 `is_deleted` 而不在事务锁内复查是不充分的。

## 第九部分：日期范围变更

### 缩短范围

- 不删除任何已生成实例；
- materializer 只遍历新的结束日期以内；
- 已生成但超过新结束日期的作业继续存在并可执行。

### 延长范围

后续 materialize 自然生成新扩展日期。

### 修改尚未开始的开始日期

- 向后移动：不应存在已生成实例；若异常存在，拒绝更新并记录一致性问题；
- 向前移动：后续 materialize 可补生成新增日期，但不早于创建/校验允许的业务日期。

## 第十部分：同步接口行为

### 成功与部分失败

HTTP 请求本身成功执行并获得逐计划结果时返回 200，即使某些计划状态为 failed。响应顶层包括：

- `created_count`
- `success_count`
- `failed_count`
- `plans[]`

每个计划结果包括：

- `plan_id`
- `status: success | failed`
- `created_dates`
- `error_code?`

稳定错误代码示例：

- `materialization_failed`
- `plan_changed`
- `plan_unavailable`

不得返回内部异常内容。

### 整体失败

鉴权、家庭缺失或无法开始任何数据库工作按正常 4xx/5xx 返回。

前端无论同步部分失败还是整体失败，都应继续调用 GET 获取已有作业。

## 第十一部分：性能

- 一次查询候选计划并预加载模板词条，避免计划词条 N+1；
- 每计划一次查询已有日期；
- 每计划一次批量 flush/commit，而非每日期 commit；
- 活动计划卡的 `generated_count` 使用聚合查询，避免逐卡查询；
- 对 `homework_plans(family_id, is_deleted, start_date, end_date)` 设计合适索引；
- 对 `tasks(source_plan_id, date)` 唯一索引同时服务缺失查询；
- 为异常超长范围设置保护上限或批处理策略，但不能静默截断；超过阈值应记录并返回可重试错误；
- 当前产品范围最多常用 30 天，自定义范围上限若 PRD 未明确，技术实现前应将保护值列入配置或请求校验。

## 第十二部分：可观测性

每次同步记录结构化信息：

- family ID（按日志隐私规范处理）；
- 候选计划数；
- 每计划缺失、创建和耗时；
- 失败错误代码；
- 唯一冲突次数；
- 总耗时。

不得记录听写正文、JWT 或完整异常响应给客户端。

建议指标：

- materialize 请求量与延迟；
- 新增实例数量；
- 失败计划比例；
- 唯一冲突数量；
- 单请求最大补生成天数。

## 第十三部分：测试策略

### 纯逻辑测试

- 含首尾日期的连续范围；
- 跨月、跨年和闰日；
- `min(end_date, today)` 上限；
- 已有日期集合差；
- 7 天/30 天预设。

### SQLite 集成测试

- 创建计划和模板词条；
- 补齐单日和多日；
- 重复 materialize 不重复；
- 听写顺序和内容完整复制；
- 编辑后旧实例不变、新实例用新模板；
- 删除后不再生成、旧实例保留；
- 一个计划失败不影响另一个计划；
- 家庭和角色权限；
- 一次性作业回归。

### PostgreSQL 并发测试

- 两个 Session 同步同一计划；
- 家长和学生并发同步；
- 编辑与同步竞争；
- 删除与同步竞争；
- 唯一冲突只产生一个实例；
- 锁等待后读取最新删除/模板状态。

### API 测试

- 逐计划结构化结果；
- 部分失败仍 200 且包含 failed_count；
- 整体鉴权/家庭错误；
- 同步后 GET 返回具体实例；
- GET 本身不写数据库。

## 第十四部分：一致性验收

- 任意并发下同一 `(source_plan_id, date)` 最多一条 Task；
- 每条新实例拥有完整、独立的听写快照；
- 同一计划单轮生成要么全部新增日期成功，要么本轮全部回滚；
- 不同计划故障互不影响；
- 删除提交后没有新的生成事务能创建该计划实例；
- 编辑与生成以锁的提交顺序决定模板版本；
- 已生成 Task 的文本、听写、状态和提交永不被计划更新覆盖；
- 同步失败不阻塞读取已有作业。
