# 更新日志

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
