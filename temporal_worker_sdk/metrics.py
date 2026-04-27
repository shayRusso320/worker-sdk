"""Prometheus metrics for worker activity."""

from prometheus_client import Counter, Histogram, Gauge
import time


class WorkerMetrics:
    """Metrics for Temporal worker activity."""

    def __init__(self) -> None:
        """Initialize worker metrics."""
        self.tasks_started = Counter(
            "temporal_tasks_started_total",
            "Total number of tasks started",
            ["task_type"],
        )
        self.tasks_completed = Counter(
            "temporal_tasks_completed_total",
            "Total number of tasks completed successfully",
            ["task_type"],
        )
        self.tasks_failed = Counter(
            "temporal_tasks_failed_total",
            "Total number of tasks that failed",
            ["task_type"],
        )
        self.task_duration = Histogram(
            "temporal_task_duration_seconds",
            "Task execution duration in seconds",
            ["task_type"],
        )
        self.worker_connected = Gauge(
            "temporal_worker_connected",
            "Whether the worker is connected to Temporal (1=connected, 0=disconnected)",
        )

    def record_task_started(self, task_type: str) -> None:
        """Record that a task has started.
        
        Args:
            task_type: The type of task.
        """
        self.tasks_started.labels(task_type=task_type).inc()

    def record_task_completed(self, task_type: str, duration: float) -> None:
        """Record that a task completed successfully.
        
        Args:
            task_type: The type of task.
            duration: Task execution duration in seconds.
        """
        self.tasks_completed.labels(task_type=task_type).inc()
        self.task_duration.labels(task_type=task_type).observe(duration)

    def record_task_failed(self, task_type: str) -> None:
        """Record that a task failed.
        
        Args:
            task_type: The type of task.
        """
        self.tasks_failed.labels(task_type=task_type).inc()

    def set_connected(self, connected: bool) -> None:
        """Set worker connection status.
        
        Args:
            connected: Whether the worker is connected.
        """
        self.worker_connected.set(1 if connected else 0)
