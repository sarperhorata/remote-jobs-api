import logging
import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class ParsedJobTitle:
    original_title: str
    parsed_title: str
    category: str
    level: str
    skills: List[str]
    location: Optional[str]
    work_type: Optional[str]
    department: Optional[str]


class JobTitleParser:
    """Job title parsing and categorization service"""

    def __init__(self):
        # Job categories with keywords
        self.categories = {
            "Technology": [
                "developer",
                "engineer",
                "programmer",
                "coder",
                "architect",
                "devops",
                "sre",
                "data scientist",
                "machine learning",
                "ai",
                "ml",
                "analyst",
                "qa",
                "test",
                "frontend",
                "backend",
                "full stack",
                "mobile",
                "ios",
                "android",
                "web",
                "software",
                "hardware",
                "system",
                "network",
                "security",
                "cyber",
                "cloud",
                "aws",
                "azure",
                "gcp",
                "database",
                "sql",
                "nosql",
            ],
            "Management": [
                "manager",
                "director",
                "head",
                "lead",
                "chief",
                "vp",
                "c-level",
                "executive",
                "supervisor",
                "coordinator",
                "administrator",
                "superintendent",
            ],
            "Design": [
                "designer",
                "ux",
                "ui",
                "graphic",
                "visual",
                "creative",
                "art",
                "brand",
                "illustrator",
                "animator",
                "photographer",
                "video",
                "motion",
            ],
            "Marketing": [
                "marketing",
                "growth",
                "seo",
                "sem",
                "ppc",
                "social media",
                "content",
                "brand",
                "advertising",
                "campaign",
                "analytics",
                "digital marketing",
            ],
            "Sales": [
                "sales",
                "account",
                "business development",
                "revenue",
                "partnership",
                "customer success",
                "client",
                "territory",
                "inside sales",
                "outside sales",
            ],
            "Finance": [
                "finance",
                "accounting",
                "controller",
                "treasurer",
                "auditor",
                "analyst",
                "investment",
                "banking",
                "risk",
                "compliance",
                "tax",
            ],
            "HR": [
                "hr",
                "human resources",
                "recruiter",
                "talent",
                "people",
                "benefits",
                "compensation",
                "training",
                "development",
                "diversity",
                "inclusion",
            ],
            "Operations": [
                "operations",
                "logistics",
                "supply chain",
                "procurement",
                "vendor",
                "facilities",
                "maintenance",
                "quality",
                "process",
                "efficiency",
            ],
            "Customer Service": [
                "customer service",
                "support",
                "help desk",
                "technical support",
                "client relations",
                "customer experience",
                "service desk",
            ],
            "Legal": [
                "legal",
                "lawyer",
                "attorney",
                "counsel",
                "paralegal",
                "compliance",
                "regulatory",
                "contract",
                "intellectual property",
                "litigation",
            ],
        }

        # Job levels
        self.levels = {
            "entry": [
                "junior",
                "jr",
                "entry",
                "associate",
                "assistant",
                "trainee",
                "intern",
            ],
            "mid": ["mid", "intermediate", "regular", "standard"],
            "senior": ["senior", "sr", "lead", "principal", "staff"],
            "executive": ["executive", "director", "head", "chief", "vp", "c-level"],
        }

        # Level keywords to preserve in title
        self.level_keywords = [
            "senior",
            "sr",
            "junior",
            "jr",
            "lead",
            "principal",
            "staff",
        ]

        # Common skills to extract
        self.skills = [
            "javascript",
            "python",
            "java",
            "react",
            "node",
            "angular",
            "vue",
            "typescript",
            "php",
            "ruby",
            "go",
            "rust",
            "kotlin",
            "swift",
            "c++",
            "c#",
            "sql",
            "mongodb",
            "postgresql",
            "mysql",
            "redis",
            "docker",
            "kubernetes",
            "aws",
            "azure",
            "gcp",
            "git",
            "jenkins",
            "jira",
            "figma",
            "sketch",
            "adobe",
            "photoshop",
            "illustrator",
        ]

        # Work types
        self.work_types = [
            "remote",
            "hybrid",
            "on-site",
            "full-time",
            "part-time",
            "contract",
            "freelance",
        ]

        # Common departments
        self.departments = [
            "engineering",
            "product",
            "marketing",
            "sales",
            "finance",
            "hr",
            "operations",
            "legal",
            "customer service",
            "design",
            "data",
            "security",
            "devops",
        ]

    def parse_job_title(self, original_title: str) -> ParsedJobTitle:
        """Parse and categorize a job title"""
        if not original_title or not original_title.strip():
            return ParsedJobTitle(
                original_title=original_title,
                parsed_title="",
                category="Unknown",
                level="unknown",
                skills=[],
                location=None,
                work_type=None,
                department=None,
            )

        # Clean the title
        cleaned_title = self._clean_title(original_title)

        # Extract components
        title_parts = self._extract_title_parts(cleaned_title)

        # Determine category
        category = self._categorize_title(title_parts["core_title"])

        # Determine level
        level = self._determine_level(title_parts["core_title"])

        # If level is found, preserve it in the parsed title
        if level != "unknown":
            # Check if level keyword is in the original title
            title_lower = title_parts["core_title"].lower()
            for level_keyword in self.level_keywords:
                if level_keyword in title_lower:
                    # Keep the level keyword in the parsed title
                    break
            else:
                # Level keyword not found, add it back
                if level == "senior":
                    title_parts["core_title"] = f"Senior {title_parts['core_title']}"
                elif level == "junior":
                    title_parts["core_title"] = f"Junior {title_parts['core_title']}"

        # Extract skills
        skills = self._extract_skills(cleaned_title)

        # Extract location - try both original and cleaned title
        location = self._extract_location(original_title)
        if not location:
            location = self._extract_location(cleaned_title)

        # Extract work type
        work_type = self._extract_work_type(cleaned_title)

        # Extract department
        department = self._extract_department(title_parts["core_title"])

        return ParsedJobTitle(
            original_title=original_title,
            parsed_title=title_parts["core_title"],
            category=category,
            level=level,
            skills=skills,
            location=location,
            work_type=work_type,
            department=department,
        )

    def _clean_title(self, title: str) -> str:
        """Clean job title by removing unwanted patterns"""
        # Remove common unwanted patterns
        unwanted_patterns = [
            r"Current Open Jobs",
            r"Open Applications",
            r"Customer Support",
            r"On-site",
            r"Full Time",
            r"Part Time",
            r"Contract",
            r"Freelance",
            # r'Remote',  # Don't remove Remote - needed for work type detection
            # r'Hybrid',  # Don't remove Hybrid - needed for work type detection
            r"Relocate to [A-Za-z\s]+",
            r"Front Office",
            r"Back Office",
            # r'—[A-Za-z\s]+',  # Removed - this was removing location information
            r"\([^)]*\)",  # Remove parentheses content
            r"\[[^\]]*\]",  # Remove bracket content
            r"[A-Z][a-z]+ [A-Z][a-z]+ [A-Z][a-z]+ [A-Z][a-z]+",  # Remove long name patterns
            r"^[A-Z][a-z]+ of [A-Z][a-z]+",  # Remove "A of B" patterns
            r"For [A-Za-z\s]+",  # Remove "For X" patterns
            r"[^\w\s–-]",  # Remove special characters except spaces, hyphens, and em dash
        ]

        # Don't remove level keywords from title
        level_keywords_pattern = r"\b(" + "|".join(self.level_keywords) + r")\b"

        cleaned = title
        for pattern in unwanted_patterns:
            cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)

        # Remove extra whitespace and normalize
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        cleaned = cleaned.strip(".,;:-_|")

        # Preserve level keywords
        title_lower = title.lower()
        preserved_keywords = []
        for keyword in self.level_keywords:
            if keyword in title_lower:
                preserved_keywords.append(keyword)

        # If we have preserved keywords, make sure they're in the cleaned title
        if preserved_keywords:
            cleaned_lower = cleaned.lower()
            for keyword in preserved_keywords:
                if keyword not in cleaned_lower:
                    # Add the keyword back
                    cleaned = f"{keyword.title()} {cleaned}"

        return cleaned

    def _extract_title_parts(self, title: str) -> Dict[str, str]:
        """Extract different parts of the job title"""
        # Split by common separators but be more careful
        if "," in title:
            # For titles like "Manager, Solutions Engineering", keep the full title
            core_title = title
        else:
            parts = re.split(r"[,|/]", title)
            core_title = parts[0].strip() if parts else title

        return {"core_title": core_title, "additional_info": ""}

    def _categorize_title(self, title: str) -> str:
        """Categorize job title based on keywords"""
        title_lower = title.lower()

        # First check for specific skills that indicate technology roles
        tech_skills = [
            "react",
            "javascript",
            "python",
            "java",
            "node",
            "angular",
            "vue",
            "typescript",
            "ruby",
            "rails",
            "php",
            "go",
            "rust",
            "kotlin",
            "swift",
        ]
        for skill in tech_skills:
            if skill in title_lower:
                return "Technology"

        # Then check other categories
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword in title_lower:
                    return category

        return "Other"

    def _determine_level(self, title: str) -> str:
        """Determine job level based on keywords"""
        title_lower = title.lower()

        for level, keywords in self.levels.items():
            for keyword in keywords:
                if keyword in title_lower:
                    return level

        return "unknown"

    def _extract_skills(self, title: str) -> List[str]:
        """Extract skills mentioned in the title"""
        title_lower = title.lower()
        found_skills = []

        for skill in self.skills:
            if skill in title_lower:
                found_skills.append(skill)

        return found_skills

    def _extract_location(self, title: str) -> Optional[str]:
        """Extract location information from title"""
        # Common location names (countries, cities, regions)
        location_names = [
            "north america",
            "south america",
            "europe",
            "asia",
            "africa",
            "australia",
            "united states",
            "usa",
            "canada",
            "mexico",
            "brazil",
            "argentina",
            "united kingdom",
            "uk",
            "germany",
            "france",
            "spain",
            "italy",
            "netherlands",
            "sweden",
            "norway",
            "denmark",
            "finland",
            "switzerland",
            "austria",
            "japan",
            "china",
            "india",
            "singapore",
            "australia",
            "new zealand",
            "new york",
            "london",
            "berlin",
            "paris",
            "madrid",
            "rome",
            "amsterdam",
            "stockholm",
            "oslo",
            "copenhagen",
            "helsinki",
            "zurich",
            "vienna",
            "tokyo",
            "beijing",
            "shanghai",
            "mumbai",
            "delhi",
            "bangalore",
            "san francisco",
            "los angeles",
            "chicago",
            "boston",
            "seattle",
            "toronto",
            "vancouver",
            "montreal",
            "sydney",
            "melbourne",
            "philadelphia",
            "pa",
            "california",
            "ca",
            "texas",
            "tx",
            "florida",
            "fl",
            "england",
            "scotland",
            "wales",
            "ireland",
            "emea",
            "apac",
            "latam",
        ]

        title_lower = title.lower()

        # Look for location patterns - improved patterns
        location_patterns = [
            # "Remote / Philadelphia, PA" or "Hybrid / London, England"
            r"(?:remote|hybrid)\s*/\s*([A-Z][a-z]+(?:\s*,\s*[A-Z]{2})?(?:\s*,\s*[A-Z][a-z]+)?)",
            # "– North America" or "— New York"
            r"[–—]\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
            # "in New York" or "at London"
            r"(?:in|at)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
            # "(Remote)" or "(New York)" or "(London, England)"
            r"\(([A-Z][a-z]+(?:\s*,\s*[A-Z]{2})?(?:\s*,\s*[A-Z][a-z]+)?)\)",
            # "Philadelphia, PA" or "London, England" - specific city, state/country pattern
            r"([A-Z][a-z]+(?:\s*,\s*[A-Z]{2})?(?:\s*,\s*[A-Z][a-z]+)?)",
        ]

        # First, try to find specific location patterns
        for pattern in location_patterns:
            match = re.search(pattern, title, re.IGNORECASE)
            if match:
                location = match.group(1)
                location_lower = location.lower()

                # Skip if it's a common job word or work type word
                skip_words = [
                    "full",
                    "time",
                    "part",
                    "contract",
                    "freelance",
                    "remote",
                    "hybrid",
                    "onsite",
                ]
                if location_lower in skip_words:
                    continue

                # Check if it's a known location name
                if location_lower in location_names:
                    return location

                # Check if it looks like a location (not a job title word)
                job_words = [
                    "director",
                    "manager",
                    "developer",
                    "engineer",
                    "designer",
                    "analyst",
                    "coordinator",
                    "executive",
                    "specialist",
                    "associate",
                    "assistant",
                    "intern",
                    "trainee",
                    "lead",
                    "head",
                    "chief",
                    "team",
                    "project",
                    "product",
                    "business",
                    "marketing",
                    "sales",
                    "python",
                    "javascript",
                    "react",
                    "node",
                    "java",
                    "ruby",
                    "php",
                ]

                if location_lower not in job_words:
                    # Additional check: if it contains common location words
                    location_indicators = [
                        "city",
                        "town",
                        "state",
                        "country",
                        "region",
                        "area",
                        "pa",
                        "ca",
                        "tx",
                        "fl",
                        "ny",
                    ]
                    if any(
                        indicator in location_lower for indicator in location_indicators
                    ):
                        return location

                    # Check if it's a city name pattern (Capitalized words)
                    if re.match(r"^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*$", location):
                        # Additional validation: not a common job title
                        common_titles = [
                            "senior",
                            "junior",
                            "lead",
                            "principal",
                            "staff",
                            "associate",
                            "assistant",
                        ]
                        if not any(title in location_lower for title in common_titles):
                            return location

        return None

    def _extract_work_type(self, title: str) -> Optional[str]:
        """Extract work type from title"""
        title_lower = title.lower()

        # Enhanced work type patterns
        work_type_patterns = {
            "remote": [r"\bremote\b", r"work from home", r"wfh"],
            "hybrid": [r"\bhybrid\b", r"partially remote"],
            "on-site": [r"\bon.?site\b", r"in.?office", r"work from office"],
            "full-time": [r"\bfull.?time\b", r"fulltime", r"ft"],
            "part-time": [r"\bpart.?time\b", r"parttime", r"pt"],
            "contract": [r"\bcontract\b", r"contractor", r"freelance"],
            "freelance": [r"\bfreelance\b", r"freelancer"],
        }

        # Check for work type patterns
        for work_type, patterns in work_type_patterns.items():
            for pattern in patterns:
                if re.search(pattern, title_lower):
                    return work_type

        # Also check for "Remote" in the original title (before cleaning)
        if "remote" in title_lower:
            return "remote"

        return None

    def _extract_department(self, title: str) -> Optional[str]:
        """Extract department from title"""
        title_lower = title.lower()

        for dept in self.departments:
            if dept in title_lower:
                return dept

        return None

    def normalize_title(self, title: str) -> str:
        """Normalize job title for grouping"""
        parsed = self.parse_job_title(title)
        return parsed.parsed_title

    def get_title_variations(self, title: str) -> List[str]:
        """Get common variations of a job title"""
        parsed = self.parse_job_title(title)
        core = parsed.parsed_title.lower()

        variations = [core]

        # Add level variations
        if parsed.level == "senior":
            variations.extend([f"senior {core}", f"sr {core}"])
        elif parsed.level == "junior":
            variations.extend([f"junior {core}", f"jr {core}"])

        # Add department variations
        if parsed.department:
            variations.append(f"{parsed.department} {core}")

        return list(set(variations))


# Global instance
job_title_parser = JobTitleParser()
