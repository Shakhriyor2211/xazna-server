#!/bin/bash
set -e

echo ">>> Starting Django server..."
gunicorn xazna.asgi:application -k uvicorn.workers.UvicornWorker -w 4 -b 0.0.0.0:8000 &

echo ">>> Starting Celery beat..."
celery -A xazna beat -S django &

echo ">>> Starting Celery workers..."
celery -A xazna worker -P prefork -c 2 -Q check,clean -n periodic_task@%h &
celery -A xazna worker -P prefork -c 1 -Q email -n email_task@%h &

echo ">>> Starting Celery flower..."
celery -A xazna flower --port=5555 &

wait
