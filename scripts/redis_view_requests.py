import asyncio
from datetime import datetime

import redis.asyncio as  redis


async def main():
    client = redis.Redis(
        host="Localhost",
        port=6379,
        decode_responses=True,
    )

    requests = await client.zrange(
        "requests.global",
        0,
        -1,
        withscores=True
    )

    for request_id, timestamp in requests:
        request_time = datetime.fromtimestamp(timestamp)

        print(
            f"Request ID: {request_id}"
            f" | Timestamp: {request_time}"
        )

    await client.aclose()

asyncio.run(main())