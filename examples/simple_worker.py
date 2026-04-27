"""Simple example worker using the Temporal SDK.

This example shows how to:
1. Define workflows and activities
2. Create a worker using the SDK
3. Run it with automatic configuration, logging, and health probes
"""

import asyncio
import logging
from datetime import timedelta
from dotenv import load_dotenv
from temporalio import workflow, activity

from temporal_worker_sdk import TemporalSDK

logger = logging.getLogger(__name__)


@activity.defn
async def greet(name: str) -> str:
    """Simple activity that greets someone.
    
    Args:
        name: The name to greet.
        
    Returns:
        A greeting message.
    """
    greeting = f"Hello, {name}!"
    logger.info("Greeting generated", extra={"name": name, "greeting": greeting})
    return greeting


@workflow.defn
class GreetingWorkflow:
    """Simple workflow that greets someone."""

    @workflow.run
    async def run(self, name: str) -> str:
        """Execute the greeting workflow.
        
        Args:
            name: The name to greet.
            
        Returns:
            The greeting message.
        """
        return await workflow.execute_activity(
            greet,
            name,
            start_to_close_timeout=timedelta(seconds=60),
        )


async def main() -> None:
    """Start the worker."""
    load_dotenv()
    sdk = TemporalSDK()
    sdk.register_activities(greet)
    sdk.register_workflows(GreetingWorkflow)
    await sdk.start()


if __name__ == "__main__":
    asyncio.run(main())
