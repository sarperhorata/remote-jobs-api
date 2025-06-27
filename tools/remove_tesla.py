#!/usr/bin/env python3

import json

def remove_tesla_entries():
    """Remove Tesla entries from distill export"""
    
    # Load distill export
    with open('distill-export/Distill export - 01-18_2025-05-25.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    original_count = len(data['data'])
    print(f'Original company count: {original_count}')
    
    # Find Tesla entries
    tesla_entries = [item for item in data['data'] if 'tesla.com' in item.get('uri', '').lower()]
    print(f'Found {len(tesla_entries)} Tesla entries:')
    for entry in tesla_entries:
        print(f'  - {entry.get("name", "Unknown")} - {entry.get("uri", "")}')
    
    # Filter out Tesla entries
    data['data'] = [item for item in data['data'] if 'tesla.com' not in item.get('uri', '').lower()]
    
    new_count = len(data['data'])
    print(f'New company count: {new_count}')
    print(f'Removed {original_count - new_count} Tesla entries')
    
    # Save updated file
    with open('distill-export/Distill export - 01-18_2025-05-25.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print('✅ Tesla entries removed and file updated')

if __name__ == "__main__":
    remove_tesla_entries() 