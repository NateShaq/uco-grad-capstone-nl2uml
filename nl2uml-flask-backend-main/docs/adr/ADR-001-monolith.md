
# ADR-001: Monolith Flask + Docker (vs AWS Lambda/CDK)

**Status:** Accepted  
**Date:** 2025-11-01

## Context
Original design used AWS CDK + Lambdas (Python) + DynamoDB + S3 + OpenAI/Gronk. Graduate project requires a self-contained, zero-cost deployment on a college server with no VPN/AWS access.

## Decision
Replatform to a **monolithic Flask app** packaged in a **Docker** image, using **SQLite** and local filesystem for persistence and a **free local LLM** (or echo agent) via a strategy interface.

## Rationale
- Offline, zero-cost operation for classrooms
- Simple ops: one container, one process, one volume
- Easier to teach and contribute to than serverless/microservices
- Still extensible (swap DB/agent later via env vars)

## Consequences
- No serverless autoscaling; acceptable for classroom scale
- Replace AWS-managed services with local equivalents
- Clearer local dev/debug loop; fewer external dependencies
