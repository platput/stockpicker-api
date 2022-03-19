import redis


class RedisManager:
    def __init__(self):
        self.client = redis.Redis(host='localhost', port=6379, db=0)
