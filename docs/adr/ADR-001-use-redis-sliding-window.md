# ADR-001: Use Redis Sliding Window for Rate Limiting

## Status

Accepted

## Context

The API needs to limit the number of requests a client can make within a specific time window.

The requirement is to allow a maximum of **5 requests within 60 seconds**.

We need a rate-limiting algorithm that can track request timestamps efficiently and work correctly when requests arrive at different times.

## Decision

We will use the **Sliding Window Log algorithm** with **Redis Sorted Sets (ZSET)**.

Each request is stored in Redis with:

* A unique request ID as the member.
* The request timestamp as the score.

Before processing a new request, requests older than 60 seconds are removed.

The remaining requests are counted. If the count reaches the limit, the API returns HTTP `429 Too Many Requests`.

## Why?

We chose this approach because:

* Redis provides fast in-memory data operations.
* Sorted Sets allow us to store and order requests by timestamp.
* The sliding window provides more accurate rate limiting than a fixed window.
* Redis can handle the request tracking without requiring a database query for every request.

## Consequences

### Positive

* Accurate sliding-window rate limiting.
* Fast request counting.
* Simple integration with FastAPI.
* Redis handles timestamp-based request storage efficiently.

### Negative

* Redis becomes a required dependency for rate limiting.
* The implementation is more complex than a simple fixed-window counter.
* Request state is stored in Redis and must be managed correctly.

## Example

The current configuration allows:

```text
5 requests / 60 seconds
```

If 5 requests already exist within the current 60-second window, the next request receives:

```text
HTTP 429 Too Many Requests
```
