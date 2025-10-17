#FROM python:3.11-slim
FROM mirror.gcr.io/library/python:3.11-slim
# System deps (optional but handy)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install Python deps
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# quick sanity to ensure drivers import correctly
#This ensures your build fails immediately if a required library or version is missing.
RUN python - <<'PY'
import asyncpg, sqlalchemy, uvicorn, opentelemetry.sdk
print("Driver smoke test OK")
PY

# Copy service code
COPY app ./app

# Expose service port
EXPOSE 8080

# Start the FastAPI app from app/main.py (object name: app)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
