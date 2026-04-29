"""HTTP health probe endpoints and metrics exposure for Kubernetes."""

import logging
from fastapi import FastAPI
from fastapi.responses import Response
from pydantic import BaseModel
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from temporal_worker_sdk.config import HealthProbeConfig

logger = logging.getLogger(__name__)


class HealthStatus(BaseModel):
    """Health status response."""

    ready: bool
    connected: bool


class HealthProbeServer:
    """HTTP server for Kubernetes health probes."""

    def __init__(self, config: HealthProbeConfig) -> None:
        """Initialize health probe server.
        
        Args:
            config: Health probe configuration.
        """
        self.config = config
        self.app = FastAPI()
        self._connected = False
        self._setup_routes()

    def _setup_routes(self) -> None:
        """Set up health probe and metrics endpoints."""

        @self.app.get("/health/live")
        async def liveness() -> dict[str, str]:
            """Liveness probe — process is alive."""
            return {"status": "alive"}

        @self.app.get("/health/ready")
        async def readiness() -> HealthStatus:
            """Readiness probe — worker is connected and ready."""
            return HealthStatus(ready=self._connected, connected=self._connected)

        @self.app.get("/metrics")
        async def metrics() -> Response:
            """Prometheus metrics endpoint."""
            return Response(
                generate_latest(),
                media_type=CONTENT_TYPE_LATEST,
            )

    def set_connected(self, connected: bool) -> None:
        """Update connection status.
        
        Args:
            connected: Whether the worker is connected to Temporal.
        """
        self._connected = connected
        logger.info(
            "Health probe connection status updated",
            extra={"connected": connected},
        )

    async def start(self) -> None:
        """Start the health probe server."""
        if not self.config.enabled:
            logger.info("Health probe server is disabled")
            return

        import uvicorn

        config = uvicorn.Config(
            self.app,
            host=self.config.host,
            port=self.config.port,
            log_config=None,
        )
        server = uvicorn.Server(config)
        logger.info(
            "Starting health probe server",
            extra={"host": self.config.host, "port": self.config.port},
        )
        await server.serve()

    async def stop(self) -> None:
        """Stop the health probe server."""
        logger.info("Stopping health probe server")
