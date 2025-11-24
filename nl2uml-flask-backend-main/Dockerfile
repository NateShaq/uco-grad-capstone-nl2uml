# syntax=docker/dockerfile:1
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    APP_HOME=/app \
    DATA_DIR=/var/lib/nl2uml \
    PLANTUML_JAR_PATH=/opt/plantuml/plantuml.jar

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      curl \
      openjdk-21-jre-headless \
      fontconfig \
      libfreetype6 \
      libharfbuzz0b \
 && rm -rf /var/lib/apt/lists/*

RUN useradd -u 10001 -m appuser \
 && mkdir -p $APP_HOME $DATA_DIR/db $DATA_DIR/diagrams \
 && chown -R appuser:appuser $APP_HOME $DATA_DIR

WORKDIR $APP_HOME

COPY requirements.txt ./
RUN python -m pip install --upgrade pip setuptools wheel \
 && pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /opt/plantuml
COPY plantuml-mit-1.2025.10.jar /opt/plantuml/plantuml.jar
RUN chown -R appuser:appuser /opt/plantuml

COPY app ./app

USER appuser
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD curl -fsS http://127.0.0.1:8080/health || exit 1

# Run plain WSGI (no websockets path for now)
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app", "--workers", "2", "--threads", "4"]
#CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:create_app()", "--workers", "2", "--threads", "4"]
