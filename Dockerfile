FROM python:3.11-slim

ARG APP_VERSION=1.2.0
ENV APP_VERSION=$APP_VERSION
LABEL org.opencontainers.image.title="Study Buddy API" \
      org.opencontainers.image.version="$APP_VERSION"

WORKDIR /app

# 配置阿里云 pip 镜像源
RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/

# 安装运行时依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码并准备运行目录
COPY . .
RUN chmod +x docker-entrypoint.sh \
    && mkdir -p /app/tmp /app/logs \
    && useradd -m appuser \
    && chown -R appuser:appuser /app

USER appuser
EXPOSE 8000
ENTRYPOINT ["./docker-entrypoint.sh"]
