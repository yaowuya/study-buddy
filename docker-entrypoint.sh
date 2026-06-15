#!/bin/sh
set -e

LOG_DIR=${LOG_DIR:-/app/logs}
mkdir -p "$LOG_DIR" 2>/dev/null || true

echo "Running database migrations..."
if [ -w "$LOG_DIR" ]; then
    APP_LOG="$LOG_DIR/app.log"
    GUNICORN_LOG_ARGS="--access-logfile $LOG_DIR/access.log --error-logfile $LOG_DIR/error.log"
    alembic upgrade head 2>&1 | tee -a "$APP_LOG"
else
    echo "Warning: $LOG_DIR is not writable; logging to stdout/stderr only."
    alembic upgrade head
    GUNICORN_LOG_ARGS="--access-logfile - --error-logfile -"
fi

echo "Starting application..."
exec gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 $GUNICORN_LOG_ARGS
