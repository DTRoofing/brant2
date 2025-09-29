"""
Google Cloud Memorystore Redis Configuration

This module provides configuration and connection management for Google Cloud Memorystore Redis.
It handles both direct Redis connections and Celery broker/backend configuration.
"""

import logging
import os
from typing import Optional, Dict, Any
from google.cloud import redis_v1
from google.api_core import exceptions as gcp_exceptions
import redis
from app.core.config import settings

logger = logging.getLogger(__name__)

class MemorystoreConfig:
    """Configuration manager for Google Cloud Memorystore Redis."""
    
    def __init__(self):
        self.project_id = settings.GOOGLE_CLOUD_PROJECT_ID
        self.region = os.getenv("MEMORYSTORE_REGION", "us-central1")
        self.instance_name = os.getenv("MEMORYSTORE_INSTANCE_NAME", "brant-redis-instance")
        self.redis_client = None
        self._instance_info = None
    
    def get_instance_info(self) -> Optional[Dict[str, Any]]:
        """Get Memorystore Redis instance information."""
        if self._instance_info:
            return self._instance_info
            
        try:
            client = redis_v1.CloudRedisClient()
            instance_path = client.instance_path(self.project_id, self.region, self.instance_name)
            instance = client.get_instance(name=instance_path)
            
            self._instance_info = {
                "host": instance.host,
                "port": instance.port,
                "memory_size_gb": instance.memory_size_gb,
                "redis_version": instance.redis_version,
                "tier": instance.tier.name,
                "authorized_network": instance.authorized_network,
                "auth_enabled": instance.auth_enabled,
                "transit_encryption_mode": instance.transit_encryption_mode.name,
            }
            
            logger.info(f"Retrieved Memorystore instance info: {self.instance_name}")
            return self._instance_info
            
        except gcp_exceptions.NotFound:
            logger.error(f"Memorystore instance {self.instance_name} not found")
            return None
        except Exception as e:
            logger.error(f"Failed to get Memorystore instance info: {e}")
            return None
    
    def get_redis_url(self, database: int = 0) -> str:
        """Get Redis URL for Memorystore instance."""
        instance_info = self.get_instance_info()
        if not instance_info:
            # Fallback to local Redis for development
            logger.warning("Using local Redis fallback")
            return f"redis://localhost:6379/{database}"
        
        host = instance_info["host"]
        port = instance_info["port"]
        return f"redis://{host}:{port}/{database}"
    
    def get_redis_client(self, database: int = 0) -> Optional[redis.Redis]:
        """Get Redis client connected to Memorystore."""
        if self.redis_client:
            return self.redis_client
            
        try:
            redis_url = self.get_redis_url(database)
            self.redis_client = redis.from_url(redis_url, decode_responses=False)
            
            # Test connection
            self.redis_client.ping()
            logger.info(f"Successfully connected to Memorystore Redis: {self.instance_name}")
            return self.redis_client
            
        except Exception as e:
            logger.error(f"Failed to connect to Memorystore Redis: {e}")
            # Fallback to local Redis for development
            try:
                fallback_url = f"redis://localhost:6379/{database}"
                self.redis_client = redis.from_url(fallback_url, decode_responses=False)
                self.redis_client.ping()
                logger.warning("Using local Redis fallback")
                return self.redis_client
            except Exception as fallback_error:
                logger.error(f"Fallback Redis connection also failed: {fallback_error}")
                return None
    
    def get_celery_broker_url(self) -> str:
        """Get Celery broker URL for Memorystore."""
        return self.get_redis_url(0)  # Use database 0 for Celery broker
    
    def get_celery_result_backend_url(self) -> str:
        """Get Celery result backend URL for Memorystore."""
        return self.get_redis_url(1)  # Use database 1 for Celery results
    
    def get_cache_redis_url(self) -> str:
        """Get Redis URL for caching."""
        return self.get_redis_url(2)  # Use database 2 for caching

# Global instance
memorystore_config = MemorystoreConfig()

def get_memorystore_redis_url() -> str:
    """Get the Redis URL for Memorystore (used by config_repository.py)."""
    return memorystore_config.get_cache_redis_url()

def get_memorystore_celery_broker_url() -> str:
    """Get the Celery broker URL for Memorystore."""
    return memorystore_config.get_celery_broker_url()

def get_memorystore_celery_result_backend_url() -> str:
    """Get the Celery result backend URL for Memorystore."""
    return memorystore_config.get_celery_result_backend_url()
