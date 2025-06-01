#!/usr/bin/env python3

import sys
import os
import asyncio
from datetime import datetime

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import settings
from motor.motor_asyncio import AsyncIOMotorClient

# Setup database connection
client = AsyncIOMotorClient(settings.MONGODB_URL)
db = client[settings.MONGODB_DB_NAME]

async def get_errors():
    try:
        # Get the latest company enrichment errors
        latest_log = await db.processing_logs.find_one(
            {'type': 'company_website_enrichment'},
            sort=[('timestamp', -1)]
        )
        
        if latest_log and 'update_errors' in latest_log:
            errors = latest_log['update_errors']
            print(f'📊 Son crawl sonucunda {len(errors)} şirket için veritabanında job bulunamadı:')
            print('=' * 80)
            
            # Group errors by type for better analysis
            no_jobs_found = []
            
            for error in errors:
                company_name = error.get('company_name', 'Unknown')
                career_url = error.get('career_page', 'No URL')
                website = error.get('website', 'No website')
                error_message = error.get('error_message', 'No message')
                
                if 'No jobs found' in error_message:
                    no_jobs_found.append({
                        'name': company_name,
                        'career_url': career_url,
                        'website': website
                    })
            
            print(f'\n🎯 ŞİRKETLER (Veritabanında job bulunamayan):')
            print('-' * 80)
            
            for i, company in enumerate(no_jobs_found, 1):
                print(f'{i:3d}. {company["name"]}')
                print(f'     Career URL: {company["career_url"]}')
                print(f'     Website: {company["website"]}')
                print()
                
            print(f'\n📝 ÖZET:')
            print(f'Toplam problem: {len(errors)}')
            print(f'Job bulunamayan: {len(no_jobs_found)}')
            
            # Also show some examples of companies that DO have jobs for comparison
            print(f'\n✅ BAŞARILI ÖRNEKLER (Karşılaştırma için):')
            
            # Get some successful companies from the stats
            if 'stats' in latest_log:
                stats = latest_log['stats']
                print(f'Başarılı güncellenen şirket sayısı: {stats.get("updated_companies", 0)}')
                
        else:
            print('❌ No processing log found')
            
    except Exception as e:
        print(f'❌ Error: {e}')
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(get_errors()) 