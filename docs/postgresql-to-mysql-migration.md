# PostgreSQL 到 MySQL 迁移手册

适用项目：作业陪伴助手 Study Buddy。

目标：线上 Ubuntu 环境从旧 PostgreSQL 数据库迁移到 MySQL，并让应用继续使用现有 FastAPI + SQLAlchemy + Alembic 结构运行。

## 迁移策略

推荐顺序：

1. 备份 PostgreSQL。
2. 在 MySQL 中创建空库和账号。
3. 使用当前项目 Alembic 在 MySQL 中创建表结构。
4. 使用项目脚本只迁移数据，不让脚本自动创建表结构。
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
sudo apt install -y mysql-server
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

## 6. 使用项目脚本只导入数据

先 dry-run 查看 PostgreSQL 源库各表数量，不写入 MySQL：

```bash
python scripts/migrate_postgres_to_mysql.py \
  --source postgresql://postgres:root@127.0.0.1:5432/studybuddy \
  --target mysql+pymysql://studybuddy:请替换为强密码@127.0.0.1:3306/studybuddy \
  --dry-run
```

确认表数量符合预期后执行正式迁移：

```bash
python scripts/migrate_postgres_to_mysql.py \
  --source postgresql://postgres:root@127.0.0.1:5432/studybuddy \
  --target mysql+pymysql://studybuddy:请替换为强密码@127.0.0.1:3306/studybuddy
```

脚本默认按依赖顺序迁移：

```text
families
users
tasks
dictation_items
submissions
mistakes
```

说明：

- 目标 MySQL 表结构必须先通过 `alembic upgrade head` 创建。
- 脚本默认会先按反向依赖顺序清空目标表，再插入 PostgreSQL 数据。
- 如果目标表已有数据且不想清空，可加 `--no-truncate`，但主键重复会导致插入失败。
- 如果 PostgreSQL 密码、MySQL 密码包含特殊字符，连接 URL 中需要做 URL encode。例如 `@` 写成 `%40`。

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
DATABASE_URL=mysql+pymysql://studybuddy:your%40password@host.docker.internal:3306/studybuddy
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
