#!/usr/bin/env python3

import sys
import asyncio
import json
import aiohttp
import logging
from bs4 import BeautifulSoup

sys.path.append('backend')

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

async def debug_tether_detailed():
    """Detailed debug of Tether crawling"""
    
    # Find Tether company
    with open('distill-export/Distill export - 01-18_2025-05-25.json', 'r') as f:
        data = json.load(f)

    tether_companies = [c for c in data['data'] if 'tether' in c.get('name', '').lower()]
    
    if not tether_companies:
        print("❌ No Tether companies found")
        return

    company = tether_companies[0]
    uri = company.get('uri')
    config_str = company.get('config', '{}')
    
    print(f'🏢 Company: {company.get("name")}')
    print(f'🔗 URL: {uri}')
    
    try:
        config = json.loads(config_str) if config_str else {}
        print(f'📋 Config parsed successfully')
        
        selections = config.get('selections', [])
        print(f'📊 Selections found: {len(selections)}')
        
        for i, selection in enumerate(selections):
            print(f'  Selection {i+1}:')
            frames = selection.get('frames', [])
            print(f'    Frames: {len(frames)}')
            
            for j, frame in enumerate(frames):
                includes = frame.get('includes', [])
                print(f'      Frame {j+1} includes: {len(includes)}')
                
                for k, include in enumerate(includes):
                    selector_type = include.get('type', 'xpath')
                    expr = include.get('expr')
                    print(f'        Include {k+1}: type={selector_type}, expr={expr}')
        
    except Exception as e:
        print(f'❌ Config parsing error: {e}')
    
    # Manual fetch and test
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    async with aiohttp.ClientSession(headers=headers) as session:
        try:
            async with session.get(uri, timeout=30) as response:
                print(f'🌐 HTTP Status: {response.status}')
                
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    print(f'📄 HTML length: {len(html)} chars')
                    
                    # Test the specific CSS selector from distill config
                    css_selector = "[data-scroll-point^='section-jobs'] .iFQjUO"
                    print(f'🔍 Testing CSS selector: {css_selector}')
                    
                    try:
                        elements = soup.select(css_selector)
                        print(f'✅ Found {len(elements)} elements with specific selector')
                        
                        for i, elem in enumerate(elements[:5]):
                            text = elem.get_text(strip=True)
                            print(f'   {i+1}. "{text[:100]}..."')
                            
                    except Exception as e:
                        print(f'❌ CSS selector error: {e}')
                    
                    # Test fallback selectors
                    fallback_selectors = [
                        '.job', '.position', '.opening', '.career',
                        '[class*="job"]', '[class*="position"]',
                        'h1, h2, h3, h4',
                        'a[href*="job"]'
                    ]
                    
                    print(f'\n🔄 Testing fallback selectors:')
                    for selector in fallback_selectors:
                        try:
                            elements = soup.select(selector)
                            print(f'   {selector}: {len(elements)} elements')
                            if elements:
                                for elem in elements[:2]:
                                    text = elem.get_text(strip=True)
                                    if text and len(text) > 10:
                                        print(f'     • "{text[:80]}..."')
                        except Exception as e:
                            print(f'   {selector}: ERROR - {e}')
                    
                else:
                    print(f'❌ HTTP Error: {response.status}')
                    
        except Exception as e:
            print(f'❌ Request error: {e}')

if __name__ == '__main__':
    asyncio.run(debug_tether_detailed()) 