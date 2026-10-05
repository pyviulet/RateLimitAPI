import json
import logging
import time
import uuid
import redis.asyncio as redis

from fastapi import FastAPI, HTTPException
from app.schema import RedisRequest



app = FastAPI()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)

LIMIT = 5

client = redis.Redis(
    host="redis",
    port=6379,
    decode_responses=True,
)


@app.get("/api/data")
async def get_data():
    with open("app/data/data.json", "r") as file:
        data = json.load(file)

    return data



@app.post("/api/redis")
async def redis_test(request: RedisRequest):
    await client.set("username", request.username)

    value = await client.get("username")

    return {"username": value}


@app.post("/api/submit")
async def submit():
    key = "requests.global"

    now = time.time()



    await client.zremrangebyscore(key, 0, now - 60)

    count = await client.zcard(key)

    if count >= LIMIT:
        logger.warning(
            f"Rate limit exceeded |"
            f"request_count={count}/{LIMIT} |"
            f"status_code=429"
        )

        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded",
        )


    request_id = str(uuid.uuid4())

    await client.zadd(key, {request_id: now})

    logger.info(
        f"Request allowed |"
        f"request_id={request_id} |"
        f"request_count={count + 1}/{LIMIT} | "
        f"status_cde=200"
    )

    return {
        "message": "Request allowed ",
        "request_count": count + 1,
    }







