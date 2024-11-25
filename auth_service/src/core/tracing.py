from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from auth_service.src.core.config import get_jaeger_settings, get_global_settings


def init_tracer():
    global_settings = get_global_settings()
    jaeger_settings = get_jaeger_settings()
    resource = Resource(attributes={'service.name': global_settings.project_name})
    tracer_provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer_provider)

    jaeger_exporter = JaegerExporter(
        agent_host_name=jaeger_settings.host,
        agent_port=jaeger_settings.port,
    )
    span_processor = BatchSpanProcessor(jaeger_exporter)
    tracer_provider.add_span_processor(span_processor)
