from prometheus_client import Counter


rate_limit_rejections_total = Counter(
    "rate_limit_rejections_total",
    "Total number of requests rejected by the rate limiter.",
)

