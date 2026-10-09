# ADR-001: Use Redis Token Bucket for Rate Limiting

## Status

Accepted

## Context

The API needs to limit the number of requests a client can make while allowing a controlled burst of requests and gradually restoring request capacity over time.

The initial requirement is to allow a maximum burst of **5 requests per client IP address**, with tokens refilling at a rate of **5 tokens per 60 seconds**.

We need a rate-limiting algorithm that can track available capacity, identify clients, and work correctly when concurrent requests arrive.

The implementation must also prevent concurrent requests from consuming the same token and exceeding the available capacity.

## Decision

We will use the **Token Bucket algorithm** with Redis.

Redis stores each client's bucket as a hash containing the available tokens and the timestamp of the last update.

A Lua script executes the token calculation and update atomically to handle concurrent requests safely.

### 1. Client Identification

For unauthenticated requests, the client will be identified by its IP address using FastAPI's:

```python
request.client.host