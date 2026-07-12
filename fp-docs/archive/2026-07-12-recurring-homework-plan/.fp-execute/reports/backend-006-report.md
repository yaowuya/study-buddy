# backend-006 执行报告

## 完成内容

- CRUD 与物化服务统一通过 `_lock_plan` 先按计划 ID 获取 `FOR UPDATE` 行锁，再校验家庭、删除状态与日期。
- 物化在获取计划锁后加载听写模板，确保编辑/生成竞争使用明确的已提交模板版本。
- `IntegrityError` 回滚后重新查询全部目标 `(source_plan_id, date)`；仅在全部存在时归类为幂等成功，否则返回脱敏的 `materialization_failed`。
- 新增 PostgreSQL 双 Session 并发测试，覆盖同时物化、编辑后物化、删除后物化；缺少 `TEST_POSTGRES_URL` 时明确跳过。

## 验证

- 范围测试：`6 passed, 3 skipped`。
- 全量 SQLite 回归：`68 passed, 3 skipped`。
- PostgreSQL 并发测试因当前环境未设置 `TEST_POSTGRES_URL`，3 项按设计跳过。
