#!/usr/bin/env python3

import json
from collections import defaultdict

def find_duplicate_urls():
    """Find and list duplicate URLs from distill export"""
    
    with open('distill-export/Distill export - 01-18_2025-05-25.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    url_companies = defaultdict(list)
    for company in data['data']:
        uri = company.get('uri')
        name = company.get('name')
        url_companies[uri].append(name)

    duplicates = {uri: names for uri, names in url_companies.items() if len(names) > 1}

    print('🔄 Duplicate URL\'ler:')
    print('=' * 80)
    
    for uri, names in duplicates.items():
        print(f'\n📍 URL: {uri}')
        for i, name in enumerate(names, 1):
            print(f'   {i}. {name}')
    
    print(f'\n📊 Toplam duplicate URL: {len(duplicates)}')
    print(f'📊 Toplam şirket: {len(data["data"])}')
    print(f'📊 Benzersiz URL: {len(url_companies)}')
    
    return duplicates

if __name__ == '__main__':
    find_duplicate_urls() 