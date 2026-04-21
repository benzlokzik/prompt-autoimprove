"""OpenTelemetry tracer and meter setup."""

from __future__ import annotations

from opentelemetry import metrics, trace
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    ConsoleMetricExporter,
    PeriodicExportingMetricReader,
)
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

_INITIALIZED = False


def configure_tracing(service_name: str = "prompt-autoimprove") -> None:
    """Initialize global tracer and meter providers exactly once."""
    global _INITIALIZED
    if _INITIALIZED:
        return

    resource = Resource.create({SERVICE_NAME: service_name})

    tracer_provider = TracerProvider(resource=resource)
    tracer_provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
    trace.set_tracer_provider(tracer_provider)

    reader = PeriodicExportingMetricReader(
        ConsoleMetricExporter(), export_interval_millis=60_000
    )
    meter_provider = MeterProvider(resource=resource, metric_readers=[reader])
    metrics.set_meter_provider(meter_provider)

    _INITIALIZED = True


def get_tracer(name: str) -> trace.Tracer:
    return trace.get_tracer(name)


def get_meter(name: str) -> metrics.Meter:
    return metrics.get_meter(name)
