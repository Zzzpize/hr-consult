import redis
import json
import time
import os

REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = 6379
REDIS_DB = 0
INPUT_FILENAME = 'redis_dump.json'

def load_redis_data():
    """
    Подключается к Redis, очищает его и загружает данные из JSON-файла.
    """
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)
        r.ping()
        print(f"Successfully connected to Redis at {REDIS_HOST}:{REDIS_PORT}")
    except redis.exceptions.ConnectionError:
        print("Waiting for Redis to start...")
        time.sleep(5)
        return load_redis_data()

    try:
        with open(INPUT_FILENAME, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"Successfully loaded data from '{INPUT_FILENAME}'")
    except FileNotFoundError:
        print(f"Error: Dump file '{INPUT_FILENAME}' not found. No data will be loaded.")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{INPUT_FILENAME}'.")
        return

    print("Flushing current Redis database...")
    r.flushdb()

    total_keys = 0
    print("Loading data into Redis...")

    for key, value in data.get('globals', {}).items():
        if isinstance(value, dict):
            r.hset(key, mapping=value)
        else:
            r.set(key, str(value))
        total_keys += 1

    for user_id, user_data in data.get('users', {}).items():
        for sub_key, value in user_data.items():
            full_key = f"user:{user_id}:{sub_key}"
            if sub_key == 'profile':
                r.hset(f"user:{user_id}", mapping=value)
            elif sub_key == 'skills':
                 if value: r.sadd(full_key, *value)
            elif isinstance(value, list):
                if value: r.rpush(full_key, *[json.dumps(item) if isinstance(item, dict) else item for item in value])
            elif isinstance(value, dict):
                r.hset(full_key, mapping=value)
            else:
                if sub_key == 'embedding':
                    r.set(full_key, json.dumps(value))
                else:
                    r.set(full_key, value)
            total_keys += 1

    for offer_id, offer_data in data.get('offers', {}).items():
        r.hset(f"offer:{offer_id}", mapping=offer_data)
        total_keys += 1

    print(f"\nSuccessfully loaded {total_keys} keys into Redis.")

if __name__ == '__main__':
    load_redis_data()