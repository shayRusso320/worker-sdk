# Temporal Worker SDK

Production-grade Python SDK that wraps the official `temporalio` SDK to eliminate boilerplate when running Temporal workers.

## Problem

Every team running a Temporal worker has to write the same boilerplate:
- Connect to Temporal server
- Read config from environment
- Handle graceful shutdown
- Set up structured logging
- Expose health probes for Kubernetes
- Export Prometheus metrics

This SDK centralizes all of that. Developers only write their business logic.

## Installation

```bash
pip install temporal-worker-sdk
```

## Quick Start

Define your workflows and activities:

```python
# workflows.py
from temporalio import workflow, activity
from datetime import timedelta

@activity.defn
async def process_payment(order_id: str) -> None:
    """Process a payment for an order."""
    print(f"Processing payment for order {order_id}")

@workflow.defn
class PaymentWorkflow:
    @workflow.run
    async def run(self, order_id: str) -> None:
        await workflow.execute_activity(
            process_payment,
            order_id,
            start_to_close_timeout=timedelta(seconds=60),
        )
```

Start the worker:

```python
# main.py
import asyncio
from dotenv import load_dotenv
from temporal_worker_sdk import TemporalSDK
from workflows import process_payment, PaymentWorkflow

async def main():
    load_dotenv()  # Load .env for local dev
    sdk = TemporalSDK()
    sdk.register_activities(process_payment)
    sdk.register_workflows(PaymentWorkflow)
    await sdk.start()

if __name__ == "__main__":
    asyncio.run(main())
```

That's it. The SDK handles:
- ✅ Connecting to Temporal
- ✅ Reading config from environment variables
- ✅ Graceful shutdown on signals
- ✅ Structured JSON logging
- ✅ Kubernetes health probes (liveness + readiness)
- ✅ Prometheus metrics at `/metrics`

## Configuration

All configuration comes from environment variables. No code changes needed for different environments.

### Required

- `WORKER_TASK_QUEUE` — Task queue name for this worker

### Optional

- `TEMPORAL_HOST` — Temporal server host (default: `localhost`)
- `TEMPORAL_PORT` — Temporal server port (default: `7233`)
- `TEMPORAL_NAMESPACE` — Temporal namespace (default: `default`)
- `WORKER_MAX_CONCURRENT_ACTIVITIES` — Max concurrent activities (default: `100`)
- `WORKER_MAX_CONCURRENT_WORKFLOW_TASKS` — Max concurrent workflow tasks (default: `40`)
- `WORKER_GRACEFUL_SHUTDOWN_TIMEOUT` — Graceful shutdown timeout in seconds (default: `30`)
- `HEALTH_PROBE_HOST` — Health probe server host (default: `0.0.0.0`)
- `HEALTH_PROBE_PORT` — Health probe server port (default: `8080`)
- `HEALTH_PROBE_ENABLED` — Enable health probe server (default: `true`)

### Example .env

```env
TEMPORAL_HOST=localhost
TEMPORAL_PORT=7233
TEMPORAL_NAMESPACE=temporal
WORKER_TASK_QUEUE=default
WORKER_MAX_CONCURRENT_ACTIVITIES=100
WORKER_MAX_CONCURRENT_WORKFLOW_TASKS=40
WORKER_GRACEFUL_SHUTDOWN_TIMEOUT=30
HEALTH_PROBE_HOST=0.0.0.0
HEALTH_PROBE_PORT=8080
HEALTH_PROBE_ENABLED=true
```

## Health Probes

The SDK automatically exposes HTTP endpoints for Kubernetes:

- `GET /health/live` — Liveness probe (process is alive)
- `GET /health/ready` — Readiness probe (worker is connected and ready)
- `GET /metrics` — Prometheus metrics

Use in your Kubernetes deployment:

```yaml
livenessProbe:
  httpGet:
    path: /health/live
    port: 8080
  initialDelaySeconds: 10
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /health/ready
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 5
```

## Metrics

The SDK exports Prometheus metrics about worker activity:

- `temporal_tasks_started_total` — Total tasks started
- `temporal_tasks_completed_total` — Total tasks completed
- `temporal_tasks_failed_total` — Total tasks failed
- `temporal_task_duration_seconds` — Task execution duration
- `temporal_worker_connected` — Worker connection status (1=connected, 0=disconnected)

Scrape with a Kubernetes ServiceMonitor:

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: temporal-worker
spec:
  selector:
    matchLabels:
      app: temporal-worker
  endpoints:
    - port: metrics
      interval: 30s
      path: /metrics
```

## Logging

The SDK uses structured JSON logging. All logs include:
- `timestamp` — ISO 8601 timestamp
- `level` — Log level (INFO, WARNING, ERROR, etc.)
- `logger` — Logger name (module)
- `message` — Log message
- `extra` — Additional context fields

Example log:

```json
{
  "timestamp": "2026-04-27 18:10:37,235",
  "level": "INFO",
  "logger": "workflows",
  "message": "Processing task",
  "extra": {"order_id": "12345"}
}
```

## Distributed Workers

For multiple worker types, use separate deployments with different task queues:

```python
# email-worker/main.py
sdk = TemporalSDK()
sdk.register_activities(send_email, send_sms)
await sdk.start()

# payment-worker/main.py
sdk = TemporalSDK()
sdk.register_activities(process_payment, refund_payment)
await sdk.start()
```

In your workflow, route activities to specific task queues:

```python
@workflow.defn
class OrderWorkflow:
    @workflow.run
    async def run(self, order_id: str) -> None:
        # Route to email task queue
        await workflow.execute_activity(
            send_email,
            order_id,
            task_queue="email-tasks"
        )
        
        # Route to payment task queue
        await workflow.execute_activity(
            process_payment,
            order_id,
            task_queue="payment-tasks"
        )
```

## Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: temporal-worker
spec:
  replicas: 3
  selector:
    matchLabels:
      app: temporal-worker
  template:
    metadata:
      labels:
        app: temporal-worker
    spec:
      containers:
      - name: worker
        image: your-worker:latest
        env:
        - name: TEMPORAL_HOST
          value: temporal-frontend.temporal.svc.cluster.local
        - name: TEMPORAL_NAMESPACE
          value: temporal
        - name: WORKER_TASK_QUEUE
          value: default
        ports:
        - name: metrics
          containerPort: 8080
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
```

## License

MIT
