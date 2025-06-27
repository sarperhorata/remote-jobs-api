#!/usr/bin/env python3

import sys
import asyncio
import json
import aiohttp
from bs4 import BeautifulSoup

sys.path.append('backend')

async def debug_container_jobs():
    """Debug container job detection"""
    
    # Find Tether company
    with open('distill-export/Distill export - 01-18_2025-05-25.json', 'r') as f:
        data = json.load(f)

    tether_companies = [c for c in data['data'] if 'tether' in c.get('name', '').lower()]
    company = tether_companies[0]
    uri = company.get('uri')
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(uri, timeout=30) as response:
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find the container
            css_selector = "[data-scroll-point^='section-jobs'] .iFQjUO"
            containers = soup.select(css_selector)
            
            print(f"🔍 Found {len(containers)} containers")
            
            if containers:
                container = containers[0]
                print(f"📦 Container text preview: {container.get_text()[:200]}...")
                
                # Test different selectors within the container
                test_selectors = [
                    'li', 'div', 'a', 'article', 'span', 'p',
                    '[class*="job"]', '[class*="position"]', '[class*="role"]',
                    'a[href*="job"]', 'a[href*="apply"]'
                ]
                
                print("\n🔍 Testing selectors within container:")
                for selector in test_selectors:
                    try:
                        elements = container.select(selector)
                        print(f"   {selector}: {len(elements)} elements")
                        
                        # Show a few examples
                        job_like_count = 0
                        for elem in elements[:10]:
                            text = elem.get_text(strip=True)
                            if 20 <= len(text) <= 200:
                                text_lower = text.lower()
                                job_keywords = ['engineer', 'developer', 'manager', 'analyst', 'designer', 'specialist']
                                if any(keyword in text_lower for keyword in job_keywords):
                                    job_like_count += 1
                                    print(f"     Job-like: {text[:80]}...")
                        
                        if job_like_count > 0:
                            print(f"     -> Found {job_like_count} job-like elements")
                    
                    except Exception as e:
                        print(f"   {selector}: ERROR - {e}")
                
                # Look for any links that might be job applications
                print("\n🔗 Looking for job application links:")
                all_links = container.find_all('a', href=True)
                print(f"   Total links in container: {len(all_links)}")
                
                job_links = []
                for link in all_links[:20]:  # Check first 20 links
                    href = link.get('href', '')
                    text = link.get_text(strip=True)
                    
                    if any(keyword in href.lower() for keyword in ['job', 'career', 'position', 'apply']):
                        job_links.append((text, href))
                    elif any(keyword in text.lower() for keyword in ['engineer', 'developer', 'manager', 'analyst']):
                        job_links.append((text, href))
                
                print(f"   Potential job links: {len(job_links)}")
                for text, href in job_links[:5]:
                    print(f"     • {text[:60]}... -> {href[:80]}...")

if __name__ == '__main__':
    asyncio.run(debug_container_jobs()) 