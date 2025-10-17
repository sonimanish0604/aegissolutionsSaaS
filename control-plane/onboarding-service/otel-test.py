import logging
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource

resource = Resource.create({
    "service.name": "otel-test",
    "service.namespace": "aegis",
    "service.version": "dev",
    "deployment.environment": "local",
})

trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer("otel.test")

with tracer.start_as_current_span("test-span"):
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("otel.audit")
    logger.info("Log inside trace span", extra={"trace": "yes"})