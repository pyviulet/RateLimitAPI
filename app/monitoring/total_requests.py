from prometheus_client import Counter


rate_limit_requests_total = Counter(
    "rate_limit_requests_total",
    "Total requests processed by the rate limiter.",
)
