# app/deps/telemetry.py
from __future__ import annotations
import os, logging

from opentelemetry import trace
from opentelemetry import metrics
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.logs import LoggerProvider, LoggingHandler
from opentelemetry.instrumentation.logging import LoggingInstrumentor
LoggingInstrumentor().instrument(set_logging_format=True)

# Traces (gRPC, stable)
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

# Logs (gRPC, stable)
from opentelemetry.sdk.logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk.logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter

SERVICE_NAME = os.getenv("OTEL_SERVICE_NAME", "onboarding-service")
SERVICE_NAMESPACE = os.getenv("OTEL_SERVICE_NAMESPACE", "aegis")
SERVICE_VERSION = os.getenv("OTEL_SERVICE_VERSION", "dev")

# Single gRPC base for both traces + logs (host:port)
OTLP_GRPC = os.getenv(
    "OTEL_EXPORTER_OTLP_ENDPOINT",
    "otel-collector-opentelemetry-collector.observability.svc.cluster.local:4317",
)


def init_otel():
    resource = Resource.create(
        {
            "service.name": SERVICE_NAME,
            "service.namespace": SERVICE_NAMESPACE,
            "service.version": SERVICE_VERSION,
            "deployment.environment": os.getenv("DEPLOY_ENV", "dev"),
        }
    )

    # ----- Tracing -----
    tp = TracerProvider(resource=resource)
    trace.set_tracer_provider(tp)
    tp.add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter(endpoint=OTLP_GRPC, insecure=True))
    )

    # ----- Logging -----
    lp = LoggerProvider(resource=resource)
    logs.set_logger_provider(lp)  # correct module for set_logger_provider
    lp.add_log_record_processor(
        BatchLogRecordProcessor(OTLPLogExporter(endpoint=OTLP_GRPC, insecure=True))
    )

    # App audit logger -> OTLP logs
    handler = LoggingHandler(level=logging.INFO, logger_provider=lp)
    audit = logging.getLogger("onboarding.audit")
    audit.setLevel(logging.INFO)
    audit.handlers = [handler]
    audit.propagate = False
    return audit
