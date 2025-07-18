#!/usr/bin/env python3
"""
Product Manager Job Titles Analysis
Bu script Product Manager ile ilgili tüm ilanları analiz eder ve title'ları gruplar.
"""

import requests
import json
import re
from collections import defaultdict, Counter

def clean_job_title(title: str) -> str:
    """Clean and normalize job titles - Enhanced version"""
    if not title:
        return ""
    
    # Remove obvious noise patterns
    title = re.sub(r'Current Open Jobs', '', title, flags=re.IGNORECASE)
    title = re.sub(r'Open Applications', '', title, flags=re.IGNORECASE)
    title = re.sub(r'Customer Support', '', title, flags=re.IGNORECASE)
    
    # Remove person names at the beginning (Jakub TutajSenior...)
    title = re.sub(r'^[A-Z][a-z]+\s+[A-Z][a-z]+(?=[A-Z])', '', title)
    
    # Remove company names at the end (ManagerMixmax -> Manager)
    title = re.sub(r'([a-z])([A-Z][a-z]+)$', r'\1', title)
    
    # Fix concatenated words by adding spaces before capitals
    title = re.sub(r'([a-z])([A-Z])', r'\1 \2', title)
    
    # Remove extra whitespace and normalize
    title = re.sub(r'\s+', ' ', title).strip()
    
    # Remove leading/trailing punctuation
    title = title.strip('.,;:-_|')
    
    return title

def normalize_job_title(title: str) -> str:
    """Normalize job titles for grouping"""
    cleaned = clean_job_title(title)
    if not cleaned:
        return ""
    
    # Convert to lowercase for comparison
    normalized = cleaned.lower()
    
    # Remove common prefixes/suffixes for grouping
    prefixes = ['senior', 'sr', 'junior', 'jr', 'lead', 'principal', 'staff', 'associate', 'assistant']
    suffixes = ['i', 'ii', 'iii', 'iv', '1', '2', '3', '4', '5']
    
    # Remove level indicators
    words = normalized.split()
    filtered_words = []
    
    for word in words:
        # Skip common level indicators
        if word not in prefixes and word not in suffixes:
            filtered_words.append(word)
    
    return ' '.join(filtered_words)

def analyze_product_manager_jobs():
    """Analyze Product Manager job titles"""
    
    # Fetch all Product Manager jobs
    print("🔍 Fetching Product Manager jobs...")
    response = requests.get("http://localhost:8001/api/v1/jobs/search?q=Product%20Manager&limit=5000", timeout=30)
    
    if response.status_code != 200:
        print(f"❌ Error fetching jobs: {response.status_code}")
        return
    
    data = response.json()
    jobs = data.get('jobs', [])
    total = data.get('total', 0)
    
    print(f"📊 Found {len(jobs)} jobs out of {total} total Product Manager positions")
    
    if not jobs:
        print("❌ No jobs found!")
        return
    
    # Analyze titles
    print("\n🧹 Analyzing and cleaning job titles...")
    
    original_titles = [job.get('title', '') for job in jobs]
    print(f"📝 Original titles sample:")
    for i, title in enumerate(original_titles[:10]):
        print(f"  {i+1}. '{title}'")
    
    # Clean titles
    cleaned_titles = [clean_job_title(title) for title in original_titles]
    print(f"\n✨ Cleaned titles sample:")
    for i, title in enumerate(cleaned_titles[:10]):
        print(f"  {i+1}. '{title}'")
    
    # Group by normalized titles
    title_groups = defaultdict(list)
    
    for i, job in enumerate(jobs):
        original_title = job.get('title', '')
        cleaned_title = clean_job_title(original_title)
        normalized_title = normalize_job_title(original_title)
        
        if normalized_title:
            title_groups[normalized_title].append({
                'original': original_title,
                'cleaned': cleaned_title,
                'company': job.get('company', ''),
                'job_id': job.get('_id', job.get('id', ''))
            })
    
    # Analyze groups
    print(f"\n📊 TITLE GROUPING ANALYSIS")
    print(f"{'='*50}")
    print(f"Total jobs analyzed: {len(jobs)}")
    print(f"Unique normalized titles: {len(title_groups)}")
    print(f"Average jobs per title: {len(jobs) / len(title_groups):.1f}")
    
    # Sort by frequency
    sorted_groups = sorted(title_groups.items(), key=lambda x: len(x[1]), reverse=True)
    
    print(f"\n🏆 TOP PRODUCT MANAGER TITLE GROUPS:")
    print(f"{'='*50}")
    
    for normalized_title, job_list in sorted_groups:
        count = len(job_list)
        print(f"\n📌 '{normalized_title.title()}' ({count} jobs)")
        
        # Show variations
        original_titles = [job['original'] for job in job_list]
        title_counts = Counter(original_titles)
        
        print(f"   Variations:")
        for variation, var_count in title_counts.most_common(5):
            print(f"     • '{variation}' ({var_count}x)")
        
        if len(title_counts) > 5:
            print(f"     ... and {len(title_counts) - 5} more variations")
    
    # Save detailed analysis
    analysis_result = {
        'query': 'Product Manager',
        'total_jobs': total,
        'analyzed_jobs': len(jobs),
        'unique_titles': len(title_groups),
        'groups': {}
    }
    
    for normalized_title, job_list in sorted_groups:
        original_titles = [job['original'] for job in job_list]
        title_counts = Counter(original_titles)
        
        analysis_result['groups'][normalized_title] = {
            'count': len(job_list),
            'variations': dict(title_counts),
            'most_common': title_counts.most_common(1)[0][0] if title_counts else normalized_title,
            'companies': list(set([job['company'] for job in job_list if job['company']]))
        }
    
    # Save to file
    with open('product_manager_analysis.json', 'w') as f:
        json.dump(analysis_result, f, indent=2)
    
    print(f"\n💾 Detailed analysis saved to: product_manager_analysis.json")
    
    return analysis_result

if __name__ == "__main__":
    try:
        result = analyze_product_manager_jobs()
        print(f"\n✅ Analysis completed successfully!")
    except Exception as e:
        print(f"\n❌ Error: {e}") 