import json
import os
from collections import defaultdict

def parse_distill_export():
    """Parse the distill export JSON file and analyze company data"""
    try:
        # Read the JSON file
        json_path = 'distill-export/Distill export - 01-18_2025-05-25.json'
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        companies = data['data']
        print(f'📊 Toplam şirket sayısı: {len(companies)}')
        
        # Analyze domains
        domains = defaultdict(int)
        unique_urls = set()
        duplicate_urls = []
        
        print('\n📋 Şirket listesi ve URL\'leri:')
        print('=' * 80)
        
        for i, company in enumerate(companies):
            name = company.get('name', 'Unknown')
            uri = company.get('uri', 'No URI')
            
            # Check for duplicates
            if uri in unique_urls:
                duplicate_urls.append((name, uri))
            else:
                unique_urls.add(uri)
            
            # Extract domain
            if uri and uri.startswith('http'):
                domain = uri.split('/')[2]
                domains[domain] += 1
            
            print(f'{i+1:3d}. {name:<50} | {uri}')
        
        print('\n' + '=' * 80)
        print(f'✅ Benzersiz URL sayısı: {len(unique_urls)}')
        print(f'🔄 Duplikat URL sayısı: {len(duplicate_urls)}')
        
        if duplicate_urls:
            print('\n❌ Duplikat URL\'ler:')
            for name, uri in duplicate_urls:
                print(f'   - {name}: {uri}')
        
        # Show top domains
        print('\n🌐 En çok şirket olan domainler:')
        sorted_domains = sorted(domains.items(), key=lambda x: x[1], reverse=True)
        for domain, count in sorted_domains[:10]:
            print(f'   {domain}: {count} şirket')
        
        # Analyze job sites
        job_platforms = {
            'lever.co': 'Lever',
            'greenhouse.io': 'Greenhouse', 
            'workable.com': 'Workable',
            'breezy.hr': 'Breezy',
            'smartrecruiters.com': 'SmartRecruiters',
            'ashbyhq.com': 'Ashby',
            'freshteam.com': 'Freshteam'
        }
        
        platform_counts = defaultdict(int)
        custom_sites = []
        
        for company in companies:
            uri = company.get('uri', '')
            is_platform = False
            
            for platform_domain, platform_name in job_platforms.items():
                if platform_domain in uri:
                    platform_counts[platform_name] += 1
                    is_platform = True
                    break
            
            if not is_platform and uri:
                custom_sites.append((company.get('name'), uri))
        
        print('\n💼 İş platformları dağılımı:')
        for platform, count in platform_counts.items():
            print(f'   {platform}: {count} şirket')
        
        print(f'\n🏢 Kendi sitelerini kullanan şirketler: {len(custom_sites)}')
        
        return {
            'total_companies': len(companies),
            'unique_urls': len(unique_urls),
            'duplicates': duplicate_urls,
            'companies': companies,
            'domains': dict(domains),
            'platform_counts': dict(platform_counts),
            'custom_sites': custom_sites
        }
        
    except Exception as e:
        print(f'❌ Hata: {str(e)}')
        return None

if __name__ == '__main__':
    result = parse_distill_export() 