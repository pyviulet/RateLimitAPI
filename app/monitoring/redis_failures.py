from prometheus_client import Counter


rate_limit_redis_failures_total = Counter(
    "rate_limit_redis_failures_total",
    "Total number of Redis failures in the rate limiter.",
)

