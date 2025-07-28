#!/usr/bin/env python3
"""
MongoDB Index Creation Script
Creates optimized indexes for better query performance
"""

import asyncio
import logging
import os
from motor.motor_asyncio import AsyncIOMotorClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_indexes():
    """Create optimized indexes for the database."""
    try:
        # Connect to MongoDB
        mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017/buzz2remote")
        client = AsyncIOMotorClient(mongo_url)
        db = client.get_default_database()
        
        logger.info("🔍 Checking and creating MongoDB indexes...")
        
        # Jobs collection indexes
        jobs_collection = db.jobs
        
        # Get existing indexes
        existing_indexes = await jobs_collection.list_indexes().to_list(None)
        existing_index_names = [idx['name'] for idx in existing_indexes]
        
        logger.info(f"📊 Existing indexes: {existing_index_names}")
        
        # Create indexes only if they don't exist
        indexes_to_create = [
            # Text search index
            {
                "name": "text_search",
                "keys": [("title", "text"), ("company", "text"), ("description", "text")],
                "options": {}
            },
            # Single field indexes
            {"name": "posted_date_desc", "keys": [("posted_date", -1)], "options": {}},
            {"name": "is_active", "keys": [("is_active", 1)], "options": {}},
            {"name": "location", "keys": [("location", 1)], "options": {}},
            {"name": "company", "keys": [("company", 1)], "options": {}},
            {"name": "isRemote", "keys": [("isRemote", 1)], "options": {}},
            # Compound indexes
            {
                "name": "active_jobs_by_date",
                "keys": [("is_active", 1), ("posted_date", -1)],
                "options": {}
            },
            {
                "name": "location_remote_date",
                "keys": [("location", 1), ("isRemote", 1), ("posted_date", -1)],
                "options": {}
            },
            {
                "name": "company_date",
                "keys": [("company", 1), ("posted_date", -1)],
                "options": {}
            },
            {
                "name": "active_location_date",
                "keys": [("is_active", 1), ("location", 1), ("posted_date", -1)],
                "options": {}
            }
        ]
        
        created_count = 0
        for index_config in indexes_to_create:
            if index_config["name"] not in existing_index_names:
                try:
                    await jobs_collection.create_index(
                        index_config["keys"],
                        name=index_config["name"],
                        **index_config["options"]
                    )
                    logger.info(f"✅ Created index: {index_config['name']}")
                    created_count += 1
                except Exception as e:
                    logger.warning(f"⚠️ Could not create index {index_config['name']}: {e}")
            else:
                logger.info(f"⏭️ Index already exists: {index_config['name']}")
        
        logger.info(f"🎯 Created {created_count} new indexes for jobs collection")
        
        # Companies collection indexes
        companies_collection = db.companies
        companies_indexes = await companies_collection.list_indexes().to_list(None)
        companies_index_names = [idx['name'] for idx in companies_indexes]
        
        company_indexes_to_create = [
            {"name": "company_name", "keys": [("name", 1)], "options": {}},
            {"name": "company_active", "keys": [("is_active", 1)], "options": {}}
        ]
        
        for index_config in company_indexes_to_create:
            if index_config["name"] not in companies_index_names:
                try:
                    await companies_collection.create_index(
                        index_config["keys"],
                        name=index_config["name"],
                        **index_config["options"]
                    )
                    logger.info(f"✅ Created company index: {index_config['name']}")
                except Exception as e:
                    logger.warning(f"⚠️ Could not create company index {index_config['name']}: {e}")
        
        # Users collection indexes
        users_collection = db.users
        users_indexes = await users_collection.list_indexes().to_list(None)
        users_index_names = [idx['name'] for idx in users_indexes]
        
        user_indexes_to_create = [
            {"name": "user_email_unique", "keys": [("email", 1)], "options": {"unique": True}},
            {"name": "user_active", "keys": [("is_active", 1)], "options": {}}
        ]
        
        for index_config in user_indexes_to_create:
            if index_config["name"] not in users_index_names:
                try:
                    await users_collection.create_index(
                        index_config["keys"],
                        name=index_config["name"],
                        **index_config["options"]
                    )
                    logger.info(f"✅ Created user index: {index_config['name']}")
                except Exception as e:
                    logger.warning(f"⚠️ Could not create user index {index_config['name']}: {e}")
        
        logger.info("🎯 Index creation completed!")
        
        # List all indexes for verification
        logger.info("\n📊 Final index summary:")
        for collection_name in ["jobs", "companies", "users"]:
            collection = db[collection_name]
            indexes = await collection.list_indexes().to_list(None)
            logger.info(f"  {collection_name}: {[idx['name'] for idx in indexes]}")
            
        client.close()
            
    except Exception as e:
        logger.error(f"❌ Error creating indexes: {e}")
        raise

async def analyze_index_usage():
    """Analyze index usage for optimization."""
    try:
        # Connect to MongoDB
        mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017/buzz2remote")
        client = AsyncIOMotorClient(mongo_url)
        db = client.get_default_database()
        
        logger.info("📊 Analyzing index usage...")
        
        # Get index usage statistics
        for collection_name in ["jobs", "companies", "users"]:
            collection = db[collection_name]
            
            # Get collection stats
            stats = await db.command("collStats", collection_name)
            logger.info(f"\n📈 {collection_name} collection stats:")
            logger.info(f"  Documents: {stats.get('count', 0):,}")
            logger.info(f"  Size: {stats.get('size', 0) / 1024 / 1024:.2f} MB")
            logger.info(f"  Indexes: {stats.get('nindexes', 0)}")
            
        client.close()
            
    except Exception as e:
        logger.error(f"❌ Error analyzing index usage: {e}")

if __name__ == "__main__":
    async def main():
        await create_indexes()
        await analyze_index_usage()
        
    asyncio.run(main()) 