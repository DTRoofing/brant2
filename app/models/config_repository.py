import logging
from typing import Dict, Any
from sqlalchemy.orm import Session
import json
from pathlib import Path
import redis

from app.models.config import CostConfiguration
from app.core.config import settings

logger = logging.getLogger(__name__)

# --- BEST PRACTICE: Centralized Redis Client ---
# In a production application, this client should be initialized once and shared,
# for example, in `app/db/session.py` or a dedicated `app/core/redis.py`.
try:
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=False) # Store bytes
    redis_client.ping()
    logger.info("Successfully connected to Redis for caching.")
except Exception as e:
    logger.error(f"Could not connect to Redis: {e}. Caching will be disabled.")
    redis_client = None

CACHE_TTL_SECONDS = 3600  # 1 hour

def get_cost_configuration(db: Session, key: str = "default") -> Dict[str, Any]:
    """
    Retrieves cost configuration, using Redis as a distributed cache.
    If not in cache, it fetches from the database and then falls back to a JSON file.
    """
    cache_key = f"cost_config:{key}"

    # 1. Try to get from Redis cache
    if redis_client:
        try:
            cached_config = redis_client.get(cache_key)
            if cached_config:
                logger.debug(f"Returning cached cost configuration for key: {key} from Redis.")
                return json.loads(cached_config)
        except Exception as e:
            logger.error(f"Redis GET failed for key {cache_key}: {e}")

    logger.info(f"Fetching cost configuration for key '{key}' from database (cache miss).")
    
    # 2. Fetch from database
    config_record = db.query(CostConfiguration).filter(CostConfiguration.key == key).first()
    
    if config_record:
        logger.info("Found cost configuration in database.")
        config_data = config_record.config_data

        # Verification step (from original code)
        try:
            config_path = Path(__file__).parent.parent / "config" / "cost_config.json"
            with open(config_path, 'r') as f:
                local_config = json.load(f)
            if config_data != local_config:
                logger.critical(
                    "CRITICAL MISMATCH: The 'default' cost configuration in the database "
                    "does not match the local cost_config.json file. The database "
                    "version will be used, but this may indicate an unapplied change. "
                    "Consider running a sync script or updating the database record."
                )
        except Exception as e:
            logger.warning(f"Could not compare DB config with local file for verification: {e}")
    else:
        # 3. Fallback to JSON file
        logger.warning(f"Cost configuration '{key}' not found in database. Falling back to cost_config.json.")
        try:
            config_path = Path(__file__).parent.parent / "config" / "cost_config.json"
            with open(config_path, 'r') as f:
                config_data = json.load(f)
        except Exception as e:
            logger.error(f"Fallback to cost_config.json also failed: {e}. Using empty config.")
            config_data = {}

    # 4. Store the result in Redis cache before returning
    if redis_client and config_data:
        try:
            redis_client.set(cache_key, json.dumps(config_data), ex=CACHE_TTL_SECONDS)
            logger.info(f"Stored cost configuration for key '{key}' in Redis cache.")
        except Exception as e:
            logger.error(f"Redis SET failed for key {cache_key}: {e}")

    return config_data