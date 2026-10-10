from app.logger.config import logger


def log_redis_failure(
    client_ip: str,
    route: str,
    error: Exception,
) -> None:
    logger.exception(
        "event=rate_limiter_failure "
        "mode=fail_open "
        "client_ip=%s "
        "route=%s "
        "error=%s",
        client_ip,
        route,
        error,
    )


def log_fail_open(
    client_ip: str,
    route: str,
) -> None:
    logger.warning(
        "event=request_allowed_without_rate_limit "
        "reason=redis_unavailable "
        "client_ip=%s "
        "route=%s",
        client_ip,
        route,
    )
