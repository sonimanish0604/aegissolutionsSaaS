# syntax=docker/dockerfile:1

FROM python:3.12-slim AS builder

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PYTHONDONTWRITEBYTECODE=1 \
    APP_HOME=/app

WORKDIR $APP_HOME

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libxml2-dev \
        libxslt1-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY src ./src
COPY mappings ./mappings
COPY pre-validateMT ./pre-validateMT
COPY schemas ./schemas
COPY iso-bootstrap ./iso-bootstrap
COPY scripts ./scripts

FROM python:3.12-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    APP_HOME=/app

WORKDIR $APP_HOME

RUN apt-get update && apt-get install -y --no-install-recommends \
        libxml2 \
        libxslt1.1 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app/src ./src
COPY --from=builder /app/mappings ./mappings
COPY --from=builder /app/pre-validateMT ./pre-validateMT
COPY --from=builder /app/schemas ./schemas
COPY --from=builder /app/iso-bootstrap ./iso-bootstrap
COPY --from=builder /app/scripts ./scripts

RUN addgroup --system app && adduser --system --ingroup app appuser && \
    chown -R appuser:app /app

USER appuser

EXPOSE 8080

CMD ["uvicorn", "src.translator_api.routes:app", "--host", "0.0.0.0", "--port", "8080"]
