import redis

client = redis.Redis(
    host='Localhost',
    port=6379,
    decode_responses=True,
)

client.set("username", "viulet")
value = client.get("username")
print(value)