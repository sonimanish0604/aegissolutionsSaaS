# app/deps/telemetry.py
from __future__ import annotations
import os, logging

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.logging import LoggingInstrumentor

# Environment metadata
SERVICE_NAME = os.getenv("OTEL_SERVICE_NAME", "onboarding-service")
SERVICE_NAMESPACE = os.getenv("OTEL_SERVICE_NAMESPACE", "aegis")
SERVICE_VERSION = os.getenv("OTEL_SERVICE_VERSION", "dev")
DEPLOY_ENV = os.getenv("DEPLOY_ENV", "dev")

# OTLP gRPC endpoint
OTLP_GRPC = os.getenv(
    "OTEL_EXPORTER_OTLP_ENDPOINT",
    "otel-collector-opentelemetry-collector.observability.svc.cluster.local:4317",
)

def init_otel() -> logging.Logger:
    # Resource metadata
    resource = Resource.create({
        "service.name": SERVICE_NAME,
        "service.namespace": SERVICE_NAMESPACE,
        "service.version": SERVICE_VERSION,
        "deployment.environment": DEPLOY_ENV,
    })

    # ----- Tracing -----
    tp = TracerProvider(resource=resource)
    trace.set_tracer_provider(tp)
    tp.add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter(endpoint=OTLP_GRPC, insecure=True))
    )

    # ----- Logging -----
    LoggingInstrumentor().instrument(set_logging_format=True)
    audit = logging.getLogger("onboarding.audit")
    audit.setLevel(logging.INFO)
    audit.propagate = False
    return audit