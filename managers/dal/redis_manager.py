import redis


class RedisManager:
    _instance = None
    redis_client = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            return cls._instance

    def get_redis_connector(self):
        if self.redis_client is None:
            self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        return self.redis_client
