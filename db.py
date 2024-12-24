import redis
import json
import zlib
from dynaconf import Dynaconf
import numpy as np
import logging

# Load settings
settings = Dynaconf(settings_files=["settings.toml"], environments=True)

# Initialize Redis connection
try:
    redis_client = redis.from_url(settings.DATABASE_URL)
    redis_client.ping()
    print("Connected to Redis!")
except redis.ConnectionError as e:
    print(f"Could not connect to Redis: {e}")
    redis_client = None


class NumpyEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle NumPy data types."""

    def default(self, obj):
        if isinstance(obj, np.bool_):
            return bool(obj)
        return super().default(obj)


def compress_data(data):
    """Compress data before saving to Redis."""
    try:
        json_data = json.dumps(data, cls=NumpyEncoder)
        return zlib.compress(json_data.encode("utf-8"))
    except Exception as e:
        print(f"Error compressing data: {e}")
        return None


def decompress_data(compressed_data):
    """Decompress data after retrieving from Redis."""
    try:
        json_data = zlib.decompress(compressed_data).decode("utf-8")
        return json.loads(json_data)
    except Exception as e:
        print(f"Error decompressing data: {e}")
        return None


def save_symbol_data(key, symbol_data):
    """Save or overwrite symbol data in Redis."""
    if not redis_client:
        print("Redis client is not connected.")
        return
    try:
        compressed_data = compress_data(symbol_data)
        if compressed_data:
            redis_client.set(key, compressed_data)
            print(f"Data saved under key: {key}")
        else:
            print(f"Failed to compress data for key: {key}")
    except Exception as e:
        print(f"Error saving data to Redis: {e}")


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)


def save_or_update_symbol_data(key, symbol_data):
    """Save or update symbol data in Redis."""
    if not redis_client:
        logging.error("Redis client is not connected.")
        return
    try:
        # Retrieve existing data
        existing_data = get_symbol_data(key)
        if existing_data and isinstance(existing_data, dict):
            # Update existing data
            existing_data.update(symbol_data)
            data_to_save = existing_data
            logging.debug(f"Existing data for key '{key}' updated with new values.")
        else:
            # Save new data
            data_to_save = symbol_data
            logging.debug(f"New data for key '{key}' will be saved.")

        # Compress and save
        compressed_data = compress_data(data_to_save)
        if compressed_data:
            redis_client.set(key, compressed_data)
            logging.info(f"Data successfully saved or updated under key: {key}")
        else:
            logging.error(f"Failed to compress data for key: {key}")
    except Exception as e:
        logging.error(f"Error saving or updating data in Redis for key '{key}': {e}")


def get_symbol_data(key):
    """Retrieve symbol data from Redis."""
    if not redis_client:
        print("Redis client is not connected.")
        return None
    try:
        compressed_data = redis_client.get(key)
        if compressed_data:
            return decompress_data(compressed_data)
        print(f"No data found for key: {key}")
        return None
    except Exception as e:
        print(f"Error retrieving data from Redis: {e}")
        return None


def update_symbol_data(key, new_data):
    """Update existing symbol data in Redis."""
    if not redis_client:
        print("Redis client is not connected.")
        return
    try:
        existing_data = get_symbol_data(key)
        if existing_data:
            if isinstance(existing_data, dict):
                existing_data.update(new_data)
                save_symbol_data(key, existing_data)
                print(f"Data updated for key: {key}")
            else:
                print(f"Existing data for key: {key} is not a dictionary. Skipping update.")
        else:
            print(f"No existing data for key: {key}. Saving as new data.")
            save_symbol_data(key, new_data)
    except Exception as e:
        print(f"Error updating data in Redis: {e}")


def delete_symbol_data(key):
    """Delete data from Redis."""
    if not redis_client:
        print("Redis client is not connected.")
        return
    try:
        result = redis_client.delete(key)
        if result:
            print(f"Key '{key}' deleted successfully.")
        else:
            print(f"Key '{key}' does not exist.")
    except Exception as e:
        print(f"Error deleting data from Redis: {e}")


def save_or_update_start_trade(value):
    """Save or update the 'start_trade' flag in Redis."""
    if not redis_client:
        print("Redis client is not connected.")
        return
    try:
        compressed_data = compress_data(value)
        if compressed_data:
            redis_client.set("start_trade", compressed_data)
            print(f"Start trade set to {value}")
        else:
            print("Failed to compress start_trade data.")
    except Exception as e:
        print(f"Error saving or updating start_trade: {e}")


def get_start_trade():
    """Retrieve the 'start_trade' flag from Redis."""
    if not redis_client:
        print("Redis client is not connected.")
        return None
    try:
        compressed_data = redis_client.get("start_trade")
        if compressed_data:
            return decompress_data(compressed_data)
        print("No start_trade data found.")
        return None
    except Exception as e:
        print(f"Error retrieving start_trade: {e}")
        return None


def clear_all_keys():
    """Clear all keys in Redis."""
    if not redis_client:
        print("Redis client is not connected.")
        return
    try:
        redis_client.flushdb()
        print("All keys cleared from Redis.")
    except Exception as e:
        print(f"Error clearing all keys from Redis: {e}")
