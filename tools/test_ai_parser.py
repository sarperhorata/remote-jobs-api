#!/usr/bin/env python3

import sys
import os
sys.path.append('backend')

from utils.cv_parser_ai import CVParserAI

def test_ai_cv_parser():
    """Test AI-enhanced CV parser"""
    
    print("🤖 AI-Enhanced CV Parser Test")
    print("=" * 80)
    
    # Check if OpenAI API key is available
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print(f"✅ OpenAI API Key found (ending: ...{api_key[-8:]})")
    else:
        print("⚠️ OPENAI_API_KEY not found - will use fallback parser")
        print("   To enable AI features, add: export OPENAI_API_KEY='your-key-here'")
    
    print()
    
    # Test CV samples
    cv_samples = [
        'cv-samples/SH PM Photo v3.pdf',
        'cv-samples/SinemDemirbilekResume.pdf'
    ]
    
    parser = CVParserAI()
    
    for cv_file in cv_samples:
        if os.path.exists(cv_file):
            print(f'📄 Testing: {cv_file}')
            print('-' * 60)
            
            try:
                result = parser.parse_cv_file_enhanced(cv_file)
                
                if result.get('error'):
                    print(f'❌ Error: {result["error"]}')
                else:
                    print(f'✅ Name: {result.get("name", "N/A")}')
                    print(f'📧 Email: {result.get("email", "N/A")}')
                    print(f'📱 Phone: {result.get("phone", "N/A")}')
                    print(f'💼 Title: {result.get("title", "N/A")}')
                    
                    skills = result.get("skills", [])
                    print(f'🎯 Skills ({len(skills)}): {", ".join(skills[:8])}{"..." if len(skills) > 8 else ""}')
                    
                    languages = result.get("languages", [])
                    if languages:
                        print(f'🌐 Languages: {", ".join(languages)}')
                    
                    experience = result.get("experience", [])
                    print(f'💼 Experience: {len(experience)} entries')
                    if experience and isinstance(experience[0], dict):
                        latest = experience[0]
                        print(f'   Latest: {latest.get("title", "N/A")} at {latest.get("company", "N/A")}')
                    
                    education = result.get("education", [])
                    print(f'🎓 Education: {len(education)} entries')
                    
                    # AI-specific fields
                    projects = result.get("projects", [])
                    if projects:
                        print(f'🚀 Projects: {len(projects)} found')
                    
                    links = result.get("links", {})
                    if links:
                        print(f'🔗 Links: {", ".join([k for k, v in links.items() if v])}')
                    
                    print(f'📈 Confidence: {result.get("confidence_score", 0):.1f}%')
                    print(f'🔧 Method: {result.get("parsing_method", "unknown")}')
                    
                    if result.get("ai_confidence"):
                        print(f'🤖 AI Confidence: {result.get("ai_confidence", 0):.1f}')
                    
                    if result.get("ai_notes"):
                        print(f'📝 AI Notes: {result.get("ai_notes", "")}')
                        
            except Exception as e:
                print(f'❌ Test failed: {str(e)}')
            
            print()
    
    print("=" * 80)
    print("🏁 AI CV Parser Test Complete!")
    
    if not api_key:
        print("\n💡 To enable AI features:")
        print("   1. Get OpenAI API key from: https://platform.openai.com/api-keys")
        print("   2. Add to your environment: export OPENAI_API_KEY='sk-...'")
        print("   3. Cost: ~$0.15 per 1M tokens (very cheap for CVs)")

if __name__ == '__main__':
    test_ai_cv_parser() 