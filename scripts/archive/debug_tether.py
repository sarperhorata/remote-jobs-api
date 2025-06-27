#!/usr/bin/env python3

import json
import sys
import asyncio
import aiohttp
from bs4 import BeautifulSoup

sys.path.append('backend')

async def debug_tether_crawling():
    """Debug Tether company crawling to understand why it finds 0 jobs"""
    
    # Find Tether companies in distill export
    with open('distill-export/Distill export - 01-18_2025-05-25.json', 'r') as f:
        data = json.load(f)

    tether_companies = [c for c in data['data'] if 'tether' in c.get('name', '').lower()]
    
    if not tether_companies:
        print("❌ No Tether companies found in distill export")
        return

    for company in tether_companies:
        print(f'🏢 Company: {company.get("name")}')
        print(f'🔗 URL: {company.get("uri")}')
        
        config = company.get('config', '{}')
        if config:
            try:
                config_obj = json.loads(config)
                print(f'📋 Config object: {json.dumps(config_obj, indent=2)[:500]}...')
            except:
                print(f'📋 Config (raw): {config[:200]}...')
        
        print()
        
        # Try to manually fetch and check the page
        uri = company.get('uri')
        if uri:
            print(f"🕷️ Manually checking: {uri}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            try:
                async with aiohttp.ClientSession(headers=headers) as session:
                    async with session.get(uri, timeout=30) as response:
                        if response.status == 200:
                            html = await response.text()
                            soup = BeautifulSoup(html, 'html.parser')
                            
                            print(f"✅ Page fetched successfully ({len(html)} chars)")
                            
                            # Look for common job-related elements
                            job_keywords = ['job', 'career', 'position', 'opening', 'hiring', 'apply']
                            job_elements = []
                            
                            for keyword in job_keywords:
                                elements = soup.find_all(text=lambda text: text and keyword in text.lower())
                                job_elements.extend(elements[:5])  # Limit to 5 per keyword
                            
                            print(f"🎯 Found {len(job_elements)} job-related text elements")
                            for i, elem in enumerate(job_elements[:10]):
                                print(f"   {i+1}. {elem.strip()[:100]}...")
                            
                            # Check for common job selectors
                            common_selectors = [
                                '.job', '.position', '.opening', '.career', 
                                '[class*="job"]', '[class*="position"]', '[class*="career"]',
                                'h1, h2, h3, h4, h5, h6'
                            ]
                            
                            for selector in common_selectors:
                                try:
                                    elements = soup.select(selector)
                                    if elements:
                                        print(f"🔍 Selector '{selector}': {len(elements)} elements found")
                                        for elem in elements[:3]:
                                            text = elem.get_text(strip=True)
                                            if text and len(text) > 10:
                                                print(f"     • {text[:80]}...")
                                except Exception as e:
                                    print(f"❌ Error with selector '{selector}': {e}")
                        else:
                            print(f"❌ HTTP {response.status}")
                            
            except Exception as e:
                print(f"❌ Error fetching page: {str(e)}")
        
        print("=" * 80)

if __name__ == '__main__':
    asyncio.run(debug_tether_crawling()) 