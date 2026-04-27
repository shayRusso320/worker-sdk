"""Temporal Worker SDK — production-grade wrapper around temporalio.

A zero-boilerplate SDK for running Temporal workers with automatic:
- Configuration from environment variables
- Graceful shutdown handling
- Structured JSON logging
- Kubernetes health probes
- Prometheus metrics
"""

__version__ = "0.1.0"

from temporal_worker_sdk.core import TemporalSDK
from temporal_worker_sdk.config import SDKConfig, TemporalConfig, WorkerConfig, HealthProbeConfig

__all__ = [
    "TemporalSDK",
    "SDKConfig",
    "TemporalConfig",
    "WorkerConfig",
    "HealthProbeConfig",
]
