#!/usr/bin/env python3

import sys
import os
import asyncio
from datetime import datetime
from collections import defaultdict

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import settings
from motor.motor_asyncio import AsyncIOMotorClient

# Setup database connection
client = AsyncIOMotorClient(settings.MONGODB_URL)
db = client[settings.MONGODB_DB_NAME]

async def analyze_all_errors():
    try:
        # Get the latest company enrichment errors
        latest_log = await db.processing_logs.find_one(
            {'type': 'company_website_enrichment'},
            sort=[('timestamp', -1)]
        )
        
        if latest_log:
            print(f'📊 COMPANY ENRICHMENT ERROR ANALYSIS')
            print('=' * 60)
            
            # Process frontend/processing errors
            processing_errors = latest_log.get('processing_errors', [])
            print(f'\n🔴 FRONTEND/PROCESSING ERRORS: {len(processing_errors)}')
            print('-' * 50)
            
            if processing_errors:
                # Group by error type
                error_types = defaultdict(list)
                
                for error in processing_errors:
                    error_type = error.get('error_type', 'unknown')
                    error_types[error_type].append(error)
                
                # Show breakdown by error type
                for error_type, errors in error_types.items():
                    print(f'\n📋 {error_type.upper()}: {len(errors)} errors')
                    
                    # Show first few examples
                    for i, error in enumerate(errors[:5], 1):
                        company_name = error.get('company_name', 'Unknown')
                        error_message = error.get('error_message', 'No message')
                        uri = error.get('uri', 'No URL')
                        
                        print(f'  {i}. {company_name}')
                        print(f'     Error: {error_message}')
                        print(f'     URL: {uri}')
                        print()
                    
                    if len(errors) > 5:
                        print(f'     ... and {len(errors) - 5} more similar errors\n')
            
            # Process database update errors  
            update_errors = latest_log.get('update_errors', [])
            print(f'\n🟡 DATABASE UPDATE ERRORS: {len(update_errors)}')
            print('-' * 50)
            print('(These are companies successfully crawled but not found in jobs database)')
            
            if update_errors:
                # Group by error message pattern
                db_error_types = defaultdict(list)
                
                for error in update_errors:
                    error_message = error.get('error_message', 'unknown')
                    if 'No jobs found' in error_message:
                        db_error_types['jobs_not_found'].append(error)
                    else:
                        db_error_types['other_db_error'].append(error)
                
                for error_type, errors in db_error_types.items():
                    print(f'\n📋 {error_type.upper()}: {len(errors)} errors')
                    
                    # Show first few examples
                    for i, error in enumerate(errors[:3], 1):
                        company_name = error.get('company_name', 'Unknown')
                        website = error.get('website', 'No website')
                        
                        print(f'  {i}. {company_name} → {website}')
                    
                    if len(errors) > 3:
                        print(f'     ... and {len(errors) - 3} more')
            
            # Stats summary
            stats = latest_log.get('stats', {})
            print(f'\n📊 SUMMARY:')
            print('-' * 30)
            print(f'Total companies: {stats.get("total_companies", 0)}')
            print(f'Successful updates: {stats.get("updated_companies", 0)}')
            print(f'Frontend/processing errors: {len(processing_errors)}')
            print(f'Database update errors: {len(update_errors)}')
            print(f'Success rate: {(stats.get("updated_companies", 0) / stats.get("total_companies", 1) * 100):.1f}%')
            
            # Most important for user: Frontend errors that need website fixes
            if processing_errors:
                print(f'\n🎯 PRIORITY FOR WEBSITE FIXES: {len(processing_errors)} companies need website-level fixes')
            else:
                print(f'\n✅ NO FRONTEND ERRORS: All {stats.get("total_companies", 0)} companies were successfully crawled!')
                print('The 230 errors are only company name matching issues in database.')
                
        else:
            print('❌ No processing log found')
            
    except Exception as e:
        print(f'❌ Error: {e}')
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(analyze_all_errors()) 