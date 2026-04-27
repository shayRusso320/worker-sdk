"""Example worker using the Temporal SDK."""

import asyncio
import logging
from dotenv import load_dotenv

from sdk import TemporalSDK
from workflows import process_task, TaskWorkflow


async def main() -> None:
    """Start the Temporal worker using the SDK."""
    load_dotenv()
    sdk = TemporalSDK()
    sdk.register_activities(process_task)
    sdk.register_workflows(TaskWorkflow)
    await sdk.start()


if __name__ == "__main__":
    asyncio.run(main())
