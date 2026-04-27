"""Example of distributed workers with multiple task queues.

This example shows how to:
1. Create separate worker deployments for different task types
2. Route activities to specific task queues from workflows
3. Scale workers independently
"""

import asyncio
import logging
from datetime import timedelta
from dotenv import load_dotenv
from temporalio import workflow, activity

from temporal_worker_sdk import TemporalSDK

logger = logging.getLogger(__name__)


# Email activities
@activity.defn
async def send_email(user_id: str, subject: str) -> None:
    """Send an email to a user.
    
    Args:
        user_id: The user ID.
        subject: Email subject.
    """
    logger.info("Email sent", extra={"user_id": user_id, "subject": subject})


# Payment activities
@activity.defn
async def process_payment(user_id: str, amount: float) -> None:
    """Process a payment for a user.
    
    Args:
        user_id: The user ID.
        amount: Payment amount.
    """
    logger.info("Payment processed", extra={"user_id": user_id, "amount": amount})


# Orchestration workflow
@workflow.defn
class OrderWorkflow:
    """Workflow that orchestrates order processing."""

    @workflow.run
    async def run(self, user_id: str, amount: float) -> None:
        """Execute the order workflow.
        
        Args:
            user_id: The user ID.
            amount: Order amount.
        """
        # Route to payment task queue
        await workflow.execute_activity(
            process_payment,
            user_id,
            amount,
            start_to_close_timeout=timedelta(seconds=60),
            task_queue="payment-tasks",
        )

        # Route to email task queue
        await workflow.execute_activity(
            send_email,
            user_id,
            "Order Confirmation",
            start_to_close_timeout=timedelta(seconds=30),
            task_queue="email-tasks",
        )


async def email_worker() -> None:
    """Start the email worker."""
    load_dotenv()
    sdk = TemporalSDK()
    sdk.register_activities(send_email)
    await sdk.start()


async def payment_worker() -> None:
    """Start the payment worker."""
    load_dotenv()
    sdk = TemporalSDK()
    sdk.register_activities(process_payment)
    await sdk.start()


async def orchestrator_worker() -> None:
    """Start the orchestrator worker."""
    load_dotenv()
    sdk = TemporalSDK()
    sdk.register_workflows(OrderWorkflow)
    await sdk.start()


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python distributed_workers.py [email|payment|orchestrator]")
        sys.exit(1)

    worker_type = sys.argv[1]

    if worker_type == "email":
        asyncio.run(email_worker())
    elif worker_type == "payment":
        asyncio.run(payment_worker())
    elif worker_type == "orchestrator":
        asyncio.run(orchestrator_worker())
    else:
        print(f"Unknown worker type: {worker_type}")
        sys.exit(1)
