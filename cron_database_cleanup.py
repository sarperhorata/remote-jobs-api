#!/usr/bin/env python3
"""
Database Cleanup Cronjob
Removes old data and optimizes database performance
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from pymongo import MongoClient
from pymongo.errors import OperationFailure

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseCleanup:
    def __init__(self):
        """Initialize Database Cleanup"""
        self.mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/buzz2remote')
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client.buzz2remote
        
        # Cleanup rules for different collections
        self.cleanup_rules = {
            'jobs': {
                'field': 'created_at',
                'keep_days': 90,        # Keep jobs for 90 days
                'archive_days': 365,    # Archive after 1 year
                'conditions': {'status': {'$in': ['expired', 'filled']}}
            },
            'job_applications': {
                'field': 'created_at',
                'keep_days': 180,       # Keep applications for 6 months
                'archive_days': 730,    # Archive after 2 years
                'conditions': {}
            },
            'user_sessions': {
                'field': 'created_at',
                'keep_days': 7,         # Keep sessions for 1 week
                'archive_days': None,   # Don't archive, just delete
                'conditions': {}
            },
            'api_logs': {
                'field': 'timestamp',
                'keep_days': 30,        # Keep API logs for 30 days
                'archive_days': None,   # Don't archive, just delete
                'conditions': {}
            },
            'crawl_logs': {
                'field': 'timestamp',
                'keep_days': 14,        # Keep crawl logs for 2 weeks
                'archive_days': None,   # Don't archive, just delete
                'conditions': {}
            },
            'error_logs': {
                'field': 'timestamp',
                'keep_days': 60,        # Keep error logs for 2 months
                'archive_days': None,   # Don't archive, just delete
                'conditions': {}
            },
            'email_logs': {
                'field': 'sent_at',
                'keep_days': 30,        # Keep email logs for 30 days
                'archive_days': 365,    # Archive after 1 year
                'conditions': {}
            },
            'notifications': {
                'field': 'created_at',
                'keep_days': 30,        # Keep notifications for 30 days
                'archive_days': None,   # Don't archive, just delete
                'conditions': {'read': True}  # Only cleanup read notifications
            }
        }
    
    def get_collection_stats(self, collection_name):
        """Get collection statistics"""
        try:
            collection = self.db[collection_name]
            
            # Get basic stats
            stats = self.db.command('collStats', collection_name)
            
            # Count total documents
            total_docs = collection.count_documents({})
            
            # Get size information
            size_mb = stats.get('size', 0) / 1024 / 1024
            storage_size_mb = stats.get('storageSize', 0) / 1024 / 1024
            
            # Get index information
            indexes = list(collection.list_indexes())
            
            return {
                'total_documents': total_docs,
                'size_mb': round(size_mb, 2),
                'storage_size_mb': round(storage_size_mb, 2),
                'avg_doc_size': stats.get('avgObjSize', 0),
                'indexes_count': len(indexes),
                'indexes': [idx['name'] for idx in indexes]
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting stats for {collection_name}: {e}")
            return None
    
    def cleanup_collection(self, collection_name, rules):
        """Cleanup a specific collection based on rules"""
        logger.info(f"🧹 Cleaning up collection: {collection_name}")
        
        try:
            collection = self.db[collection_name]
            
            # Get initial stats
            initial_stats = self.get_collection_stats(collection_name)
            if not initial_stats:
                return None
            
            cleanup_result = {
                'collection': collection_name,
                'initial_documents': initial_stats['total_documents'],
                'initial_size_mb': initial_stats['size_mb'],
                'deleted_documents': 0,
                'archived_documents': 0,
                'final_documents': 0,
                'final_size_mb': 0,
                'space_saved_mb': 0
            }
            
            # Calculate cutoff dates
            keep_cutoff = datetime.now() - timedelta(days=rules['keep_days'])
            archive_cutoff = None
            if rules.get('archive_days'):
                archive_cutoff = datetime.now() - timedelta(days=rules['archive_days'])
            
            # Build query for old documents
            query = {rules['field']: {'$lt': keep_cutoff}}
            if rules.get('conditions'):
                query.update(rules['conditions'])
            
            # Count documents to be cleaned
            docs_to_cleanup = collection.count_documents(query)
            
            if docs_to_cleanup == 0:
                logger.info(f"✅ No documents to cleanup in {collection_name}")
                cleanup_result['final_documents'] = initial_stats['total_documents']
                cleanup_result['final_size_mb'] = initial_stats['size_mb']
                return cleanup_result
            
            logger.info(f"📊 Found {docs_to_cleanup} documents to cleanup in {collection_name}")
            
            # Archive old documents if archive_days is specified
            if archive_cutoff:
                archive_query = {rules['field']: {'$lt': archive_cutoff}}
                if rules.get('conditions'):
                    archive_query.update(rules['conditions'])
                
                # Find documents to archive
                docs_to_archive = list(collection.find(archive_query))
                
                if docs_to_archive:
                    # Create archive collection name
                    archive_collection_name = f"{collection_name}_archive"
                    archive_collection = self.db[archive_collection_name]
                    
                    # Insert into archive
                    archive_collection.insert_many(docs_to_archive)
                    cleanup_result['archived_documents'] = len(docs_to_archive)
                    
                    # Delete from original collection
                    delete_result = collection.delete_many(archive_query)
                    logger.info(f"📦 Archived {len(docs_to_archive)} documents from {collection_name}")
            
            # Delete old documents that don't need archiving
            delete_query = query.copy()
            if archive_cutoff:
                # Only delete documents newer than archive cutoff but older than keep cutoff
                delete_query[rules['field']] = {
                    '$gte': archive_cutoff,
                    '$lt': keep_cutoff
                }
            
            delete_result = collection.delete_many(delete_query)
            cleanup_result['deleted_documents'] = delete_result.deleted_count
            
            logger.info(f"🗑️ Deleted {delete_result.deleted_count} documents from {collection_name}")
            
            # Get final stats
            final_stats = self.get_collection_stats(collection_name)
            if final_stats:
                cleanup_result['final_documents'] = final_stats['total_documents']
                cleanup_result['final_size_mb'] = final_stats['size_mb']
                cleanup_result['space_saved_mb'] = round(
                    initial_stats['size_mb'] - final_stats['size_mb'], 2
                )
            
            return cleanup_result
            
        except Exception as e:
            logger.error(f"❌ Error cleaning up {collection_name}: {e}")
            return None
    
    def optimize_indexes(self):
        """Optimize database indexes"""
        logger.info("⚡ Optimizing database indexes")
        
        optimization_results = []
        
        try:
            # Get list of all collections
            collections = self.db.list_collection_names()
            
            for collection_name in collections:
                if collection_name.startswith('system.'):
                    continue  # Skip system collections
                
                try:
                    collection = self.db[collection_name]
                    
                    # Rebuild indexes
                    result = collection.reindex()
                    
                    optimization_results.append({
                        'collection': collection_name,
                        'status': 'success',
                        'message': 'Indexes rebuilt successfully'
                    })
                    
                    logger.info(f"✅ Optimized indexes for {collection_name}")
                    
                except Exception as e:
                    optimization_results.append({
                        'collection': collection_name,
                        'status': 'error',
                        'message': str(e)
                    })
                    logger.error(f"❌ Error optimizing indexes for {collection_name}: {e}")
            
            return optimization_results
            
        except Exception as e:
            logger.error(f"❌ Error during index optimization: {e}")
            return []
    
    def compact_database(self):
        """Compact database to reclaim space"""
        logger.info("📦 Compacting database")
        
        try:
            # Run compact on the database
            result = self.db.command('compact')
            
            logger.info("✅ Database compaction completed")
            return {
                'status': 'success',
                'result': result
            }
            
        except OperationFailure as e:
            # Compact might not be available on all MongoDB configurations
            logger.warning(f"⚠️ Database compaction not available: {e}")
            return {
                'status': 'not_available',
                'result': str(e)
            }
        except Exception as e:
            logger.error(f"❌ Error during database compaction: {e}")
            return {
                'status': 'error',
                'result': str(e)
            }
    
    def analyze_database_health(self):
        """Analyze overall database health"""
        logger.info("🔍 Analyzing database health")
        
        try:
            # Get database stats
            db_stats = self.db.command('dbStats')
            
            # Get server status
            server_status = self.client.admin.command('serverStatus')
            
            # Calculate health metrics
            total_size_gb = db_stats.get('dataSize', 0) / 1024**3
            storage_size_gb = db_stats.get('storageSize', 0) / 1024**3
            index_size_gb = db_stats.get('indexSize', 0) / 1024**3
            
            # Memory usage
            mem_info = server_status.get('mem', {})
            
            # Connection info
            connections = server_status.get('connections', {})
            
            health_report = {
                'database': {
                    'collections': db_stats.get('collections', 0),
                    'objects': db_stats.get('objects', 0),
                    'data_size_gb': round(total_size_gb, 2),
                    'storage_size_gb': round(storage_size_gb, 2),
                    'index_size_gb': round(index_size_gb, 2),
                    'avg_obj_size': db_stats.get('avgObjSize', 0)
                },
                'memory': {
                    'resident_mb': mem_info.get('resident', 0),
                    'virtual_mb': mem_info.get('virtual', 0),
                    'mapped_mb': mem_info.get('mapped', 0)
                },
                'connections': {
                    'current': connections.get('current', 0),
                    'available': connections.get('available', 0),
                    'total_created': connections.get('totalCreated', 0)
                },
                'uptime_hours': round(server_status.get('uptime', 0) / 3600, 2)
            }
            
            # Generate health recommendations
            recommendations = []
            
            if total_size_gb > 5:  # 5GB threshold
                recommendations.append({
                    'priority': 'medium',
                    'message': f"Database size is {total_size_gb:.1f}GB",
                    'action': 'Consider regular cleanup and archiving'
                })
            
            if index_size_gb > total_size_gb * 0.5:  # Indexes > 50% of data
                recommendations.append({
                    'priority': 'medium',
                    'message': f"Index size ({index_size_gb:.1f}GB) is large relative to data",
                    'action': 'Review and optimize indexes'
                })
            
            connection_usage = (connections.get('current', 0) / max(connections.get('available', 1), 1)) * 100
            if connection_usage > 80:
                recommendations.append({
                    'priority': 'high',
                    'message': f"High connection usage: {connection_usage:.1f}%",
                    'action': 'Monitor connection pooling and optimize queries'
                })
            
            health_report['recommendations'] = recommendations
            
            return health_report
            
        except Exception as e:
            logger.error(f"❌ Error analyzing database health: {e}")
            return None
    
    def run_full_cleanup(self):
        """Run comprehensive database cleanup"""
        logger.info("🚀 Starting comprehensive database cleanup")
        
        cleanup_summary = {
            'timestamp': datetime.now(),
            'collections_processed': 0,
            'total_deleted': 0,
            'total_archived': 0,
            'total_space_saved_mb': 0,
            'cleanup_results': [],
            'optimization_results': [],
            'compaction_result': None,
            'health_report': None
        }
        
        # 1. Cleanup collections based on rules
        for collection_name, rules in self.cleanup_rules.items():
            try:
                # Check if collection exists
                if collection_name not in self.db.list_collection_names():
                    logger.info(f"⏭️ Collection {collection_name} does not exist, skipping")
                    continue
                
                result = self.cleanup_collection(collection_name, rules)
                
                if result:
                    cleanup_summary['cleanup_results'].append(result)
                    cleanup_summary['collections_processed'] += 1
                    cleanup_summary['total_deleted'] += result['deleted_documents']
                    cleanup_summary['total_archived'] += result['archived_documents']
                    cleanup_summary['total_space_saved_mb'] += result['space_saved_mb']
                
            except Exception as e:
                logger.error(f"❌ Error processing {collection_name}: {e}")
                cleanup_summary['cleanup_results'].append({
                    'collection': collection_name,
                    'error': str(e)
                })
        
        # 2. Optimize indexes
        optimization_results = self.optimize_indexes()
        cleanup_summary['optimization_results'] = optimization_results
        
        # 3. Compact database (optional)
        compaction_result = self.compact_database()
        cleanup_summary['compaction_result'] = compaction_result
        
        # 4. Analyze database health
        health_report = self.analyze_database_health()
        cleanup_summary['health_report'] = health_report
        
        # 5. Save cleanup log
        self.save_cleanup_log(cleanup_summary)
        
        logger.info(f"✅ Database cleanup completed")
        logger.info(f"📊 Processed {cleanup_summary['collections_processed']} collections")
        logger.info(f"🗑️ Deleted {cleanup_summary['total_deleted']} documents")
        logger.info(f"📦 Archived {cleanup_summary['total_archived']} documents")
        logger.info(f"💾 Space saved: {cleanup_summary['total_space_saved_mb']:.2f} MB")
        
        return cleanup_summary
    
    def save_cleanup_log(self, summary):
        """Save cleanup log to database"""
        try:
            # Convert datetime objects for JSON serialization
            summary_copy = json.loads(json.dumps(summary, default=str))
            
            # Save to cleanup_logs collection
            self.db.cleanup_logs.insert_one(summary_copy)
            
            # Keep only last 30 cleanup logs
            old_logs = list(self.db.cleanup_logs.find().sort('timestamp', -1).skip(30))
            for old_log in old_logs:
                self.db.cleanup_logs.delete_one({'_id': old_log['_id']})
            
            logger.info("💾 Cleanup log saved to database")
            
        except Exception as e:
            logger.error(f"❌ Error saving cleanup log: {e}")

def main():
    """Main function for cronjob execution"""
    try:
        cleanup = DatabaseCleanup()
        
        # Run comprehensive cleanup
        summary = cleanup.run_full_cleanup()
        
        # Print summary
        print(f"✅ Database cleanup completed successfully")
        print(f"📊 Collections processed: {summary['collections_processed']}")
        print(f"🗑️ Documents deleted: {summary['total_deleted']}")
        print(f"📦 Documents archived: {summary['total_archived']}")
        print(f"💾 Space saved: {summary['total_space_saved_mb']:.2f} MB")
        
        if summary['health_report'] and summary['health_report'].get('recommendations'):
            print(f"\n📋 Health recommendations:")
            for rec in summary['health_report']['recommendations'][:3]:
                print(f"  {rec['priority'].upper()}: {rec['message']}")
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Database cleanup failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main()) 