#!/usr/bin/env python3
"""
Migration Script: Local Redis to Google Cloud Memorystore

This script helps migrate the application from local Redis to Google Cloud Memorystore.
It provides utilities to test the migration and verify connectivity.
"""

import os
import sys
import logging
import argparse
from typing import Dict, Any, Optional
import redis
from google.cloud import redis_v1
from google.api_core import exceptions as gcp_exceptions

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.config import settings
from app.core.memorystore import memorystore_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MemorystoreMigration:
    """Handles migration from local Redis to Google Cloud Memorystore."""
    
    def __init__(self):
        self.local_redis = None
        self.memorystore_redis = None
    
    def test_local_redis(self) -> bool:
        """Test connection to local Redis."""
        try:
            local_url = "redis://localhost:6379/0"
            self.local_redis = redis.from_url(local_url, decode_responses=False)
            self.local_redis.ping()
            logger.info("✅ Local Redis connection successful")
            return True
        except Exception as e:
            logger.error(f"❌ Local Redis connection failed: {e}")
            return False
    
    def test_memorystore_connection(self) -> bool:
        """Test connection to Google Cloud Memorystore."""
        try:
            # Test if we can get instance info
            instance_info = memorystore_config.get_instance_info()
            if not instance_info:
                logger.error("❌ Could not retrieve Memorystore instance info")
                return False
            
            # Test Redis connection
            self.memorystore_redis = memorystore_config.get_redis_client()
            if not self.memorystore_redis:
                logger.error("❌ Could not connect to Memorystore Redis")
                return False
            
            self.memorystore_redis.ping()
            logger.info("✅ Memorystore Redis connection successful")
            logger.info(f"   Instance: {instance_info['host']}:{instance_info['port']}")
            logger.info(f"   Memory: {instance_info['memory_size_gb']}GB")
            logger.info(f"   Version: {instance_info['redis_version']}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Memorystore connection failed: {e}")
            return False
    
    def migrate_data(self, dry_run: bool = True) -> bool:
        """Migrate data from local Redis to Memorystore."""
        if not self.local_redis or not self.memorystore_redis:
            logger.error("❌ Both local and Memorystore connections required")
            return False
        
        try:
            # Get all keys from local Redis
            local_keys = self.local_redis.keys('*')
            logger.info(f"Found {len(local_keys)} keys in local Redis")
            
            if dry_run:
                logger.info("🔍 DRY RUN - Would migrate the following keys:")
                for key in local_keys[:10]:  # Show first 10 keys
                    ttl = self.local_redis.ttl(key)
                    logger.info(f"   {key} (TTL: {ttl}s)")
                if len(local_keys) > 10:
                    logger.info(f"   ... and {len(local_keys) - 10} more keys")
                return True
            
            # Actually migrate the data
            migrated_count = 0
            for key in local_keys:
                try:
                    # Get value and TTL
                    value = self.local_redis.dump(key)
                    ttl = self.local_redis.ttl(key)
                    
                    # Restore to Memorystore
                    self.memorystore_redis.restore(key, ttl * 1000 if ttl > 0 else 0, value)
                    migrated_count += 1
                    
                except Exception as e:
                    logger.warning(f"Failed to migrate key {key}: {e}")
            
            logger.info(f"✅ Successfully migrated {migrated_count} keys to Memorystore")
            return True
            
        except Exception as e:
            logger.error(f"❌ Data migration failed: {e}")
            return False
    
    def test_celery_configuration(self) -> bool:
        """Test Celery configuration with Memorystore."""
        try:
            from app.workers.celery_app import celery_app
            
            # Test broker connection
            broker_url = settings.get_celery_broker_url()
            logger.info(f"Celery broker URL: {broker_url}")
            
            # Test result backend connection
            result_backend_url = settings.get_celery_result_backend_url()
            logger.info(f"Celery result backend URL: {result_backend_url}")
            
            # Test Celery connection
            celery_app.broker_connection().ensure_connection(max_retries=1)
            logger.info("✅ Celery broker connection successful")
            
            # Test result backend
            celery_app.backend.ensure_connection(max_retries=1)
            logger.info("✅ Celery result backend connection successful")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Celery configuration test failed: {e}")
            return False
    
    def run_migration_test(self, dry_run: bool = True) -> bool:
        """Run complete migration test."""
        logger.info("🚀 Starting Memorystore migration test")
        logger.info("=" * 50)
        
        # Test local Redis
        local_ok = self.test_local_redis()
        
        # Test Memorystore
        memorystore_ok = self.test_memorystore_connection()
        
        # Test Celery configuration
        celery_ok = self.test_celery_configuration()
        
        # Migrate data if both connections work
        migration_ok = False
        if local_ok and memorystore_ok:
            migration_ok = self.migrate_data(dry_run=dry_run)
        
        # Summary
        logger.info("=" * 50)
        logger.info("📊 Migration Test Results:")
        logger.info(f"   Local Redis: {'✅' if local_ok else '❌'}")
        logger.info(f"   Memorystore: {'✅' if memorystore_ok else '❌'}")
        logger.info(f"   Celery Config: {'✅' if celery_ok else '❌'}")
        logger.info(f"   Data Migration: {'✅' if migration_ok else '❌'}")
        
        return all([local_ok, memorystore_ok, celery_ok, migration_ok])

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Migrate from local Redis to Google Cloud Memorystore")
    parser.add_argument("--dry-run", action="store_true", default=True,
                       help="Run in dry-run mode (default: True)")
    parser.add_argument("--migrate", action="store_true", default=False,
                       help="Actually perform the migration (overrides dry-run)")
    parser.add_argument("--test-only", action="store_true", default=False,
                       help="Only test connections, don't migrate data")
    
    args = parser.parse_args()
    
    # Determine if this is a dry run
    dry_run = args.dry_run and not args.migrate
    
    if args.migrate:
        logger.warning("⚠️  MIGRATION MODE - This will actually migrate data!")
        response = input("Are you sure you want to proceed? (yes/no): ")
        if response.lower() != 'yes':
            logger.info("Migration cancelled")
            return
    
    migration = MemorystoreMigration()
    
    if args.test_only:
        # Only test connections
        local_ok = migration.test_local_redis()
        memorystore_ok = migration.test_memorystore_connection()
        celery_ok = migration.test_celery_configuration()
        
        success = all([local_ok, memorystore_ok, celery_ok])
    else:
        # Full migration test
        success = migration.run_migration_test(dry_run=dry_run)
    
    if success:
        logger.info("🎉 Migration test completed successfully!")
        sys.exit(0)
    else:
        logger.error("💥 Migration test failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
