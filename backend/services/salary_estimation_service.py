import asyncio
import logging
import re
from datetime import datetime, timedelta
from statistics import mean, median
from typing import Dict, List, Optional, Tuple

from ..database.db import get_database

logger = logging.getLogger(__name__)


class SalaryEstimationService:
    def __init__(self):
        self.db = None
        self.salary_patterns = {
            "yearly": [
                r"(\d{1,3}(?:,\d{3})*)\s*(?:USD|EUR|GBP|CAD|AUD|CHF|SEK|NOK|DKK|PLN|CZK|HUF|RON|BGN|HRK|RSD|MKD|ALL|BAM|MDL|UAH|GEL|AMD|AZN|BYN|KZT|KGS|TJS|TMT|UZS|MNT|LAK|KHR|MMK|THB|VND|IDR|MYR|SGD|BND|PHP|INR|PKR|BDT|LKR|NPR|BTN|MVR|AED|QAR|SAR|OMR|KWD|BHD|JOD|ILS|EGP|LYD|TND|DZD|MAD|MRO|XOF|XAF|XPF|GHS|NGN|KES|UGX|TZS|MWK|ZMW|ZAR|BWP|NAD|SZL|LSL|MUR|SCR|KMF|DJF|ETB|SOS|SDG|SSP|CDF|RWF|BIF|GMD|GNF|SLL|LRD|SLE|GIP|FKP|SHP|AOA|STD|CVE|GQE|XCD|BBD|TTD|JMD|HTG|GYD|SRD|BZD|BMD|KYD|AWG|ANG|XPF|TOP|WST|FJD|VUV|SBD|PGK)",
                r"(\d{1,3}(?:,\d{3})*)\s*(?:USD|EUR|GBP|CAD|AUD|CHF|SEK|NOK|DKK|PLN|CZK|HUF|RON|BGN|HRK|RSD|MKD|ALL|BAM|MDL|UAH|GEL|AMD|AZN|BYN|KZT|KGS|TJS|TMT|UZS|MNT|LAK|KHR|MMK|THB|VND|IDR|MYR|SGD|BND|PHP|INR|PKR|BDT|LKR|NPR|BTN|MVR|AED|QAR|SAR|OMR|KWD|BHD|JOD|ILS|EGP|LYD|TND|DZD|MAD|MRO|XOF|XAF|XPF|GHS|NGN|KES|UGX|TZS|MWK|ZMW|ZAR|BWP|NAD|SZL|LSL|MUR|SCR|KMF|DJF|ETB|SOS|SDG|SSP|CDF|RWF|BIF|GMD|GNF|SLL|LRD|SLE|GIP|FKP|SHP|AOA|STD|CVE|GQE|XCD|BBD|TTD|JMD|HTG|GYD|SRD|BZD|BMD|KYD|AWG|ANG|XPF|TOP|WST|FJD|VUV|SBD|PGK)\s*(?:salary|compensation)",
                r"(\d{1,3}(?:,\d{3})*)\s*(?:USD|EUR|GBP|CAD|AUD|CHF|SEK|NOK|DKK|PLN|CZK|HUF|RON|BGN|HRK|RSD|MKD|ALL|BAM|MDL|UAH|GEL|AMD|AZN|BYN|KZT|KGS|TJS|TMT|UZS|MNT|LAK|KHR|MMK|THB|VND|IDR|MYR|SGD|BND|PHP|INR|PKR|BDT|LKR|NPR|BTN|MVR|AED|QAR|SAR|OMR|KWD|BHD|JOD|ILS|EGP|LYD|TND|DZD|MAD|MRO|XOF|XAF|XPF|GHS|NGN|KES|UGX|TZS|MWK|ZMW|ZAR|BWP|NAD|SZL|LSL|MUR|SCR|KMF|DJF|ETB|SOS|SDG|SSP|CDF|RWF|BIF|GMD|GNF|SLL|LRD|SLE|GIP|FKP|SHP|AOA|STD|CVE|GQE|XCD|BBD|TTD|JMD|HTG|GYD|SRD|BZD|BMD|KYD|AWG|ANG|XPF|TOP|WST|FJD|VUV|SBD|PGK)",
            ],
            "monthly": [
                r"(\d{1,3}(?:,\d{3})*)\s*(?:USD|EUR|GBP|CAD|AUD|CHF|SEK|NOK|DKK|PLN|CZK|HUF|RON|BGN|HRK|RSD|MKD|ALL|BAM|MDL|UAH|GEL|AMD|AZN|BYN|KZT|KGS|TJS|TMT|UZS|MNT|LAK|KHR|MMK|THB|VND|IDR|MYR|SGD|BND|PHP|INR|PKR|BDT|LKR|NPR|BTN|MVR|AED|QAR|SAR|OMR|KWD|BHD|JOD|ILS|EGP|LYD|TND|DZD|MAD|MRO|XOF|XAF|XPF|GHS|NGN|KES|UGX|TZS|MWK|ZMW|ZAR|BWP|NAD|SZL|LSL|MUR|SCR|KMF|DJF|ETB|SOS|SDG|SSP|CDF|RWF|BIF|GMD|GNF|SLL|LRD|SLE|GIP|FKP|SHP|AOA|STD|CVE|GQE|XCD|BBD|TTD|JMD|HTG|GYD|SRD|BZD|BMD|KYD|AWG|ANG|XPF|TOP|WST|FJD|VUV|SBD|PGK)\s*(?:per\s*month|monthly|mo|month)",
            ],
            "hourly": [
                r"(\d{1,3}(?:,\d{3})*)\s*(?:USD|EUR|GBP|CAD|AUD|CHF|SEK|NOK|DKK|PLN|CZK|HUF|RON|BGN|HRK|RSD|MKD|ALL|BAM|MDL|UAH|GEL|AMD|AZN|BYN|KZT|KGS|TJS|TMT|UZS|MNT|LAK|KHR|MMK|THB|VND|IDR|MYR|SGD|BND|PHP|INR|PKR|BDT|LKR|NPR|BTN|MVR|AED|QAR|SAR|OMR|KWD|BHD|JOD|ILS|EGP|LYD|TND|DZD|MAD|MRO|XOF|XAF|XPF|GHS|NGN|KES|UGX|TZS|MWK|ZMW|ZAR|BWP|NAD|SZL|LSL|MUR|SCR|KMF|DJF|ETB|SOS|SDG|SSP|CDF|RWF|BIF|GMD|GNF|SLL|LRD|SLE|GIP|FKP|SHP|AOA|STD|CVE|GQE|XCD|BBD|TTD|JMD|HTG|GYD|SRD|BZD|BMD|KYD|AWG|ANG|XPF|TOP|WST|FJD|VUV|SBD|PGK)\s*(?:per\s*hour|hourly|hr|hour)",
            ],
        }

        # Maaş aralığı kalıpları
        self.range_patterns = [
            r"(\d{1,3}(?:,\d{3})*)\s*-\s*(\d{1,3}(?:,\d{3})*)\s*(?:USD|EUR|GBP|CAD|AUD|CHF|SEK|NOK|DKK|PLN|CZK|HUF|RON|BGN|HRK|RSD|MKD|ALL|BAM|MDL|UAH|GEL|AMD|AZN|BYN|KZT|KGS|TJS|TMT|UZS|MNT|LAK|KHR|MMK|THB|VND|IDR|MYR|SGD|BND|PHP|INR|PKR|BDT|LKR|NPR|BTN|MVR|AED|QAR|SAR|OMR|KWD|BHD|JOD|ILS|EGP|LYD|TND|DZD|MAD|MRO|XOF|XAF|XPF|GHS|NGN|KES|UGX|TZS|MWK|ZMW|ZAR|BWP|NAD|SZL|LSL|MUR|SCR|KMF|DJF|ETB|SOS|SDG|SSP|CDF|RWF|BIF|GMD|GNF|SLL|LRD|SLE|GIP|FKP|SHP|AOA|STD|CVE|GQE|XCD|BBD|TTD|JMD|HTG|GYD|SRD|BZD|BMD|KYD|AWG|ANG|XPF|TOP|WST|FJD|VUV|SBD|PGK)",
            r"(\d{1,3}(?:,\d{3})*)\s*to\s*(\d{1,3}(?:,\d{3})*)\s*(?:USD|EUR|GBP|CAD|AUD|CHF|SEK|NOK|DKK|PLN|CZK|HUF|RON|BGN|HRK|RSD|MKD|ALL|BAM|MDL|UAH|GEL|AMD|AZN|BYN|KZT|KGS|TJS|TMT|UZS|MNT|LAK|KHR|MMK|THB|VND|IDR|MYR|SGD|BND|PHP|INR|PKR|BDT|LKR|NPR|BTN|MVR|AED|QAR|SAR|OMR|KWD|BHD|JOD|ILS|EGP|LYD|TND|DZD|MAD|MRO|XOF|XAF|XPF|GHS|NGN|KES|UGX|TZS|MWK|ZMW|ZAR|BWP|NAD|SZL|LSL|MUR|SCR|KMF|DJF|ETB|SOS|SDG|SSP|CDF|RWF|BIF|GMD|GNF|SLL|LRD|SLE|GIP|FKP|SHP|AOA|STD|CVE|GQE|XCD|BBD|TTD|JMD|HTG|GYD|SRD|BZD|BMD|KYD|AWG|ANG|XPF|TOP|WST|FJD|VUV|SBD|PGK)",
        ]

    async def initialize(self):
        """Veritabanı bağlantısını başlat"""
        if not self.db:
            self.db = await get_database()

    def extract_salary_from_text(self, text: str) -> Optional[Dict]:
        """Metinden maaş bilgisini çıkar"""
        if not text:
            return None

        text_lower = text.lower()

        # Maaş aralığı kontrolü
        for pattern in self.range_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                min_salary = int(match.group(1).replace(",", ""))
                max_salary = int(match.group(2).replace(",", ""))
                currency = self._extract_currency(text[match.start() : match.end()])
                period = self._determine_period(text_lower)

                return {
                    "min_salary": min_salary,
                    "max_salary": max_salary,
                    "currency": currency,
                    "period": period,
                    "is_range": True,
                }

        # Tek maaş kontrolü
        for period, patterns in self.salary_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    salary = int(match.group(1).replace(",", ""))
                    currency = self._extract_currency(text[match.start() : match.end()])

                    return {
                        "min_salary": salary,
                        "max_salary": salary,
                        "currency": currency,
                        "period": period,
                        "is_range": False,
                    }

        return None

    def _extract_currency(self, text: str) -> str:
        """Metinden para birimini çıkar"""
        currencies = [
            "USD",
            "EUR",
            "GBP",
            "CAD",
            "AUD",
            "CHF",
            "SEK",
            "NOK",
            "DKK",
            "PLN",
            "CZK",
            "HUF",
            "RON",
            "BGN",
            "HRK",
            "RSD",
            "MKD",
            "ALL",
            "BAM",
            "MDL",
            "UAH",
            "GEL",
            "AMD",
            "AZN",
            "BYN",
            "KZT",
            "KGS",
            "TJS",
            "TMT",
            "UZS",
            "MNT",
            "LAK",
            "KHR",
            "MMK",
            "THB",
            "VND",
            "IDR",
            "MYR",
            "SGD",
            "BND",
            "PHP",
            "INR",
            "PKR",
            "BDT",
            "LKR",
            "NPR",
            "BTN",
            "MVR",
            "AED",
            "QAR",
            "SAR",
            "OMR",
            "KWD",
            "BHD",
            "JOD",
            "ILS",
            "EGP",
            "LYD",
            "TND",
            "DZD",
            "MAD",
            "MRO",
            "XOF",
            "XAF",
            "XPF",
            "GHS",
            "NGN",
            "KES",
            "UGX",
            "TZS",
            "MWK",
            "ZMW",
            "ZAR",
            "BWP",
            "NAD",
            "SZL",
            "LSL",
            "MUR",
            "SCR",
            "KMF",
            "DJF",
            "ETB",
            "SOS",
            "SDG",
            "SSP",
            "CDF",
            "RWF",
            "BIF",
            "GMD",
            "GNF",
            "SLL",
            "LRD",
            "SLE",
            "GIP",
            "FKP",
            "SHP",
            "AOA",
            "STD",
            "CVE",
            "GQE",
            "XCD",
            "BBD",
            "TTD",
            "JMD",
            "HTG",
            "GYD",
            "SRD",
            "BZD",
            "BMD",
            "KYD",
            "AWG",
            "ANG",
            "XPF",
            "TOP",
            "WST",
            "FJD",
            "VUV",
            "SBD",
            "PGK",
        ]

        for currency in currencies:
            if currency in text.upper():
                return currency

        return "USD"  # Varsayılan

    def _determine_period(self, text: str) -> str:
        """Maaş periyodunu belirle"""
        if any(
            word in text for word in ["yearly", "annual", "annually", "per year", "yr"]
        ):
            return "yearly"
        elif any(word in text for word in ["monthly", "per month", "mo", "month"]):
            return "monthly"
        elif any(word in text for word in ["hourly", "per hour", "hr", "hour"]):
            return "hourly"
        else:
            return "yearly"  # Varsayılan

    def normalize_salary_to_yearly(self, salary: int, period: str) -> int:
        """Maaşı yıllık bazda normalize et"""
        if period == "yearly":
            return salary
        elif period == "monthly":
            return salary * 12
        elif period == "hourly":
            return salary * 40 * 52  # Haftada 40 saat, 52 hafta
        else:
            return salary

    def normalize_salary_from_yearly(self, salary: int, target_period: str) -> int:
        """Yıllık maaşı hedef periyoda çevir"""
        if target_period == "yearly":
            return salary
        elif target_period == "monthly":
            return salary // 12
        elif target_period == "hourly":
            return salary // (40 * 52)  # Haftada 40 saat, 52 hafta
        else:
            return salary

    async def find_similar_jobs(
        self,
        job_title: str,
        location: str = None,
        company_size: str = None,
        experience_level: str = None,
    ) -> List[Dict]:
        """Benzer işleri bul"""
        if self.db is None:
            await self.initialize()

        # Arama kriterleri
        search_criteria = {
            "salary_min": {"$exists": True, "$ne": None},
            "salary_max": {"$exists": True, "$ne": None},
        }

        # Job title benzerliği
        if job_title:
            # Anahtar kelimeleri çıkar
            keywords = self._extract_keywords(job_title)
            if keywords:
                search_criteria["$or"] = [
                    {"title": {"$regex": keyword, "$options": "i"}}
                    for keyword in keywords
                ]

        # Location filtresi
        if location:
            search_criteria["location"] = {"$regex": location, "$options": "i"}

        # Company size filtresi
        if company_size:
            search_criteria["company_size"] = company_size

        # Experience level filtresi
        if experience_level:
            search_criteria["experience_level"] = experience_level

        try:
            # Benzer işleri bul
            similar_jobs = (
                await self.db.jobs.find(search_criteria).limit(50).to_list(50)
            )

            # Maaş bilgisi olan işleri filtrele
            jobs_with_salary = []
            for job in similar_jobs:
                if job.get("salary_min") and job.get("salary_max"):
                    jobs_with_salary.append(job)

            return jobs_with_salary

        except Exception as e:
            logger.error(f"Error finding similar jobs: {e}")
            return []

    def _extract_keywords(self, job_title: str) -> List[str]:
        """İş başlığından anahtar kelimeleri çıkar"""
        # Yaygın kelimeleri kaldır
        stop_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "being",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "must",
            "can",
            "this",
            "that",
            "these",
            "those",
            "i",
            "you",
            "he",
            "she",
            "it",
            "we",
            "they",
            "me",
            "him",
            "her",
            "us",
            "them",
            "my",
            "your",
            "his",
            "her",
            "its",
            "our",
            "their",
            "mine",
            "yours",
            "his",
            "hers",
            "ours",
            "theirs",
            "who",
            "whom",
            "whose",
            "which",
            "what",
            "where",
            "when",
            "why",
            "how",
            "all",
            "any",
            "both",
            "each",
            "few",
            "more",
            "most",
            "other",
            "some",
            "such",
            "no",
            "nor",
            "not",
            "only",
            "own",
            "same",
            "so",
            "than",
            "too",
            "very",
            "s",
            "t",
            "can",
            "will",
            "just",
            "don",
            "should",
            "now",
            "d",
            "ll",
            "m",
            "o",
            "re",
            "ve",
            "y",
            "ain",
            "aren",
            "couldn",
            "didn",
            "doesn",
            "hadn",
            "hasn",
            "haven",
            "isn",
            "ma",
            "mightn",
            "mustn",
            "needn",
            "shan",
            "shouldn",
            "wasn",
            "weren",
            "won",
            "wouldn",
        }

        # Kelimeleri ayır ve temizle
        words = re.findall(r"\b[a-zA-Z]+\b", job_title.lower())
        keywords = [word for word in words if word not in stop_words and len(word) > 2]

        return keywords[:5]  # En fazla 5 anahtar kelime

    async def estimate_salary(
        self,
        job_title: str,
        location: str = None,
        company_size: str = None,
        experience_level: str = None,
    ) -> Optional[Dict]:
        """Maaş tahmini yap"""
        try:
            # Benzer işleri bul
            similar_jobs = await self.find_similar_jobs(
                job_title, location, company_size, experience_level
            )

            if not similar_jobs:
                logger.warning(f"No similar jobs found for: {job_title}")
                return None

            # Maaş verilerini topla
            salaries = []
            for job in similar_jobs:
                min_salary = job.get("salary_min")
                max_salary = job.get("salary_max")
                currency = job.get("salary_currency", "USD")

                if min_salary and max_salary:
                    # Maaşları yıllık bazda normalize et
                    normalized_min = self.normalize_salary_to_yearly(
                        min_salary, job.get("salary_period", "yearly")
                    )
                    normalized_max = self.normalize_salary_to_yearly(
                        max_salary, job.get("salary_period", "yearly")
                    )

                    # Ortalama maaş
                    avg_salary = (normalized_min + normalized_max) / 2
                    salaries.append(
                        {
                            "salary": avg_salary,
                            "currency": currency,
                            "min": normalized_min,
                            "max": normalized_max,
                        }
                    )

            if not salaries:
                return None

            # İstatistiksel analiz
            salary_values = [s["salary"] for s in salaries]
            currencies = [s["currency"] for s in salaries]

            # En yaygın para birimi
            most_common_currency = max(set(currencies), key=currencies.count)

            # Aynı para birimindeki maaşları filtrele
            same_currency_salaries = [
                s for s in salaries if s["currency"] == most_common_currency
            ]

            if not same_currency_salaries:
                return None

            salary_values_same_currency = [s["salary"] for s in same_currency_salaries]

            # İstatistikler
            mean_salary = mean(salary_values_same_currency)
            median_salary = median(salary_values_same_currency)

            # Aykırı değerleri filtrele (Q1 - 1.5*IQR ve Q3 + 1.5*IQR)
            sorted_salaries = sorted(salary_values_same_currency)
            q1 = sorted_salaries[len(sorted_salaries) // 4]
            q3 = sorted_salaries[3 * len(sorted_salaries) // 4]
            iqr = q3 - q1

            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr

            filtered_salaries = [
                s
                for s in salary_values_same_currency
                if lower_bound <= s <= upper_bound
            ]

            if filtered_salaries:
                final_mean = mean(filtered_salaries)
                final_median = median(filtered_salaries)

                # Güven aralığı hesapla
                confidence_interval = 0.15  # %15 güven aralığı
                min_estimate = int(final_mean * (1 - confidence_interval))
                max_estimate = int(final_mean * (1 + confidence_interval))

                return {
                    "min_salary": min_estimate,
                    "max_salary": max_estimate,
                    "currency": most_common_currency,
                    "period": "yearly",
                    "is_estimated": True,
                    "confidence_score": self._calculate_confidence_score(
                        len(filtered_salaries), len(similar_jobs)
                    ),
                    "data_points": len(filtered_salaries),
                    "similar_jobs_count": len(similar_jobs),
                    "mean_salary": int(final_mean),
                    "median_salary": int(final_median),
                }

            return None

        except Exception as e:
            logger.error(f"Error estimating salary: {e}")
            return None

    def _calculate_confidence_score(self, data_points: int, total_jobs: int) -> float:
        """Güven skoru hesapla (0-1 arası)"""
        # Veri noktası sayısına göre güven skoru
        if data_points >= 20:
            base_score = 0.9
        elif data_points >= 10:
            base_score = 0.8
        elif data_points >= 5:
            base_score = 0.7
        elif data_points >= 3:
            base_score = 0.6
        else:
            base_score = 0.5

        # Benzer iş sayısına göre düzeltme
        if total_jobs >= 50:
            adjustment = 0.1
        elif total_jobs >= 20:
            adjustment = 0.05
        else:
            adjustment = 0

        return min(1.0, base_score + adjustment)

    async def process_job_salary(self, job_data: Dict) -> Dict:
        """İş verisini işle ve maaş bilgisini ekle"""
        # Mevcut maaş bilgisi kontrolü
        if job_data.get("salary_min") and job_data.get("salary_max"):
            return job_data

        # Maaş bilgisini metinden çıkar
        description = job_data.get("description", "")
        salary_info = self.extract_salary_from_text(description)

        if salary_info:
            # Maaş bilgisini job_data'ya ekle
            job_data.update(
                {
                    "salary_min": salary_info["min_salary"],
                    "salary_max": salary_info["max_salary"],
                    "salary_currency": salary_info["currency"],
                    "salary_period": salary_info["period"],
                    "is_estimated": False,
                }
            )
        else:
            # Maaş tahmini yap
            estimated_salary = await self.estimate_salary(
                job_data.get("title", ""),
                job_data.get("location"),
                job_data.get("company_size"),
                job_data.get("experience_level"),
            )

            if estimated_salary:
                job_data.update(
                    {
                        "salary_min": estimated_salary["min_salary"],
                        "salary_max": estimated_salary["max_salary"],
                        "salary_currency": estimated_salary["currency"],
                        "salary_period": estimated_salary["period"],
                        "is_estimated": True,
                        "salary_confidence": estimated_salary["confidence_score"],
                        "salary_data_points": estimated_salary["data_points"],
                    }
                )

        return job_data


# Global servis instance
salary_estimation_service = SalaryEstimationService()
