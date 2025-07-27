import io
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Optional imports for CV parsing
try:
    import PyPDF2

    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    PyPDF2 = None
    logger.warning("PyPDF2 not available - PDF parsing disabled")

try:
    import docx

    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    docx = None
    logger.warning("python-docx not available - DOCX parsing disabled")

try:
    import spacy

    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    spacy = None
    logger.warning("spaCy not available - using basic parsing")


class CVParserService:
    def __init__(self):
        self.nlp = None
        if SPACY_AVAILABLE:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                logger.warning("spaCy English model not found. Using basic parsing.")
                self.nlp = None
        else:
            logger.info("Using basic parsing without spaCy")

    def parse_cv(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        Parse CV file and extract structured information
        """
        try:
            file_extension = Path(filename).suffix.lower()

            if file_extension == ".pdf":
                text = self._extract_text_from_pdf(file_content)
            elif file_extension in [".doc", ".docx"]:
                text = self._extract_text_from_doc(file_content, file_extension)
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")

            # Parse the extracted text
            parsed_data = self._parse_text(text)

            logger.info(f"Successfully parsed CV: {filename}")
            return parsed_data

        except Exception as e:
            logger.error(f"Error parsing CV {filename}: {str(e)}")
            raise

    def _extract_text_from_pdf(self, file_content: bytes) -> str:
        """Extract text from PDF file"""
        if not PDF_AVAILABLE:
            raise ValueError("PDF parsing not available - PyPDF2 not installed")

        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            raise

    def _extract_text_from_doc(self, file_content: bytes, file_extension: str) -> str:
        """Extract text from DOC/DOCX file"""
        if not DOCX_AVAILABLE:
            raise ValueError("DOCX parsing not available - python-docx not installed")

        try:
            if file_extension == ".docx":
                doc = docx.Document(io.BytesIO(file_content))
            else:
                # For .doc files, we might need additional libraries
                # For now, we'll handle .docx only
                raise ValueError(
                    "DOC format not supported yet. Please convert to DOCX or PDF."
                )

            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            logger.error(f"Error extracting text from DOC: {str(e)}")
            raise

    def _parse_text(self, text: str) -> Dict[str, Any]:
        """Parse extracted text and extract structured information"""
        parsed_data = {
            "name": "",
            "email": "",
            "phone": "",
            "location": "",
            "summary": "",
            "skills": [],
            "experience": [],
            "education": [],
            "languages": [],
            "certifications": [],
        }

        # Extract basic information
        parsed_data["name"] = self._extract_name(text)
        parsed_data["email"] = self._extract_email(text)
        parsed_data["phone"] = self._extract_phone(text)
        parsed_data["location"] = self._extract_location(text)
        parsed_data["summary"] = self._extract_summary(text)
        parsed_data["skills"] = self._extract_skills(text)
        parsed_data["experience"] = self._extract_experience(text)
        parsed_data["education"] = self._extract_education(text)
        parsed_data["languages"] = self._extract_languages(text)
        parsed_data["certifications"] = self._extract_certifications(text)

        return parsed_data

    def _extract_name(self, text: str) -> str:
        """Extract name from CV text"""
        # Look for common name patterns at the beginning of the document
        lines = text.split("\n")
        for line in lines[:10]:  # Check first 10 lines
            line = line.strip()
            if line and len(line) < 50:  # Reasonable name length
                # Remove common titles and prefixes
                clean_line = re.sub(
                    r"^(Mr\.|Mrs\.|Ms\.|Dr\.|Prof\.)\s*", "", line, flags=re.IGNORECASE
                )
                if re.match(r"^[A-Z][a-z]+(\s+[A-Z][a-z]+)*$", clean_line):
                    return clean_line
        return ""

    def _extract_email(self, text: str) -> str:
        """Extract email address from text"""
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        emails = re.findall(email_pattern, text)
        return emails[0] if emails else ""

    def _extract_phone(self, text: str) -> str:
        """Extract phone number from text"""
        # Various phone number patterns
        phone_patterns = [
            r"\+?1?\s*\(?[0-9]{3}\)?[\s.-]?[0-9]{3}[\s.-]?[0-9]{4}",  # US format
            r"\+?[0-9]{1,4}[\s.-]?[0-9]{1,4}[\s.-]?[0-9]{1,4}[\s.-]?[0-9]{1,4}",  # International
            r"\(?[0-9]{3}\)?[\s.-]?[0-9]{3}[\s.-]?[0-9]{4}",  # Simple US
        ]

        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            if phones:
                return phones[0]
        return ""

    def _extract_location(self, text: str) -> str:
        """Extract location from text"""
        # Look for common location indicators
        location_indicators = ["Address:", "Location:", "Based in:", "Residing in:"]
        lines = text.split("\n")

        for i, line in enumerate(lines):
            for indicator in location_indicators:
                if indicator.lower() in line.lower():
                    # Extract the location part
                    location = line.split(":", 1)[1].strip() if ":" in line else ""
                    if location:
                        return location

                    # Check next line if current line only contains indicator
                    if i + 1 < len(lines):
                        next_line = lines[i + 1].strip()
                        if next_line and len(next_line) < 100:
                            return next_line

        return ""

    def _extract_summary(self, text: str) -> str:
        """Extract professional summary/objective"""
        summary_indicators = [
            "Summary:",
            "Objective:",
            "Profile:",
            "About:",
            "Professional Summary:",
        ]
        lines = text.split("\n")

        for i, line in enumerate(lines):
            for indicator in summary_indicators:
                if indicator.lower() in line.lower():
                    # Extract summary content
                    summary = line.split(":", 1)[1].strip() if ":" in line else ""
                    if summary:
                        return summary

                    # Check next few lines for summary content
                    summary_lines = []
                    for j in range(i + 1, min(i + 5, len(lines))):
                        next_line = lines[j].strip()
                        if next_line and len(next_line) > 20:
                            summary_lines.append(next_line)
                        elif next_line and len(next_line) < 10:
                            break

                    if summary_lines:
                        return " ".join(summary_lines)

        return ""

    def _extract_skills(self, text: str) -> List[str]:
        """Extract skills from text"""
        skills = []

        # Look for skills section
        skills_indicators = [
            "Skills:",
            "Technical Skills:",
            "Programming Languages:",
            "Technologies:",
        ]
        lines = text.split("\n")

        for i, line in enumerate(lines):
            for indicator in skills_indicators:
                if indicator.lower() in line.lower():
                    # Extract skills from current line
                    skills_text = line.split(":", 1)[1].strip() if ":" in line else ""
                    if skills_text:
                        skills.extend([s.strip() for s in skills_text.split(",")])

                    # Check next few lines for more skills
                    for j in range(i + 1, min(i + 10, len(lines))):
                        next_line = lines[j].strip()
                        if next_line and len(next_line) < 100:
                            # Check if line contains skill-like content
                            if "," in next_line or "•" in next_line or "-" in next_line:
                                skill_items = re.split(r"[,•\-]", next_line)
                                skills.extend(
                                    [s.strip() for s in skill_items if s.strip()]
                                )
                        elif not next_line:
                            break

        # Clean and filter skills
        cleaned_skills = []
        for skill in skills:
            skill = skill.strip()
            if skill and len(skill) > 1 and len(skill) < 50:
                # Remove common prefixes/suffixes
                skill = re.sub(r"^(and|or|&)\s*", "", skill, flags=re.IGNORECASE)
                skill = re.sub(r"\s+(and|or|&)$", "", skill, flags=re.IGNORECASE)
                if skill and skill not in cleaned_skills:
                    cleaned_skills.append(skill)

        return cleaned_skills[:20]  # Limit to 20 skills

    def _extract_experience(self, text: str) -> List[Dict[str, str]]:
        """Extract work experience from text"""
        experience = []

        # Look for experience section
        experience_indicators = [
            "Experience:",
            "Work Experience:",
            "Employment History:",
            "Professional Experience:",
        ]
        lines = text.split("\n")

        for i, line in enumerate(lines):
            for indicator in experience_indicators:
                if indicator.lower() in line.lower():
                    # Parse experience entries
                    current_experience = {}
                    for j in range(i + 1, len(lines)):
                        exp_line = lines[j].strip()
                        if not exp_line:
                            if current_experience:
                                experience.append(current_experience.copy())
                                current_experience = {}
                            continue

                        # Look for company name pattern
                        if (
                            re.match(r"^[A-Z][A-Za-z\s&.,]+$", exp_line)
                            and len(exp_line) < 100
                        ):
                            if current_experience:
                                experience.append(current_experience.copy())
                            current_experience = {"company": exp_line}

                        # Look for date patterns
                        date_pattern = r"(\d{4})\s*[-–]\s*(\d{4}|Present|Current)"
                        date_match = re.search(date_pattern, exp_line)
                        if date_match:
                            current_experience["period"] = date_match.group(0)

                        # Look for job title
                        if "title" not in current_experience and len(exp_line) < 80:
                            current_experience["title"] = exp_line

                        # Look for description
                        if (
                            len(exp_line) > 50
                            and "description" not in current_experience
                        ):
                            current_experience["description"] = exp_line

                    # Add last experience entry
                    if current_experience:
                        experience.append(current_experience)
                    break

        return experience[:5]  # Limit to 5 experiences

    def _extract_education(self, text: str) -> List[Dict[str, str]]:
        """Extract education from text"""
        education = []

        # Look for education section
        education_indicators = ["Education:", "Academic Background:", "Qualifications:"]
        lines = text.split("\n")

        for i, line in enumerate(lines):
            for indicator in education_indicators:
                if indicator.lower() in line.lower():
                    # Parse education entries
                    current_education = {}
                    for j in range(i + 1, len(lines)):
                        edu_line = lines[j].strip()
                        if not edu_line:
                            if current_education:
                                education.append(current_education.copy())
                                current_education = {}
                            continue

                        # Look for university/school name
                        if (
                            re.match(r"^[A-Z][A-Za-z\s&.,]+$", edu_line)
                            and len(edu_line) < 100
                        ):
                            if current_education:
                                education.append(current_education.copy())
                            current_education = {"institution": edu_line}

                        # Look for degree
                        degree_patterns = [
                            "Bachelor",
                            "Master",
                            "PhD",
                            "Doctorate",
                            "Associate",
                            "Diploma",
                        ]
                        for pattern in degree_patterns:
                            if pattern.lower() in edu_line.lower():
                                current_education["degree"] = edu_line
                                break

                        # Look for date
                        date_pattern = r"(\d{4})\s*[-–]\s*(\d{4}|Present|Current)"
                        date_match = re.search(date_pattern, edu_line)
                        if date_match:
                            current_education["period"] = date_match.group(0)

                    # Add last education entry
                    if current_education:
                        education.append(current_education)
                    break

        return education[:3]  # Limit to 3 education entries

    def _extract_languages(self, text: str) -> List[str]:
        """Extract languages from text"""
        languages = []

        # Look for languages section
        language_indicators = ["Languages:", "Language Skills:", "Spoken Languages:"]
        lines = text.split("\n")

        for i, line in enumerate(lines):
            for indicator in language_indicators:
                if indicator.lower() in line.lower():
                    # Extract languages from current line
                    lang_text = line.split(":", 1)[1].strip() if ":" in line else ""
                    if lang_text:
                        languages.extend([l.strip() for l in lang_text.split(",")])

                    # Check next few lines
                    for j in range(i + 1, min(i + 5, len(lines))):
                        next_line = lines[j].strip()
                        if next_line and len(next_line) < 100:
                            if "," in next_line:
                                lang_items = next_line.split(",")
                                languages.extend([l.strip() for l in lang_items])
                        elif not next_line:
                            break
                    break

        # Clean languages
        cleaned_languages = []
        for lang in languages:
            lang = lang.strip()
            if lang and len(lang) > 1 and len(lang) < 30:
                # Remove proficiency levels
                lang = re.sub(r"\s*\([^)]*\)", "", lang)
                lang = re.sub(
                    r"\s*(Native|Fluent|Intermediate|Basic)",
                    "",
                    lang,
                    flags=re.IGNORECASE,
                )
                if lang and lang not in cleaned_languages:
                    cleaned_languages.append(lang)

        return cleaned_languages[:5]  # Limit to 5 languages

    def _extract_certifications(self, text: str) -> List[str]:
        """Extract certifications from text"""
        certifications = []

        # Look for certifications section
        cert_indicators = [
            "Certifications:",
            "Certificates:",
            "Professional Certifications:",
        ]
        lines = text.split("\n")

        for i, line in enumerate(lines):
            for indicator in cert_indicators:
                if indicator.lower() in line.lower():
                    # Extract certifications from current line
                    cert_text = line.split(":", 1)[1].strip() if ":" in line else ""
                    if cert_text:
                        certifications.extend([c.strip() for c in cert_text.split(",")])

                    # Check next few lines
                    for j in range(i + 1, min(i + 10, len(lines))):
                        next_line = lines[j].strip()
                        if next_line and len(next_line) < 150:
                            if "," in next_line or "•" in next_line:
                                cert_items = re.split(r"[,•]", next_line)
                                certifications.extend([c.strip() for c in cert_items])
                        elif not next_line:
                            break
                    break

        # Clean certifications
        cleaned_certs = []
        for cert in certifications:
            cert = cert.strip()
            if cert and len(cert) > 5 and len(cert) < 100:
                # Remove date patterns
                cert = re.sub(r"\d{4}", "", cert)
                cert = re.sub(r"\s+", " ", cert).strip()
                if cert and cert not in cleaned_certs:
                    cleaned_certs.append(cert)

        return cleaned_certs[:5]  # Limit to 5 certifications


# Create singleton instance
cv_parser_service = CVParserService()
