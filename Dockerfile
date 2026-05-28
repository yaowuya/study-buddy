FROM python:3.11-slim

WORKDIR /app

# 配置阿里云 pip 镜像源
RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn uvicorn[standard]

# 复制代码
COPY . .

# 复制并设置 entrypoint 脚本权限
RUN chmod +x docker-entrypoint.sh

# 创建临时文件目录
RUN mkdir -p /app/tmp

# 创建非 root 用户
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

ENTRYPOINT ["./docker-entrypoint.sh"]
