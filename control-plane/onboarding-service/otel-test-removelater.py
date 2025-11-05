import logging
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource
# Resource metadata
resource = Resource.create({
    "service.name": "otel-test",
    "service.namespace": "aegis",
    "service.version": "dev",
    "deployment.environment": "local",
})
#from opentelemetry.sdk.logs import LoggerProvider, LoggingHandler, set_logger_provider
#from opentelemetry.sdk.logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.instrumentation.logging import LoggingInstrumentor

LoggingInstrumentor().instrument(set_logging_format=True)
trace.set_tracer_provider(TracerProvider(resource=resource))
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter(endpoint=OTLP_GRPC, insecure=True))
)

tracer = trace.get_tracer("otel.test")
with tracer.start_as_current_span("test-span"):
    audit.info("Log inside trace span", extra={"trace": "yes"})




# OTLP endpoint (adjust if needed)
OTLP_GRPC = "otel-collector-opentelemetry-collector.observability.svc.cluster.local:4317"

# Setup logger provider
lp = LoggerProvider(resource=resource)
set_logger_provider(lp)
lp.add_log_record_processor(BatchLogRecordProcessor(
    OTLPLogExporter(endpoint=OTLP_GRPC, insecure=True)
))

# Create audit logger
handler = LoggingHandler(level=logging.INFO, logger_provider=lp)
audit = logging.getLogger("otel.audit")
audit.setLevel(logging.INFO)
audit.handlers = [handler]
audit.propagate = False

# Emit test log
audit.info("OpenTelemetry test log emitted", extra={"test_id": "12345"})