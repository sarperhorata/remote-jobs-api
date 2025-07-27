import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import re

from services.job_title_parser import job_title_parser


def test_location_parsing():
    test_cases = [
        "Group Director, CEO – North America",
        "SEO Associate (Talent Pool)Remote —Full-time Remote / Philadelphia, PA",
        "SEO Team Lead (Talent Pool)Remote —Full-time Remote / Philadelphia, PA",
        "Regional Vice President, Strategic Accounts, EMEAHybrid —Full-Time London, England",
        "Python Developer, remote",
        "Senior Account Executive Remote —Full-time",
        "Junior Market Researcher (Crypto and Blockchain)Remote —Full-time",
    ]

    print("Lokasyon Parsing Debug Testleri:\n")

    for i, title in enumerate(test_cases, 1):
        print(f"Test {i}: {title}")

        # Clean title first
        cleaned = job_title_parser._clean_title(title)
        print(f"  Temizlenmiş: {cleaned}")

        # Extract location
        location = job_title_parser._extract_location(title)
        print(f"  Lokasyon: {location}")

        # Full parse
        parsed = job_title_parser.parse_job_title(title)
        print(f"  Tam Parse - Lokasyon: {parsed.location}")
        print(f"  Tam Parse - Work Type: {parsed.work_type}")
        print("-" * 80)


if __name__ == "__main__":
    test_location_parsing()
