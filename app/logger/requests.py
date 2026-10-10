from app.logger.config import logger


def log_request_allowed(
    client_ip: str,
    route: str,
    tokens_remaining: float | None,
) -> None:
    logger.info(
        "event=request_allowed "
        "client_ip=%s route=%s tokens_remaining=%s",
        client_ip,
        route,
        tokens_remaining,
    )


def log_request_rejected(
    client_ip: str,
    route: str,
) -> None:
    logger.warning(
        "event=rate_limit_exceeded "
        "client_ip=%s route=%s",
        client_ip,
        route,
    )

