#!/usr/bin/env python3

import sys, os
sys.path.append('backend')
from utils.cv_parser_ai import CVParserAI

def test_remaining_cvs():
    cv_files = ['cv-samples/ArdaTisikResume.pdf', 'cv-samples/BurakBasaranResume.pdf', 'cv-samples/Hakan Ermis.pdf']
    parser = CVParserAI()

    print("🧪 Testing Remaining CV Samples with AI Parser")
    print("=" * 60)

    for cv_file in cv_files:
        if os.path.exists(cv_file):
            print(f'\n📄 Testing: {cv_file}')
            print('-' * 40)
            result = parser.parse_cv_file_enhanced(cv_file)
            if result.get('error'):
                print(f'❌ Error: {result["error"]}')
            else:
                print(f'✅ Name: {result.get("name", "N/A")}')
                print(f'📧 Email: {result.get("email", "N/A")}')
                print(f'💼 Title: {result.get("title", "N/A")}')
                skills = result.get("skills", [])
                print(f'🎯 Skills ({len(skills)}): {", ".join(skills[:6])}{"..." if len(skills) > 6 else ""}')
                
                # Experience & Education count
                experience = result.get("experience", [])
                education = result.get("education", [])
                print(f'💼 Experience: {len(experience)} entries')
                print(f'🎓 Education: {len(education)} entries')
                
                print(f'📈 Confidence: {result.get("confidence_score", 0):.1f}%')
                print(f'🔧 Method: {result.get("parsing_method", "unknown")}')
                
                if result.get("ai_confidence"):
                    print(f'🤖 AI Confidence: {result.get("ai_confidence", 0):.2f}')

    print("\n" + "=" * 60)
    print("🏁 All CV tests completed!")

if __name__ == '__main__':
    test_remaining_cvs() 