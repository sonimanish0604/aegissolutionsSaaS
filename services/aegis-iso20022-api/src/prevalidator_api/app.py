import logging
import os

from fastapi import FastAPI

from .routes import router
from audit_middleware import AuditMiddleware
from audit_emitter import KafkaAuditEmitter, LoggingEmitter

logger = logging.getLogger(__name__)


def _init_emitter():
    bootstrap = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
    topic = os.getenv("AUDIT_TOPIC", "audit.events")
    if bootstrap and KafkaAuditEmitter:
        try:
            return KafkaAuditEmitter(bootstrap_servers=bootstrap, topic=topic)
        except Exception as exc:  # pragma: no cover - fallback to logging
            logger.warning("Prevalidator Kafka emitter unavailable: %s", exc)
    return LoggingEmitter()


app = FastAPI(title="Aegis ISO20022 Prevalidator")
app.include_router(router)
app.add_middleware(AuditMiddleware, emitter=_init_emitter())


@app.get("/")
def healthcheck():
    return {"status": "ok"}
