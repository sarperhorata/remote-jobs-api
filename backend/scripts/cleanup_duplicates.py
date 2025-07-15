#!/usr/bin/env python3
"""
Job Duplication Cleanup Script

Bu script mevcut veritabanındaki duplikasyonları tespit eder ve temizler.
"""

import asyncio
import logging
import sys
import os
from datetime import datetime

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.job_deduplication_service import deduplication_service
from database import get_async_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def cleanup_existing_duplicates():
    """Clean up existing duplicates in the database"""
    try:
        logger.info("🚀 Starting duplicate cleanup process...")
        
        # Step 1: Generate duplicate report
        logger.info("📊 Generating duplicate report...")
        report = await deduplication_service.get_duplicate_report()
        
        logger.info(f"📈 Duplicate Report Summary:")
        logger.info(f"   • Total jobs: {report['total_jobs']}")
        logger.info(f"   • Total duplicates: {report['total_duplicates']}")
        logger.info(f"   • Companies with duplicates: {report['companies_with_duplicates']}")
        
        if report['total_duplicates'] == 0:
            logger.info("✅ No duplicates found! Database is clean.")
            return
        
        # Step 2: Show detailed duplicate groups
        logger.info("\n🔍 Detailed Duplicate Groups:")
        for company_group in report['duplicate_groups']:
            logger.info(f"\n🏢 Company: {company_group['company']}")
            logger.info(f"   • Total jobs: {company_group['total_jobs']}")
            logger.info(f"   • Duplicate count: {company_group['duplicate_count']}")
            
            for i, group in enumerate(company_group['groups'], 1):
                logger.info(f"   • Group {i}: {len(group)} similar jobs")
                for job in group[:3]:  # Show first 3 jobs
                    logger.info(f"     - {job.get('title', 'No title')} (ID: {job['_id']})")
                if len(group) > 3:
                    logger.info(f"     ... and {len(group) - 3} more")
        
        # Step 3: Ask for confirmation
        print(f"\n⚠️  Found {report['total_duplicates']} duplicates across {report['companies_with_duplicates']} companies.")
        response = input("Do you want to proceed with cleanup? (y/N): ")
        
        if response.lower() != 'y':
            logger.info("❌ Cleanup cancelled by user.")
            return
        
        # Step 4: Perform cleanup
        logger.info("🧹 Starting duplicate cleanup...")
        stats = await deduplication_service.find_and_remove_duplicates()
        
        logger.info(f"✅ Cleanup completed!")
        logger.info(f"📊 Cleanup Statistics:")
        logger.info(f"   • Total jobs checked: {stats.total_checked}")
        logger.info(f"   • Duplicates found: {stats.duplicates_found}")
        logger.info(f"   • Duplicates removed: {stats.removed_duplicates}")
        logger.info(f"   • Processing time: {stats.processing_time:.2f} seconds")
        
        # Step 5: Generate final report
        logger.info("\n📋 Generating final report...")
        final_report = await deduplication_service.get_duplicate_report()
        
        logger.info(f"🎉 Final Status:")
        logger.info(f"   • Remaining jobs: {final_report['total_jobs']}")
        logger.info(f"   • Remaining duplicates: {final_report['total_duplicates']}")
        
        if final_report['total_duplicates'] == 0:
            logger.info("🎊 Perfect! All duplicates have been removed.")
        else:
            logger.info(f"⚠️  {final_report['total_duplicates']} duplicates still remain (low confidence matches).")
        
    except Exception as e:
        logger.error(f"❌ Error during cleanup: {str(e)}")
        raise

async def analyze_duplicates_only():
    """Only analyze duplicates without cleaning up"""
    try:
        logger.info("🔍 Analyzing duplicates in database...")
        
        report = await deduplication_service.get_duplicate_report()
        
        logger.info(f"📊 Duplicate Analysis Report:")
        logger.info(f"   • Total jobs: {report['total_jobs']}")
        logger.info(f"   • Total duplicates: {report['total_duplicates']}")
        logger.info(f"   • Companies with duplicates: {report['companies_with_duplicates']}")
        
        if report['total_duplicates'] > 0:
            logger.info("\n🔍 Duplicate Details:")
            for company_group in report['duplicate_groups']:
                logger.info(f"\n🏢 {company_group['company']}:")
                logger.info(f"   • Jobs: {company_group['total_jobs']}")
                logger.info(f"   • Duplicates: {company_group['duplicate_count']}")
                
                for i, group in enumerate(company_group['groups'], 1):
                    logger.info(f"   • Group {i} ({len(group)} jobs):")
                    for job in group:
                        logger.info(f"     - {job.get('title', 'No title')} (ID: {job['_id']})")
        else:
            logger.info("✅ No duplicates found!")
        
    except Exception as e:
        logger.error(f"❌ Error during analysis: {str(e)}")
        raise

async def main():
    """Main function"""
    if len(sys.argv) > 1 and sys.argv[1] == "--analyze-only":
        await analyze_duplicates_only()
    else:
        await cleanup_existing_duplicates()

if __name__ == "__main__":
    asyncio.run(main()) 