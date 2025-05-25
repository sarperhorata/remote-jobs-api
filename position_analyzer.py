#!/usr/bin/env python3
"""
Position Analyzer - Groups similar job positions
Benzer pozisyonları gruplar ve analiz eder
"""

import re
from typing import Dict, List, Set
from collections import defaultdict
from backend.database import get_db

class PositionAnalyzer:
    """Pozisyonları analiz eden ve gruplandıran sınıf"""
    
    def __init__(self):
        self.db = get_db()
        self.jobs_collection = self.db.jobs
        
        # Pozisyon grupları tanımları
        self.position_groups = {
            'product_management': {
                'keywords': ['product manager', 'product owner', 'product lead', 'cpo', 'chief product officer', 'product director', 'product head'],
                'variations': ['senior', 'junior', 'lead', 'principal', 'staff', 'director', 'head', 'chief']
            },
            'project_management': {
                'keywords': ['project manager', 'program manager', 'scrum master', 'agile coach', 'delivery manager'],
                'variations': ['senior', 'junior', 'lead', 'principal', 'staff', 'director', 'head']
            },
            'software_engineering': {
                'keywords': ['software engineer', 'developer', 'programmer', 'software developer', 'full stack', 'backend', 'frontend', 'mobile developer'],
                'variations': ['senior', 'junior', 'lead', 'principal', 'staff', 'architect', 'tech lead']
            },
            'data_science': {
                'keywords': ['data scientist', 'data analyst', 'data engineer', 'machine learning', 'ai engineer', 'ml engineer'],
                'variations': ['senior', 'junior', 'lead', 'principal', 'staff', 'head', 'director']
            },
            'devops_engineering': {
                'keywords': ['devops', 'site reliability', 'sre', 'platform engineer', 'infrastructure engineer', 'cloud engineer'],
                'variations': ['senior', 'junior', 'lead', 'principal', 'staff', 'architect']
            },
            'design': {
                'keywords': ['ui designer', 'ux designer', 'product designer', 'graphic designer', 'visual designer', 'interaction designer'],
                'variations': ['senior', 'junior', 'lead', 'principal', 'head', 'director']
            },
            'marketing': {
                'keywords': ['marketing manager', 'digital marketing', 'content marketing', 'growth marketing', 'marketing specialist'],
                'variations': ['senior', 'junior', 'lead', 'director', 'head', 'chief marketing officer', 'cmo']
            },
            'sales': {
                'keywords': ['sales manager', 'account manager', 'business development', 'sales representative', 'account executive'],
                'variations': ['senior', 'junior', 'lead', 'director', 'head', 'chief sales officer', 'cso']
            },
            'hr_people': {
                'keywords': ['hr manager', 'people manager', 'talent acquisition', 'recruiter', 'hr specialist', 'people operations'],
                'variations': ['senior', 'junior', 'lead', 'director', 'head', 'chief people officer', 'cpo']
            },
            'finance': {
                'keywords': ['finance manager', 'financial analyst', 'accountant', 'controller', 'cfo', 'chief financial officer'],
                'variations': ['senior', 'junior', 'lead', 'director', 'head', 'chief']
            }
        }
    
    def normalize_title(self, title: str) -> str:
        """Pozisyon başlığını normalize eder"""
        if not title:
            return ""
        
        # Küçük harfe çevir
        title = title.lower().strip()
        
        # Özel karakterleri temizle
        title = re.sub(r'[^\w\s]', ' ', title)
        
        # Çoklu boşlukları tek boşluğa çevir
        title = re.sub(r'\s+', ' ', title)
        
        return title
    
    def extract_seniority_level(self, title: str) -> str:
        """Pozisyondan tecrübe seviyesini çıkarır"""
        title_lower = title.lower()
        
        if any(word in title_lower for word in ['chief', 'cto', 'ceo', 'cfo', 'cpo', 'cmo']):
            return 'executive'
        elif any(word in title_lower for word in ['director', 'head', 'vp', 'vice president']):
            return 'director'
        elif any(word in title_lower for word in ['principal', 'staff', 'architect']):
            return 'principal'
        elif any(word in title_lower for word in ['senior', 'sr', 'lead']):
            return 'senior'
        elif any(word in title_lower for word in ['junior', 'jr', 'entry', 'intern', 'trainee']):
            return 'junior'
        else:
            return 'mid'
    
    def categorize_position(self, title: str) -> str:
        """Pozisyonu kategorize eder"""
        title_normalized = self.normalize_title(title)
        
        for category, config in self.position_groups.items():
            for keyword in config['keywords']:
                if keyword in title_normalized:
                    return category
        
        return 'other'
    
    def analyze_positions(self) -> Dict:
        """Tüm pozisyonları analiz eder"""
        print("🔍 Pozisyonlar analiz ediliyor...")
        
        # Tüm unique pozisyonları al
        pipeline = [
            {"$group": {"_id": "$title", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        
        positions = list(self.jobs_collection.aggregate(pipeline))
        
        # Analiz sonuçları
        analysis = {
            'total_unique_positions': len(positions),
            'categories': defaultdict(lambda: {'positions': [], 'total_jobs': 0}),
            'seniority_levels': defaultdict(int),
            'top_positions': positions[:20]  # En çok iş ilanı olan 20 pozisyon
        }
        
        for pos in positions:
            title = pos['_id']
            count = pos['count']
            
            if not title:
                continue
            
            # Kategori belirle
            category = self.categorize_position(title)
            
            # Tecrübe seviyesi belirle
            seniority = self.extract_seniority_level(title)
            
            # Sonuçları kaydet
            analysis['categories'][category]['positions'].append({
                'title': title,
                'count': count,
                'seniority': seniority
            })
            analysis['categories'][category]['total_jobs'] += count
            analysis['seniority_levels'][seniority] += count
        
        return analysis
    
    def get_similar_positions(self, target_title: str, limit: int = 10) -> List[Dict]:
        """Belirli bir pozisyona benzer pozisyonları bulur"""
        category = self.categorize_position(target_title)
        target_seniority = self.extract_seniority_level(target_title)
        
        # Aynı kategorideki pozisyonları bul
        pipeline = [
            {"$group": {"_id": "$title", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        
        all_positions = list(self.jobs_collection.aggregate(pipeline))
        similar_positions = []
        
        for pos in all_positions:
            title = pos['_id']
            if not title or title.lower() == target_title.lower():
                continue
            
            pos_category = self.categorize_position(title)
            pos_seniority = self.extract_seniority_level(title)
            
            if pos_category == category:
                similarity_score = 1.0
                
                # Aynı tecrübe seviyesi bonus
                if pos_seniority == target_seniority:
                    similarity_score += 0.5
                
                similar_positions.append({
                    'title': title,
                    'count': pos['count'],
                    'category': pos_category,
                    'seniority': pos_seniority,
                    'similarity_score': similarity_score
                })
        
        # Benzerlik skoruna göre sırala
        similar_positions.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        return similar_positions[:limit]
    
    def print_analysis_report(self, analysis: Dict):
        """Analiz raporunu yazdırır"""
        print("\n" + "="*60)
        print("📊 POZİSYON ANALİZ RAPORU")
        print("="*60)
        
        print(f"\n📈 Genel İstatistikler:")
        print(f"• Toplam unique pozisyon: {analysis['total_unique_positions']:,}")
        
        print(f"\n🎯 Tecrübe Seviyeleri:")
        for level, count in sorted(analysis['seniority_levels'].items(), key=lambda x: x[1], reverse=True):
            print(f"• {level.title()}: {count:,} iş ilanı")
        
        print(f"\n📂 Kategori Dağılımı:")
        sorted_categories = sorted(analysis['categories'].items(), key=lambda x: x[1]['total_jobs'], reverse=True)
        
        for category, data in sorted_categories:
            print(f"\n🔸 {category.replace('_', ' ').title()}:")
            print(f"  • Toplam iş ilanı: {data['total_jobs']:,}")
            print(f"  • Unique pozisyon: {len(data['positions'])}")
            
            # En popüler 5 pozisyonu göster
            top_positions = sorted(data['positions'], key=lambda x: x['count'], reverse=True)[:5]
            for pos in top_positions:
                print(f"    - {pos['title']} ({pos['count']} ilan)")
        
        print(f"\n🏆 En Popüler 10 Pozisyon:")
        for i, pos in enumerate(analysis['top_positions'][:10], 1):
            print(f"{i:2d}. {pos['_id']} ({pos['count']:,} ilan)")

def main():
    """Ana fonksiyon"""
    analyzer = PositionAnalyzer()
    
    # Pozisyonları analiz et
    analysis = analyzer.analyze_positions()
    
    # Raporu yazdır
    analyzer.print_analysis_report(analysis)
    
    # Örnek benzer pozisyon arama
    print(f"\n🔍 Örnek: 'Product Manager' pozisyonuna benzer pozisyonlar:")
    similar = analyzer.get_similar_positions("Product Manager", limit=5)
    for pos in similar:
        print(f"• {pos['title']} ({pos['count']} ilan) - Skor: {pos['similarity_score']:.1f}")

if __name__ == "__main__":
    main() 