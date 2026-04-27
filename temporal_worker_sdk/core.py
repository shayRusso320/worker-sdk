"""Core Temporal SDK implementation."""

import asyncio
import logging
from typing import Any, Type

from temporalio.client import Client
from temporalio.worker import Worker

from sdk.config import SDKConfig
from sdk.logging import setup_logging
from sdk.metrics import WorkerMetrics
from sdk.health_probe import HealthProbeServer
from sdk.shutdown import GracefulShutdownHandler

logger = logging.getLogger(__name__)


class TemporalSDK:
    """Production-grade Temporal worker SDK."""

    def __init__(self) -> None:
        """Initialize the SDK with configuration from environment."""
        setup_logging()
        self.config = SDKConfig()
        self.metrics = WorkerMetrics()
        self.health_probe = HealthProbeServer(self.config.health_probe)
        self.shutdown_handler = GracefulShutdownHandler(
            self.config.worker.graceful_shutdown_timeout
        )

        self.client: Client | None = None
        self.worker: Worker | None = None
        self._activities: list[Any] = []
        self._workflows: list[Type[Any]] = []

    def register_activities(self, *activities: Any) -> None:
        """Register activities with the worker.
        
        Args:
            *activities: Activity functions or classes to register.
        """
        self._activities.extend(activities)
        logger.info(
            "Activities registered",
            extra={"count": len(activities)},
        )

    def register_workflows(self, *workflows: Type[Any]) -> None:
        """Register workflows with the worker.
        
        Args:
            *workflows: Workflow classes to register.
        """
        self._workflows.extend(workflows)
        logger.info(
            "Workflows registered",
            extra={"count": len(workflows)},
        )

    async def _connect_to_temporal(self) -> None:
        """Connect to Temporal server."""
        try:
            self.client = await Client.connect(
                f"{self.config.temporal.host}:{self.config.temporal.port}",
                namespace=self.config.temporal.namespace,
            )
            logger.info(
                "Connected to Temporal server",
                extra={
                    "host": self.config.temporal.host,
                    "port": self.config.temporal.port,
                    "namespace": self.config.temporal.namespace,
                },
            )
            self.metrics.set_connected(True)
            self.health_probe.set_connected(True)
        except Exception as e:
            logger.error(
                "Failed to connect to Temporal server",
                extra={"error": str(e)},
                exc_info=True,
            )
            raise

    async def _initialize_worker(self) -> None:
        """Initialize and start the Temporal worker."""
        if not self.client:
            raise RuntimeError("Client not connected")

        self.worker = Worker(
            self.client,
            task_queue=self.config.worker.task_queue,
            activities=self._activities,
            workflows=self._workflows,
            max_concurrent_activities=self.config.worker.max_concurrent_activities,
            max_concurrent_workflow_tasks=self.config.worker.max_concurrent_workflow_tasks,
        )

        logger.info(
            "Worker initialized",
            extra={
                "task_queue": self.config.worker.task_queue,
                "activities": len(self._activities),
                "workflows": len(self._workflows),
            },
        )

    async def _run_worker(self) -> None:
        """Run the worker."""
        if not self.worker:
            raise RuntimeError("Worker not initialized")

        logger.info("Starting worker")
        await self.worker.run()

    async def start(self) -> None:
        """Start the SDK and worker."""
        try:
            self.shutdown_handler.setup_signal_handlers()
            self.shutdown_handler.register_callback(self._shutdown)

            await self._connect_to_temporal()
            await self._initialize_worker()

            probe_task = asyncio.create_task(self.health_probe.start())
            worker_task = asyncio.create_task(self._run_worker())
            shutdown_task = asyncio.create_task(
                self.shutdown_handler.wait_for_shutdown()
            )

            done, pending = await asyncio.wait(
                [probe_task, worker_task, shutdown_task],
                return_when=asyncio.FIRST_COMPLETED,
            )

            for task in pending:
                task.cancel()

            logger.info("SDK shutdown complete")

        except Exception as e:
            logger.error(
                "Fatal error in SDK",
                extra={"error": str(e)},
                exc_info=True,
            )
            raise

    async def _shutdown(self) -> None:
        """Gracefully shut down the worker and client."""
        logger.info("Shutting down worker")

        if self.worker:
            await self.worker.shutdown()

        if self.client:
            await self.client.close()

        self.metrics.set_connected(False)
        self.health_probe.set_connected(False)

        logger.info("Shutdown complete")
