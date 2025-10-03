#!/bin/bash
set -e

trap "kill 0" EXIT

echo ">>> Starting Django server..."
gunicorn xazna.asgi:application -k uvicorn.workers.UvicornWorker -w 4 -b 0.0.0.0:8000 &

echo ">>> Starting Celery beat..."
celery -A xazna beat -S django &

echo ">>> Starting Celery workers..."
celery -A xazna worker -P prefork -c 2 -Q check,clean -n periodic_task@%h &
celery -A xazna worker -P prefork -c 1 -Q email -n email_task@%h &

echo ">>> Waiting for Celery workers to be ready..."
until celery -A xazna status | grep -q "OK"; do
    echo ">>> Workers not ready yet, retrying in 1 second..."
    sleep 1
done

echo ">>> Starting Celery flower..."
celery -A xazna flower --port=5555 &

wait
