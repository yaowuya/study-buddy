# 作业陪伴助手 — 设计规格文档

> 日期：2026-05-10
> 状态：已确认

## 产品概述

家庭教育协作工具，解决双职工家庭孩子放学后独立完成作业的问题。家长远程布置任务，学生端自主执行（含语音听写），家长远程批改验收。

## 用户角色

- **家长**：任务发起者、验收者。使用手机端或 PC Web。
- **学生**：任务执行者。使用平板或手机端，UI 以大卡片大字体为主，防误触。

## 核心功能范围

### 家长端
1. 注册 / 登录，生成家庭连接码
2. 发布任务（学校任务 / 家庭任务）：标题、描述、预计耗时
3. 听写配置：批量录入词组、设置语速和停顿间隔
4. 任务追踪：列表/日历视图，实时进度（未开始/进行中/待批改）
5. 作业批改：查看完成状态、标记对错、填写评语
6. 错题本：自动归集错题，按学科分类，支持归档

### 学生端
1. 扫码 / 输入连接码绑定家庭
2. 今日任务看板：大卡片展示，区分学校/家庭任务
3. 任务状态流转：待开始 → 进行中 → 提交/完成
4. 听写模式：设备本地 TTS 报词，支持暂停/重播/跳词
5. 完成提交：点击"完成"即可提交任务
6. 完成激励：全部任务完成后全屏勋章动画

### 数据层
- 定时轮询同步（30 秒），无 WebSocket
- 离线缓存当日任务，断网可操作，恢复后同步
- 历史任务和错题数据可导出/导入

## 技术架构

### 后端
- **FastAPI** (Python) + **PostgreSQL** + SQLAlchemy 2.x + Alembic
- **JWT** 认证（python-jose）
- 部署：阿里云 ECS，Docker Compose（Nginx + FastAPI + PostgreSQL）

### 客户端
- **UniApp** (Vue 3 + TypeScript)，编译 iOS / Android / H5
- 状态管理：Pinia
- TTS：设备本地（APP 用 `plus.speech`，H5 用 `speechSynthesis`）
- 轮询：`sync store`，前台每 30s 拉取，退后台暂停

## 数据模型（核心）

```
User(id, role, family_code, hashed_password)
Family(id, code, parent_id, student_id)
Task(id, family_id, type, title, desc, duration, status, date)
DictationItem(id, task_id, content, speed, pause_interval)
Submission(id, task_id, comment, is_correct, submitted_at)
MistakeBook(id, task_id, subject, archived)
```

## API 结构

`/api/v1/` 前缀，Bearer JWT 鉴权。

| 模块 | 路径 |
|------|------|
| 认证 | `/auth/register`, `/auth/login`, `/auth/bind` |
| 任务 | `/tasks/` CRUD, `/tasks/{id}/status` |
| 听写 | `/dictation/` CRUD |
| 提交 | `/submissions/`, `/submissions/{id}/grade` |
| 错题本 | `/mistakes/`, `/mistakes/{id}/archive` |

## 界面设计规范

- 字体：Lexend（降低儿童阅读疲劳）
- 主色：Sky Blue `#005DA7`（家长端）/ `#4F46E5`（学生端）
- 圆角：容器 `24px`，卡片 `16px`，按钮 `12px`
- 触控最小目标：48×48px
- 间距：8px grid，卡片 padding 24px

## 关键约束

- 学生端离线时仍可查看当日任务，本地操作队列网络恢复后同步
- 无实时推送，家长发布后学生最长 30 秒内感知

## 参考资料

- 需求文档：`docs/requirements.md`
- 技术选型：`docs/tech-stack.md`
- Stitch 设计稿：
  - 作业陪伴助手：`projects/1261262470017047406`
  - 设计系统参考：`projects/13033815433092296680`
