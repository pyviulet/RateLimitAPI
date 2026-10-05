import redis.asyncio as redis
import asyncio


LIMIT = 5

async def main():
    client = redis.Redis(
        host="Localhost",
        port=6379,
        decode_responses=True,
    )

    key = "requests:viulet"

    count = await client.incr(key)

    if count == 1:
        await client.expire(key, 30)

    if count > LIMIT:
        print("Rate limit exceeded")
    else:
        print("Request allowed")

    print("Request count", count)

    await client.aclose()

asyncio.run(main())