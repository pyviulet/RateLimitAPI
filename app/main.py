import json
import logging
import os
import uuid

import redis.asyncio as redis

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.schema import RedisRequest


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)


# Token Bucket configuration
CAPACITY = 5
REFILL_RATE = CAPACITY / 60  # 5 tokens every 60 seconds

RATE_LIMITED_ROUTES = {
    ("POST", "/api/submit"),
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    client = redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=6379,
        decode_responses=True,
    )

    app.state.redis = client

    yield

    await client.aclose()


app = FastAPI(lifespan=lifespan)


# Redis executes this script atomically.
TOKEN_BUCKET_SCRIPT = """
local key = KEYS[1]

local capacity = tonumber(ARGV[1])
local refill_rate = tonumber(ARGV[2])
local cost = tonumber(ARGV[3])

-- Use Redis server time to avoid differences between app server clocks.
local time = redis.call('TIME')
local now = tonumber(time[1]) + tonumber(time[2]) / 1000000

local data = redis.call('HMGET', key, 'tokens', 'timestamp')

local tokens = tonumber(data[1])
local last_timestamp = tonumber(data[2])

-- A new client starts with a full bucket.
if tokens == nil then
    tokens = capacity
end

if last_timestamp == nil then
    last_timestamp = now
end

-- Refill tokens based on elapsed time.
local elapsed = math.max(0, now - last_timestamp)

tokens = math.min(
    capacity,
    tokens + elapsed * refill_rate
)

local allowed = 0

-- Consume a token only if one is available.
if tokens >= cost then
    tokens = tokens - cost
    allowed = 1
end

-- Save the updated bucket.
redis.call(
    'HSET',
    key,
    'tokens', tokens,
    'timestamp', now
)

-- Remove inactive buckets eventually.
local ttl = math.ceil(capacity / refill_rate * 2)
redis.call('EXPIRE', key, ttl)

return {allowed, tostring(tokens)}
"""


@app.middleware("http")
async def rate_limit_middleware(
    request: Request,
    call_next,
):
    route = (request.method, request.url.path)

    # Skip rate limiting for unprotected routes.
    if route not in RATE_LIMITED_ROUTES:
        return await call_next(request)

    client = request.app.state.redis

    client_ip = (
        request.client.host
        if request.client is not None
        else "unknown"
    )

    key = f"rate_limit:token_bucket:{client_ip}"

    try:
        result = await client.eval(
            TOKEN_BUCKET_SCRIPT,
            1,
            key,
            CAPACITY,
            REFILL_RATE,
            1,
        )

    except redis.RedisError:
        logger.exception(
            "event=rate_limiter_failure "
            "mode=fail_open client_ip=%s route=%s",
            client_ip,
            request.url.path,
        )

        # Fail-open: allow the request to continue.
        request.state.tokens_remaining = None

        logger.warning(
            "event=request_allowed_without_rate_limit "
            "reason=redis_unavailable client_ip=%s",
            client_ip,
        )

        return await call_next(request)

    allowed = int(result[0])
    tokens_remaining = float(result[1])

    if not allowed:
        logger.warning(
            "event=rate_limit_exceeded client_ip=%s route=%s",
            client_ip,
            request.url.path,
        )

        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded"},
        )

    request_id = str(uuid.uuid4())
    request.state.tokens_remaining = tokens_remaining

    logger.info(
        "event=request_allowed request_id=%s "
        "client_ip=%s tokens_remaining=%.2f",
        request_id,
        client_ip,
        tokens_remaining,
    )

    return await call_next(request)

@app.get("/api/data")
async def get_data():
    with open("app/data/data.json", "r") as file:
        data = json.load(file)

    return data


@app.post("/api/redis")
async def redis_test(
    request: Request,
    redis_request: RedisRequest,
):
    client = request.app.state.redis

    await client.set("username", redis_request.username)

    value = await client.get("username")

    return {"username": value}


@app.post("/api/submit")
async def submit(request: Request):
    tokens_remaining = request.state.tokens_remaining

    return {
        "message": "Request allowed",
        "tokens_remaining": (
            round(tokens_remaining, 2)
            if tokens_remaining is not None
            else None
        ),
    }