import redis

class RedisManager:
    def __init__(self):
        self.redis_client = None
        self.initialize_redis()

    def initialize_redis(self):
        try:
            self.redis_client = redis.Redis(host='redis', port=6379, db=0)
           
            # self.redis_client = redis.Redis(host=os.getenv('REDIS_HOST', 'localhost'), port=os.getenv('REDIS_PORT', 6379), db=0)
            self.redis_client.ping()
            print("Connected to Redis")
        except redis.exceptions.ConnectionError:
            print("Unable to connect to Redis, falling back to database")
            self.redis_client = None

    def get_client(self):
        return self.redis_client

redis_manager = RedisManager()  # 创建 RedisManager 实例
