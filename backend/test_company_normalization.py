#!/usr/bin/env python3

import sys
import os
import asyncio
import re
from datetime import datetime

# Add paths
sys.path.append('/Users/sarperhorata/buzz2remote')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the enhanced normalization function
from company_website_enricher import CompanyWebsiteEnricher

class CompanyNormalizationTester:
    def __init__(self):
        self.enricher = CompanyWebsiteEnricher()
        # Test cases from the actual 230 failed companies
        self.test_cases = [
            # Direct examples from the error list
            "Clerky Jobs",
            "The Democratic Party", 
            "Openings at PADI Travel",
            "Openings at Dotsub",
            "Openings at Parashift",
            "Openings at Connected Women",
            "15Five Careers",
            "Heetch Jobs",
            "Girls Who Code",
            "Kraken Digital Asset Exchange",
            "Careers at Adioma",
            "Jobs at Cameo",
            "Openings at Dollar Flight Club",
            "Jobs at Bevy",
            "Eight Sleep Jobs",
            "Work at Metabase",
            "Şurada açılan kadrolar: CVEDIA",
            "Careers – Run the World Digital",
            "BrandBastion - Current Openings",
            "Şurada açılan kadrolar: JAUMO",
            "Careers at Realm",
            "Join Our Team",
            "Find your team | Ookla®",
            "Careers at Exit Bee - Current Job Openings at a growing ad tech startup",
            "Dutchie | Cannabis Technology Careers",
            "Search Peloton Jobs | Peloton®",
            "Work at Close | 100% Remote SaaS Jobs",
            "Jobs — Working at Balsamiq | Balsamiq",
            "Student Loan Hero - Current Openings",
            "Jobs at SafetyWing | SafetyWing Careers",
            "Open Positions – Sysdig",
            "Jobs at Sourcegraph",
            "Remote SaaS Jobs - SureSwift Capital, Inc.",
            "Şurada açılan kadrolar: Remote Year",
            "We're Hiring! - Linear",
            "Come help us change the future of financing. See open jobs.",
            "Careers at Bird (formerly MessageBird)",
            "Work at Teleport | Teleport",
            "Come work with us - HelpDocs",
            "Join the Buffer journey - Jobs @ Buffer",
            "Come help us change the future of financing. See open jobs.",
            "Jobs at Kit",
            "Jobs at Livestorm - join the future of video engagement",
            "Careers at Hypothesis | Join Our Team",
            "Ahrefs'te Kariyer",
            "Jobs at Big Cartel",
            "DuckDuckGo is Hiring!",
            "Current job openings - OTO",
            "Ceros jobs | Ceros openings | Ceros careers",
            "Latest Job Openings - Join Omnipresent",
            "Jobs at Thesis*",
            "Jobs at InCharge Energy",
            "Jobs at Tailor | Y Combinator",
            "Aircall Jobs | Aircall",
            "Careers at OffSec | OffSec Jobs",
            "Careers for Problem-Solvers | Invisible Technologies",
            "Find your career at DISCO",
            "Şurada açılan kadrolar: BAD Marketing",
            "Vacancies / Social Discovery Group",
            "Şurada açılan kadrolar: GAMURS Group",
            "Alpaca - We're Hiring! Find Your Next Career Role",
            "Work at Codeway",
            "Careers with Bitwarden | Bitwarden",
            "Join the Circle team",
            "Jobs at Roadie",
            "Jobs at GiveDirectly",
            "Epic Games Careers, Jobs and Employment Opportunity - Epic Games",
            "Jobs at Beyond Finance",
            "Jobs at Garner Health",
            "Jobs at Axios",
            "Jobs at eClinical Solutions",
            "Job Openings – Innovative Minds Needed",
            "Jobs at Downing Capital Group",
            "Offene Stellen | Flip",
            "Jobs at Product People",
            "Jobs at Fulfil Solutions",
            "Jobs at Atomic",
            "Pleo Careers: We're building the go-to spending platform for forward-thinking teams - Pleo",
            "Join Us - Welcome | Blue River Technology",
            "Jobs at WOO X",
        ]
        
        # Expected results (what we want to extract as company names)
        self.expected_results = {
            "Clerky Jobs": ["Clerky"],
            "The Democratic Party": ["Democratic Party", "DNC"],
            "Openings at PADI Travel": ["PADI Travel", "PADI"],
            "15Five Careers": ["15Five"],
            "Heetch Jobs": ["Heetch"],
            "Jobs at Cameo": ["Cameo"],
            "Work at Metabase": ["Metabase"],
            "Şurada açılan kadrolar: CVEDIA": ["CVEDIA"],
            "Jobs at Bevy": ["Bevy"],
            "Jobs at Big Cartel": ["Big Cartel"],
            "DuckDuckGo is Hiring!": ["DuckDuckGo"],
            "Aircall Jobs | Aircall": ["Aircall"],
            "Work at Codeway": ["Codeway"],
        }

    def test_normalization(self):
        """Test the enhanced normalization function"""
        print("🧪 TESTING ENHANCED COMPANY NAME NORMALIZATION")
        print("=" * 60)
        
        total_tests = len(self.test_cases)
        successful_extractions = 0
        
        for i, test_case in enumerate(self.test_cases, 1):
            print(f"\n{i:2d}. Testing: '{test_case}'")
            
            # Get normalized variations
            variations = self.enricher.normalize_company_name(test_case)
            
            print(f"    Variations ({len(variations)}): {variations[:5]}{'...' if len(variations) > 5 else ''}")
            
            # Check if we have good extractions
            has_good_extraction = False
            expected = self.expected_results.get(test_case, [])
            
            if expected:
                # Check if any expected result is in variations
                for exp in expected:
                    if any(exp.lower() in var.lower() or var.lower() in exp.lower() for var in variations):
                        has_good_extraction = True
                        print(f"    ✅ Found expected: {exp}")
                        break
                
                if not has_good_extraction:
                    print(f"    ❌ Expected: {expected}, but got: {variations[:3]}")
            else:
                # For cases without expected results, check if we extracted something reasonable
                reasonable_variations = []
                for var in variations[:3]:
                    # Skip if it's just the original or too similar to original
                    if (var != test_case and 
                        len(var) >= 3 and len(var) <= 30 and
                        not any(word in var.lower() for word in ['jobs', 'careers', 'hiring', 'openings', 'current'])):
                        reasonable_variations.append(var)
                
                if reasonable_variations:
                    has_good_extraction = True
                    print(f"    ✅ Reasonable extractions: {reasonable_variations}")
                else:
                    print(f"    ⚠️  No clear company name extracted")
            
            if has_good_extraction:
                successful_extractions += 1
        
        success_rate = (successful_extractions / total_tests) * 100
        
        print(f"\n" + "=" * 60)
        print(f"📊 TEST RESULTS:")
        print(f"Total test cases: {total_tests}")
        print(f"Successful extractions: {successful_extractions}")
        print(f"Success rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print(f"🎉 EXCELLENT! Success rate is {success_rate:.1f}% (Target: 80%+)")
        elif success_rate >= 70:
            print(f"✅ GOOD! Success rate is {success_rate:.1f}% (Target: 80%+)")
        else:
            print(f"⚠️  NEEDS IMPROVEMENT! Success rate is {success_rate:.1f}% (Target: 80%+)")
        
        return success_rate

    def test_specific_patterns(self):
        """Test specific problematic patterns"""
        print(f"\n🔍 TESTING SPECIFIC PROBLEMATIC PATTERNS")
        print("-" * 50)
        
        specific_tests = [
            ("Clerky Jobs", "Clerky"),
            ("Jobs at Cameo", "Cameo"), 
            ("Openings at PADI Travel", "PADI Travel"),
            ("The Democratic Party", "Democratic Party"),
            ("15Five Careers", "15Five"),
            ("Work at Metabase", "Metabase"),
            ("Şurada açılan kadrolar: CVEDIA", "CVEDIA"),
            ("DuckDuckGo is Hiring!", "DuckDuckGo"),
            ("We're Hiring! - Linear", "Linear"),
            ("Join Our Team", None),  # This should be filtered out
        ]
        
        for test_input, expected in specific_tests:
            variations = self.enricher.normalize_company_name(test_input)
            
            if expected:
                # Check if expected result is in variations
                found = any(expected.lower() in var.lower() or var.lower() in expected.lower() for var in variations)
                status = "✅" if found else "❌"
                print(f"{status} '{test_input}' → Expected: '{expected}' | Got: {variations[:3]}")
            else:
                # Should be filtered out or minimal variations
                status = "✅" if len([v for v in variations if len(v) > 3]) <= 2 else "❌"
                print(f"{status} '{test_input}' → Should be filtered | Got: {variations[:3]}")

def main():
    """Run all tests"""
    tester = CompanyNormalizationTester()
    
    # Run main normalization test
    success_rate = tester.test_normalization()
    
    # Run specific pattern tests
    tester.test_specific_patterns()
    
    print(f"\n🎯 OVERALL ASSESSMENT:")
    if success_rate >= 80:
        print("✅ Enhanced normalization is ready for production!")
        print("🚀 Expected improvement: 52% → 85%+ success rate")
    else:
        print("⚠️  Enhanced normalization needs more work")
        print("🔧 Consider adding fuzzy matching or more patterns")

if __name__ == "__main__":
    main() 