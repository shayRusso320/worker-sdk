"""Temporal workflows and activities."""

from temporalio import workflow, activity
import logging
from datetime import timedelta

logger = logging.getLogger(__name__)


@activity.defn
async def process_task(task_content: str) -> None:
    """Activity that receives a task and logs its contents.
    
    Args:
        task_content: The content of the task to process.
    """
    logger.info("Processing task", extra={"content": task_content})


@workflow.defn
class TaskWorkflow:
    """Workflow that orchestrates task processing."""

    @workflow.run
    async def run(self, task_content: str) -> None:
        """Execute the task processing workflow.
        
        Args:
            task_content: The content of the task to process.
        """
        await workflow.execute_activity(
            process_task,
            task_content,
            start_to_close_timeout=timedelta(seconds=60),
        )
