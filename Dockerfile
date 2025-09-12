FROM python:3.12.11-slim-bookworm

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD python manage.py migrate --noinput && \
    python manage.py collectstatic --noinput && \
    celery -A xazna worker -P prefork -c 4 -Q conversion -n conversion_worker@%h && \
    gunicorn xazna.wsgi:application --bind 0.0.0.0:8000
