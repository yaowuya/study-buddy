#!/bin/sh
set -e

LOG_DIR=/app/logs
mkdir -p $LOG_DIR

echo "Running database migrations..."
alembic upgrade head 2>&1 | tee -a $LOG_DIR/app.log

echo "Starting application..."
exec gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 --access-logfile $LOG_DIR/access.log --error-logfile $LOG_DIR/error.log 2>&1 | tee -a $LOG_DIR/app.log
