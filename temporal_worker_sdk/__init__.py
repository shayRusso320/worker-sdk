"""Temporal Worker SDK — production-grade wrapper around temporalio.

A zero-boilerplate SDK for running Temporal workers with automatic:
- Configuration from environment variables
- Graceful shutdown handling
- Structured JSON logging
- Kubernetes health probes
- Prometheus metrics
"""

import os

from temporal_worker_sdk.core import TemporalSDK
from temporal_worker_sdk.config import SDKConfig, TemporalConfig, WorkerConfig, HealthProbeConfig

__version__ = os.getenv("SETUPTOOLS_SCM_PRETEND_VERSION", "0.1.0")
__all__ = [
    "TemporalSDK",
    "SDKConfig",
    "TemporalConfig",
    "WorkerConfig",
    "HealthProbeConfig",
]
