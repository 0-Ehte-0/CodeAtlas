import redis

from config import get_redis_url

redis_client = redis.from_url(get_redis_url(), decode_responses=True)


def test_redis_connection():
    redis_client.set("test", "hello")

    value = redis_client.get("test")

    print(value)


if __name__ == "__main__":
    test_redis_connection()