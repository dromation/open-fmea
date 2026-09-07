FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    OPEN_FMEA_DEBUG=1 \
    OPEN_FMEA_SECRET_KEY=open-fmea-container-demo-local-only \
    OPEN_FMEA_DB_PATH=/data/open_fmea_demo.sqlite3 \
    PORT=8000

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY LICENSE README.md manage.py pyproject.toml ./
COPY domain ./domain
COPY django_app ./django_app
COPY docs ./docs
COPY samples ./samples
COPY docker-entrypoint.sh ./docker-entrypoint.sh

RUN adduser --disabled-password --gecos "" openfmea \
    && mkdir -p /data \
    && chown -R openfmea:openfmea /app /data \
    && chmod +x /app/docker-entrypoint.sh

USER openfmea

EXPOSE 8000
VOLUME ["/data"]

ENTRYPOINT ["/app/docker-entrypoint.sh"]

