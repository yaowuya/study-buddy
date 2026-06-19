# 更新日志

## [1.0.0] - 2026-06-19

### 新功能

#### 客户端体验
- 完成 UniApp 客户端主要页面建设与整体 UI 升级，覆盖登录注册、家长今日作业、作业发布/编辑、批改、学生今日作业与听写流程
- 新增 Soft Organic Cards 风格的公共视觉变量与页面设计素材
- 新增 `ConfirmModal` 公共确认弹窗，替换系统原生弹框，统一删除等高风险操作体验
- 新增底部导航组件，优化家长端与学生端核心页面切换
- 作业历史支持按时间范围筛选，默认筛选本月并按日期倒序分组

#### 数据库与迁移
- 默认数据库从 PostgreSQL 切换到 MySQL，并补充 MySQL 兼容类型封装
- 新增 PostgreSQL 到 MySQL 的数据迁移脚本与迁移说明文档
- 更新 Alembic 迁移与测试，覆盖 MySQL 运行时配置和迁移兼容性

### 优化

#### 项目结构
- 将后端代码从 `backend/` 迁移到仓库根目录，统一 `app/`、`tests/`、`alembic/`、`requirements.txt` 等入口
- 更新 README 与部署配置，保持开发、测试、构建命令与当前目录结构一致

#### 前端适配
- 优化小屏手机任务卡片标题、状态徽章、听写标签的字号、内边距与换行布局
- 作业标题超长时单行截断显示，减少列表布局抖动
- 修复真机环境下作业历史卡片倾斜被截断的问题

#### 部署与日志
- 调整 Docker 构建上下文与容器命名，前端目录排除出后端镜像构建
- 容器日志目录挂载到宿主机 `/data/logs/studybuddy`
- TTS 临时目录改为 named volume，避免容器内写入权限问题
- 重构日志配置到 `app/core/logging.py`，统一应用日志文件输出

### 修复

- 修复任务列表接口忽略 `task_date` 参数导致返回所有任务的问题
- 修复 H5 开发环境登录失败的问题
- 登录时校验用户选择角色与账号实际角色，避免角色错配进入系统
- 修复 App 真机 `URLSearchParams` 未定义导致请求无法发送的问题
- 修复作业历史页面真机为空和日期筛选相关问题
- 修复 Docker 启动配置、日志目录权限与 TTS 临时文件写入问题

## [0.1.0] - 2025-01-17

### 新功能

#### 听写功能
- 实现听写功能，支持 TTS 语音朗读
- 集成百度 TTS API，支持基础/精品/臻品/大模型音库
- 支持通过环境变量配置默认语音
- 前端统一调用后端 TTS API

#### 用户认证
- 实现登录持久化，Token 有效期内免登录
- 登录页自动检查已登录状态并跳转

#### 部署
- 添加 Docker 部署配置
- 容器启动时自动执行数据库迁移
- 日志输出到文件并挂载到宿主机
- 配置阿里云 pip 镜像源加速依赖安装

### 优化

#### 用户体验
- 关闭 debugMode 消除 HTML5+ Runtime 弹框
- 历史页面通知铃铛改为退出按钮
- 修复首页和内容页被头部遮住的问题
- 修复布置作业页面输入框超出容器边界

#### 前端配置
- 使用条件编译配置 API 地址，适配 HBuilderX 打包
- App 打包后使用生产环境 API 地址

### 修复

- 修复 App 端语音合成兼容性问题
- 修复百度 TTS API 调用参数问题（tex 两次 urlencode、POST 请求）
- 修复前端 TTS URL 配置问题

---

## 部署说明

### 环境变量配置

```bash
# 后端 .env
DATABASE_URL=postgresql://postgres:password@host:5432/studybuddy
SECRET_KEY=your-secret-key
BAIDU_TTS_API_KEY=your-api-key
BAIDU_TTS_SECRET_KEY=your-secret-key
BAIDU_TTS_DEFAULT_VOICE=xiaoxian
```

### 可用语音列表

| 分类 | 音色 ID | 名称 |
|------|---------|------|
| 基础音库 | xiaomei, xiaoyu, xiaoyao, yaya | 度小美、度小宇、度逍遥、度丫丫 |
| 精品音库 | xiaoyao_pro, xiaolu, bowen, xiaotong, xiaomeng, miduo, xiaojiao | 度逍遥精品、度小鹿、度博文等 |
| 臻品音库 | xiaoxian, xiaowen, xiaoqiao, xinghe 等 | 度小贤、度小雯、度小乔、度星河等 |
| 大模型音库 | hanzhu, yanran, xiaoyue 等 | 度涵竹、度嫣然、度小粤（粤语）等 |
