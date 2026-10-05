import redis.asyncio as redis
import asyncio


async def main():
    client = redis.Redis(
        host="Localhost",
        port=6379,
        decode_responses=True,
    )

    await client.set("username", "viulet")
    value = await client.get("username")

    print(value)
    await client.aclose()

asyncio.run(main())

