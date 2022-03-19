import redis


class RedisManager:
    def __init__(self):
        self.client = redis.Redis(host='127.0.0.1', port=6379, db=0)
