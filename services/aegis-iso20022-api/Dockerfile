# syntax=docker/dockerfile:1

FROM python:3.12-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_NO_CACHE_DIR=off \
    PYTHONDONTWRITEBYTECODE=1 \
    APP_HOME=/app

WORKDIR $APP_HOME

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libxml2-dev \
        libxslt1-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

COPY . .

RUN addgroup --system app && \
    adduser --system --ingroup app appuser && \
    chown -R appuser:app /app

USER appuser

EXPOSE 8080

CMD ["uvicorn", "src.translator_api.routes:app", "--host", "0.0.0.0", "--port", "8080"]
