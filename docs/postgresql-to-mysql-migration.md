# PostgreSQL 到 MySQL 迁移手册

适用项目：作业陪伴助手 Study Buddy。

目标：线上 Ubuntu 环境从旧 PostgreSQL 数据库迁移到 MySQL，并让应用继续使用现有 FastAPI + SQLAlchemy + Alembic 结构运行。

## 迁移策略

推荐顺序：

1. 备份 PostgreSQL。
2. 在 MySQL 中创建空库和账号。
3. 使用当前项目 Alembic 在 MySQL 中创建表结构。
4. 使用 `pgloader` 只迁移数据，不让 `pgloader` 自动创建表结构。
5. 校验核心表记录数。
6. 切换 `.env` 的 `DATABASE_URL`。
7. 重启服务并观察日志。

项目 UUID 字段在 MySQL 中使用 `CHAR(36)` 存储，Python 层仍然读写 `uuid.UUID`。

## 1. 进入维护窗口

迁移前需要停止写入，避免 PostgreSQL 迁移过程中仍有新数据产生。

如果是 systemd 服务：

```bash
sudo systemctl stop study-buddy
```

如果是 Docker/Compose：

```bash
docker compose down
```

## 2. 备份 PostgreSQL

```bash
mkdir -p ~/studybuddy-backups
pg_dump -h 127.0.0.1 -p 5432 -U postgres -Fc studybuddy > ~/studybuddy-backups/studybuddy_$(date +%F_%H%M%S).dump
```

同时记录各表数量，后面用于对比：

```bash
psql -h 127.0.0.1 -p 5432 -U postgres -d studybuddy
```

```sql
SELECT 'families' AS table_name, COUNT(*) FROM families
UNION ALL SELECT 'users', COUNT(*) FROM users
UNION ALL SELECT 'tasks', COUNT(*) FROM tasks
UNION ALL SELECT 'dictation_items', COUNT(*) FROM dictation_items
UNION ALL SELECT 'submissions', COUNT(*) FROM submissions
UNION ALL SELECT 'mistakes', COUNT(*) FROM mistakes;
```

## 3. 安装 MySQL 依赖

```bash
sudo apt update
sudo apt install -y mysql-server pgloader
```

如果项目虚拟环境还没有安装依赖：

```bash
cd /path/to/study-buddy
source .venv/bin/activate
pip install -r requirements.txt
```

## 4. 创建 MySQL 数据库和账号

```bash
sudo mysql
```

```sql
CREATE DATABASE studybuddy CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'studybuddy'@'localhost' IDENTIFIED BY '请替换为强密码';
GRANT ALL PRIVILEGES ON studybuddy.* TO 'studybuddy'@'localhost';
FLUSH PRIVILEGES;
```

## 5. 用 Alembic 创建 MySQL 表结构

在项目目录写入或修改 `.env`：

```env
DATABASE_URL=mysql+pymysql://studybuddy:请替换为强密码@localhost:3306/studybuddy
SECRET_KEY=请使用生产环境密钥
```

执行迁移：

```bash
cd /path/to/study-buddy
source .venv/bin/activate
alembic upgrade head
```

确认 UUID 字段是 `char(36)`：

```bash
mysql -ustudybuddy -p studybuddy
```

```sql
SHOW COLUMNS FROM users;
SHOW COLUMNS FROM tasks;
```

## 6. 使用 pgloader 只导入数据

创建 `pg-to-mysql.load`：

```lisp
LOAD DATABASE
     FROM postgresql://postgres:root@127.0.0.1:5432/studybuddy
     INTO mysql://studybuddy:请替换为强密码@127.0.0.1:3306/studybuddy

WITH data only, truncate

INCLUDING ONLY TABLE NAMES MATCHING
    ~/families/,
    ~/users/,
    ~/tasks/,
    ~/dictation_items/,
    ~/submissions/,
    ~/mistakes/;
```

执行：

```bash
pgloader pg-to-mysql.load
```

说明：

- `data only` 表示只导数据，不由 `pgloader` 创建表。
- `truncate` 会先清空 MySQL 目标表，所以只应在新建空库或确认可覆盖时使用。
- 如果 PostgreSQL 密码、MySQL 密码包含特殊字符，建议 URL encode，或临时使用不含特殊字符的迁移账号。

## 7. 校验 MySQL 数据

```bash
mysql -ustudybuddy -p studybuddy
```

```sql
SELECT 'families' AS table_name, COUNT(*) FROM families
UNION ALL SELECT 'users', COUNT(*) FROM users
UNION ALL SELECT 'tasks', COUNT(*) FROM tasks
UNION ALL SELECT 'dictation_items', COUNT(*) FROM dictation_items
UNION ALL SELECT 'submissions', COUNT(*) FROM submissions
UNION ALL SELECT 'mistakes', COUNT(*) FROM mistakes;
```

再做几条关联检查：

```sql
SELECT COUNT(*) AS orphan_users
FROM users u
LEFT JOIN families f ON u.family_id = f.id
WHERE u.family_id IS NOT NULL AND f.id IS NULL;

SELECT COUNT(*) AS orphan_tasks
FROM tasks t
LEFT JOIN families f ON t.family_id = f.id
WHERE f.id IS NULL;

SELECT COUNT(*) AS orphan_submissions
FROM submissions s
LEFT JOIN tasks t ON s.task_id = t.id
WHERE t.id IS NULL;
```

三个 orphan 结果都应该是 `0`。

## 8. 切换应用到 MySQL

确认生产 `.env`：

```env
DATABASE_URL=mysql+pymysql://studybuddy:请替换为强密码@localhost:3306/studybuddy
```

如果应用跑在 Docker Compose 容器里，而 MySQL 跑在宿主机上，`localhost` 指的是容器自身，不是宿主机。此时应使用 `host.docker.internal`，并确保 `.env` 每个配置独占一行：

```env
# 数据库连接
DATABASE_URL=mysql+pymysql://studybuddy:请替换为强密码@host.docker.internal:3306/studybuddy
```

如果数据库密码包含特殊字符，需要做 URL 编码。例如密码里的 `@` 要写成 `%40`：

```env
DATABASE_URL=mysql+pymysql://paas:Cai%40180906@host.docker.internal:3306/studybuddy
```

重启服务：

```bash
sudo systemctl start study-buddy
sudo journalctl -u study-buddy -f
```

如果是 Docker/Compose：

```bash
docker compose up -d
docker compose logs -f
```

## 9. 回滚方案

迁移失败且尚未重新开放写入时：

1. 停止应用。
2. 将 `.env` 的 `DATABASE_URL` 改回 PostgreSQL。
3. 启动应用。
4. 保留 MySQL 失败现场，排查后重新迁移。

如果已经开放写入并产生了 MySQL 新数据，不要直接切回 PostgreSQL，否则会丢失新写入数据。需要先导出并人工合并新增数据。
