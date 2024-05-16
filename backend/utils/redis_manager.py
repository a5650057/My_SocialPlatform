import redis
import argparse

class RedisManager:
    def __init__(self):
        self.redis_client = None
        self.initialize_redis()

    def initialize_redis(self):
        # 解析命令行參數
        parser = argparse.ArgumentParser()
        parser.add_argument('--dev', action='store_true', help='use development settings')
        args, unknown = parser.parse_known_args()

        try:
            if args.dev:
                self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
            else:
                self.redis_client = redis.Redis(host='redis', port=6379, db=0)

            self.redis_client.ping()
            print("Connected to Redis")
        except redis.exceptions.ConnectionError:
            print("Unable to connect to Redis, falling back to database")
            self.redis_client = None

    def get_client(self):
        return self.redis_client

redis_manager = RedisManager()  # 创建 RedisManager 实例
