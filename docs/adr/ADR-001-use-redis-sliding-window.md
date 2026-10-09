# ADR-001: Use Redis Sliding Window for Rate Limiting

## Status

Accepted

## Context

The API needs to limit the number of requests a client can make within a specific time window.

The requirement is to allow a maximum of **5 requests per client IP address within 60 seconds**.

We need a rate-limiting algorithm that can track request timestamps efficiently, identify clients, and work correctly when requests arrive at different times.

The implementation must also account for concurrent requests to prevent clients from exceeding the configured limit.

## Decision

We will use the **Sliding Window Log algorithm** with **Redis Sorted Sets (ZSET)**.

### 1. Client Identification

For unauthenticated requests, the client will be identified by its IP address using FastAPI's:

```python
request.client.host