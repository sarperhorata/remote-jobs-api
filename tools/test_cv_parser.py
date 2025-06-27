#!/usr/bin/env python3

import sys
import os
sys.path.append('backend')

from utils.cv_parser import CVParser

def test_cv_samples():
    """Test CV parsing with sample files"""
    cv_samples = [
        'cv-samples/SH PM Photo v3.pdf',
        'cv-samples/Hakan Ermis.pdf', 
        'cv-samples/ArdaTisikResume.pdf',
        'cv-samples/BurakBasaranResume.pdf',
        'cv-samples/SinemDemirbilekResume.pdf'
    ]

    parser = CVParser()
    
    print("🧪 CV Parser Test Başlıyor...")
    print("=" * 80)

    for cv_file in cv_samples:
        if os.path.exists(cv_file):
            print(f'\n📄 Test ediliyor: {cv_file}')
            print('-' * 60)
            
            try:
                result = parser.parse_cv_file(cv_file)
                
                if result.get('error'):
                    print(f'❌ Hata: {result["error"]}')
                else:
                    print(f'✅ İsim: {result.get("name", "N/A")}')
                    print(f'📧 Email: {result.get("email", "N/A")}')
                    print(f'📱 Telefon: {result.get("phone", "N/A")}')
                    print(f'💼 Pozisyon: {result.get("title", "N/A")}')
                    
                    skills = result.get("skills", [])
                    print(f'🎯 Beceriler ({len(skills)}): {", ".join(skills[:5])}{"..." if len(skills) > 5 else ""}')
                    
                    print(f'📈 Güven Skoru: {result.get("confidence_score", 0):.1f}%')
                    print(f'💡 Deneyim: {len(result.get("experience", []))} giriş')
                    print(f'🎓 Eğitim: {len(result.get("education", []))} giriş')
                    
                    # Show experience details if available
                    experience = result.get("experience", [])
                    if experience:
                        print("💼 Deneyim detayları:")
                        for i, exp in enumerate(experience[:2]):  # Show first 2
                            print(f"   {i+1}. {exp.get('title', 'N/A')}")
                    
                    # Show education details if available  
                    education = result.get("education", [])
                    if education:
                        print("🎓 Eğitim detayları:")
                        for i, edu in enumerate(education[:2]):  # Show first 2
                            print(f"   {i+1}. {edu.get('degree', 'N/A')}")
                            
            except Exception as e:
                print(f'❌ İşlem hatası: {str(e)}')
        else:
            print(f'❌ Dosya bulunamadı: {cv_file}')

    print("\n" + "=" * 80)
    print("🏁 CV Parser Test Tamamlandı!")

if __name__ == '__main__':
    test_cv_samples() 