from bs4 import BeautifulSoup
import requests
import logging
from typing import List, Dict, Optional
import re
from urllib.parse import urljoin

class SelectorValidator:
    COMMON_JOB_PATTERNS = [
        r'job', r'career', r'position', r'opening', r'role',
        r'vacancy', r'opportunities', r'listing'
    ]
    
    COMMON_SELECTORS = {
        'lever.co': {
            'primary': '.content .section-wrapper',
            'fallbacks': ['.postings-group', '.job-listing']
        },
        'greenhouse.io': {
            'primary': '#main',
            'fallbacks': ['.opening', '.job-listing']
        },
        'breezy.hr': {
            'primary': '.portal-content',
            'fallbacks': ['.positions', '.job-listings']
        }
    }

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def validate_selector(self, url: str, current_selector: str) -> Optional[str]:
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Mevcut seçici çalışıyor mu kontrol et
            elements = soup.select(current_selector)
            if elements and self._contains_job_content(elements):
                return current_selector
                
            # Çalışmıyorsa, platform bazlı yedek seçicileri dene
            platform = self._detect_platform(url)
            if platform and platform in self.COMMON_SELECTORS:
                for selector in [self.COMMON_SELECTORS[platform]['primary']] + self.COMMON_SELECTORS[platform]['fallbacks']:
                    elements = soup.select(selector)
                    if elements and self._contains_job_content(elements):
                        return selector
            
            # Platform bazlı seçiciler çalışmadıysa, otomatik keşif yap
            return self._discover_job_section(soup)
            
        except Exception as e:
            self.logger.error(f"Error validating selector for {url}: {str(e)}")
            return None

    def _contains_job_content(self, elements: List) -> bool:
        """Bulunan elementlerin iş ilanı içeriği olup olmadığını kontrol et"""
        text = ' '.join(element.get_text().lower() for element in elements)
        return any(re.search(pattern, text) for pattern in self.COMMON_JOB_PATTERNS)

    def _detect_platform(self, url: str) -> Optional[str]:
        """URL'den iş ilanı platformunu tespit et"""
        for platform in self.COMMON_SELECTORS.keys():
            if platform in url:
                return platform
        return None

    def _discover_job_section(self, soup: BeautifulSoup) -> Optional[str]:
        """Sayfada iş ilanlarının olduğu bölümü otomatik keşfet"""
        # ID ve class'larda iş ilanı ile ilgili anahtar kelimeleri ara
        potential_selectors = []
        
        for element in soup.find_all(class_=True):
            classes = ' '.join(element.get('class'))
            if any(pattern in classes.lower() for pattern in self.COMMON_JOB_PATTERNS):
                selector = self._generate_selector(element)
                potential_selectors.append(selector)

        for element in soup.find_all(id=True):
            if any(pattern in element.get('id').lower() for pattern in self.COMMON_JOB_PATTERNS):
                selector = self._generate_selector(element)
                potential_selectors.append(selector)

        # En uygun seçiciyi seç
        for selector in potential_selectors:
            elements = soup.select(selector)
            if elements and self._contains_job_content(elements):
                return selector

        return None

    def _generate_selector(self, element) -> str:
        """Element için CSS seçici oluştur"""
        if element.get('id'):
            return f"#{element['id']}"
        elif element.get('class'):
            return f".{'.'.join(element['class'])}"
        return element.name 