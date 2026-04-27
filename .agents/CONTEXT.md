# Worker SDK — Problem Description

## Context

We are building an internal Python SDK that wraps the official `temporalio` SDK.

The problem it solves: every team that wants to run a Temporal worker has to write the same
boilerplate — connecting to Temporal, reading config from environment, handling graceful shutdown,
setting up logging, exposing health probes for Kubernetes, and exporting metrics. Each team solves
this independently, inconsistently, and often incompletely.

The SDK centralizes all of that. A developer using it only writes their business logic and calls
`sdk.start()`. Everything else is handled automatically.

---

## What the SDK Must Provide

### Configuration
All configuration is read from environment variables. No config is passed in code. The SDK reads
what it needs at startup and raises clearly if a required variable is missing.

### Temporal Worker Bootstrap
The SDK handles connecting to the Temporal server, initializing the worker, and registering
activities and workflows that the developer has provided. The developer does not interact with the
Temporal client directly.

### Graceful Shutdown
When the process receives a termination signal, the SDK stops accepting new tasks, waits for
any in-flight work to finish within a configurable timeout, then exits cleanly.

### Health Probes
The SDK exposes HTTP endpoints for Kubernetes liveness and readiness probes automatically —
without the developer writing any probe-related code. Readiness must reflect whether the worker
has actually connected to Temporal and started polling, not just that the process is alive.

The key requirement: if a team upgrades the SDK version, their worker gets health probes with
zero code changes on their side. Probes must be entirely internal to the SDK.

### Structured Logging
The SDK sets up structured JSON logging and uses it for all internal events. Developers do not
configure logging themselves.

### Metrics
The SDK exports Prometheus metrics about worker activity — how many tasks started, completed,
failed, and how long they took. This happens automatically without the developer adding any
instrumentation.

---

## What the Developer Writes

Only their business logic and a call to `sdk.start()`. The SDK's public API should be minimal
and intuitive. Design it however makes sense — the goal is that the barrier to running a
production-grade Temporal worker is as low as possible.