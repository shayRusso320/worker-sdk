"""Configuration management for the Temporal SDK."""

from pydantic_settings import BaseSettings
from pydantic import Field


class TemporalConfig(BaseSettings):
    """Temporal server connection configuration.
    
    All values are read from environment variables.
    """

    host: str = Field(
        default="localhost",
        description="Temporal server host",
    )
    port: int = Field(
        default=7233,
        description="Temporal server port",
    )
    namespace: str = Field(
        default="default",
        description="Temporal namespace",
    )

    class Config:
        env_prefix = "TEMPORAL_"


class WorkerConfig(BaseSettings):
    """Worker configuration."""

    task_queue: str = Field(
        description="Task queue name for the worker",
    )
    max_concurrent_activities: int = Field(
        default=100,
        description="Maximum concurrent activities",
    )
    max_concurrent_workflow_tasks: int = Field(
        default=40,
        description="Maximum concurrent workflow tasks",
    )
    graceful_shutdown_timeout: int = Field(
        default=30,
        description="Graceful shutdown timeout in seconds",
    )

    class Config:
        env_prefix = "WORKER_"


class HealthProbeConfig(BaseSettings):
    """Health probe HTTP server configuration."""

    host: str = Field(
        default="0.0.0.0",
        description="Health probe server host",
    )
    port: int = Field(
        default=8080,
        description="Health probe server port",
    )
    enabled: bool = Field(
        default=True,
        description="Enable health probe server",
    )

    class Config:
        env_prefix = "HEALTH_PROBE_"


class SDKConfig(BaseSettings):
    """Root configuration for the SDK."""

    temporal: TemporalConfig = Field(default_factory=TemporalConfig)
    worker: WorkerConfig = Field(default_factory=WorkerConfig)
    health_probe: HealthProbeConfig = Field(default_factory=HealthProbeConfig)

    class Config:
        env_nested_delimiter = "__"
        case_sensitive = False
