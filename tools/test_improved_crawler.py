#!/usr/bin/env python3

import sys
import asyncio
import json
import aiohttp
sys.path.append('backend')

from distill_crawler import DistillCrawler

async def test_tether_crawling():
    """Test improved crawler with Tether company"""
    
    # Find Tether company in distill export
    with open('distill-export/Distill export - 01-18_2025-05-25.json', 'r') as f:
        data = json.load(f)

    tether_companies = [c for c in data['data'] if 'tether' in c.get('name', '').lower()]
    
    if not tether_companies:
        print("❌ No Tether companies found")
        return

    crawler = DistillCrawler()
    
    # Initialize session properly
    connector = aiohttp.TCPConnector(limit=10, ttl_dns_cache=300)
    timeout = aiohttp.ClientTimeout(total=60)
    
    async with aiohttp.ClientSession(
        headers=crawler.headers,
        connector=connector,
        timeout=timeout
    ) as session:
        crawler.session = session
        
        for company in tether_companies:
            print(f'🏢 Testing: {company.get("name")}')
            print(f'🔗 URL: {company.get("uri")}')
            
            # Test crawling this specific company
            jobs = await crawler.crawl_company(company)
            
            print(f'✅ Found {len(jobs)} jobs')
            
            # Show first few jobs
            for i, job in enumerate(jobs[:5]):
                print(f'   {i+1}. {job.title}')
                if job.apply_url != job.source_url:
                    print(f'      Apply: {job.apply_url}')
            
            if len(jobs) > 5:
                print(f'   ... and {len(jobs) - 5} more jobs')
            
            print()

if __name__ == '__main__':
    asyncio.run(test_tether_crawling()) 