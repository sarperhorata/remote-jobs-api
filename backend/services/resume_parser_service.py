import re
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import pypdf
from docx import Document
from io import BytesIO
import base64

logger = logging.getLogger(__name__)

class ResumeParserService:
    """
    Resume parsing service that extracts structured information from resumes
    Supports PDF, DOCX, and text formats
    """
    
    def __init__(self):
        self.email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        self.phone_pattern = r'(\+?[\d\s\-\(\)]{10,})'
        self.linkedin_pattern = r'(?:linkedin\.com/in/|linkedin\.com/company/)([a-zA-Z0-9\-_]+)'
        self.github_pattern = r'(?:github\.com/)([a-zA-Z0-9\-_]+)'
        
        # Common skill keywords
        self.tech_skills = {
            'programming': ['python', 'javascript', 'java', 'c++', 'c#', 'php', 'ruby', 'go', 'rust', 'swift', 'kotlin'],
            'frameworks': ['react', 'angular', 'vue', 'django', 'flask', 'spring', 'express', 'laravel', 'rails'],
            'databases': ['mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'sqlite', 'oracle'],
            'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'jenkins'],
            'tools': ['git', 'jira', 'confluence', 'slack', 'figma', 'adobe', 'photoshop'],
            'languages': ['english', 'turkish', 'german', 'french', 'spanish', 'italian', 'russian', 'chinese']
        }
        
        # Education keywords
        self.education_keywords = [
            'university', 'college', 'school', 'institute', 'academy', 'bachelor', 'master', 'phd', 'degree',
            'graduation', 'diploma', 'certificate', 'course', 'training', 'education'
        ]
        
        # Experience keywords
        self.experience_keywords = [
            'experience', 'work', 'employment', 'job', 'position', 'role', 'responsibility',
            'project', 'achievement', 'accomplishment', 'lead', 'manage', 'develop', 'design'
        ]

    def parse_resume(self, file_content: bytes, file_type: str) -> Dict[str, Any]:
        """
        Parse resume file and extract structured information
        
        Args:
            file_content: Raw file content
            file_type: File type ('pdf', 'docx', 'txt')
            
        Returns:
            Dictionary containing parsed resume information
        """
        try:
            # Extract text based on file type
            if file_type.lower() == 'pdf':
                text = self._extract_text_from_pdf(file_content)
            elif file_type.lower() == 'docx':
                text = self._extract_text_from_docx(file_content)
            elif file_type.lower() == 'txt':
                text = file_content.decode('utf-8')
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
            
            # Parse the extracted text
            return self._parse_text(text)
            
        except Exception as e:
            logger.error(f"Error parsing resume: {str(e)}")
            return {
                'error': str(e),
                'raw_text': file_content.decode('utf-8', errors='ignore')[:1000] if isinstance(file_content, bytes) else str(file_content)[:1000]
            }

    def _extract_text_from_pdf(self, file_content: bytes) -> str:
        """Extract text from PDF file"""
        try:
            pdf_reader = pypdf.PdfReader(BytesIO(file_content))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            return ""

    def _extract_text_from_docx(self, file_content: bytes) -> str:
        """Extract text from DOCX file"""
        try:
            doc = Document(BytesIO(file_content))
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            logger.error(f"Error extracting text from DOCX: {str(e)}")
            return ""

    def _parse_text(self, text: str) -> Dict[str, Any]:
        """Parse text and extract structured information"""
        text = text.lower()
        lines = text.split('\n')
        
        result = {
            'personal_info': self._extract_personal_info(text),
            'skills': self._extract_skills(text),
            'experience': self._extract_experience(text, lines),
            'education': self._extract_education(text, lines),
            'languages': self._extract_languages(text),
            'summary': self._extract_summary(text),
            'raw_text': text[:2000],  # Keep first 2000 chars for reference
            'parsed_at': datetime.now().isoformat()
        }
        
        return result

    def _extract_personal_info(self, text: str) -> Dict[str, str]:
        """Extract personal information"""
        info = {}
        
        # Extract email
        emails = re.findall(self.email_pattern, text)
        if emails:
            info['email'] = emails[0]
        
        # Extract phone
        phones = re.findall(self.phone_pattern, text)
        if phones:
            info['phone'] = phones[0].strip()
        
        # Extract LinkedIn
        linkedin = re.findall(self.linkedin_pattern, text)
        if linkedin:
            info['linkedin'] = f"linkedin.com/in/{linkedin[0]}"
        
        # Extract GitHub
        github = re.findall(self.github_pattern, text)
        if github:
            info['github'] = f"github.com/{github[0]}"
        
        # Extract name (simple heuristic)
        lines = text.split('\n')
        for line in lines[:10]:  # Check first 10 lines
            line = line.strip()
            if len(line) > 2 and len(line) < 50 and not any(keyword in line for keyword in ['@', 'http', 'www', 'experience', 'education']):
                if not re.search(r'\d', line):  # No numbers
                    info['name'] = line.title()
                    break
        
        return info

    def _extract_skills(self, text: str) -> Dict[str, List[str]]:
        """Extract skills from text"""
        skills = {}
        
        for category, keywords in self.tech_skills.items():
            found_skills = []
            for skill in keywords:
                if skill in text:
                    found_skills.append(skill)
            if found_skills:
                skills[category] = found_skills
        
        # Extract additional skills using regex patterns
        additional_skills = []
        
        # Look for skill patterns like "Skills:", "Technologies:", etc.
        skill_patterns = [
            r'skills?[:\s]+([^.\n]+)',
            r'technologies?[:\s]+([^.\n]+)',
            r'tools?[:\s]+([^.\n]+)',
            r'languages?[:\s]+([^.\n]+)'
        ]
        
        for pattern in skill_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                skills_list = [s.strip() for s in match.split(',')]
                additional_skills.extend(skills_list)
        
        if additional_skills:
            skills['additional'] = list(set(additional_skills))
        
        return skills

    def _extract_experience(self, text: str, lines: List[str]) -> List[Dict[str, str]]:
        """Extract work experience"""
        experience = []
        
        # Look for experience sections
        experience_sections = []
        in_experience = False
        current_section = []
        
        for line in lines:
            line_lower = line.lower()
            
            # Check if we're entering an experience section
            if any(keyword in line_lower for keyword in ['experience', 'work history', 'employment']):
                if current_section:
                    experience_sections.append('\n'.join(current_section))
                current_section = [line]
                in_experience = True
            elif in_experience:
                # Check if we're leaving experience section
                if any(keyword in line_lower for keyword in ['education', 'skills', 'projects', 'certificates']):
                    experience_sections.append('\n'.join(current_section))
                    current_section = []
                    in_experience = False
                else:
                    current_section.append(line)
        
        if current_section:
            experience_sections.append('\n'.join(current_section))
        
        # Parse each experience section
        for section in experience_sections:
            exp = self._parse_experience_section(section)
            if exp:
                experience.append(exp)
        
        return experience

    def _parse_experience_section(self, section: str) -> Optional[Dict[str, str]]:
        """Parse individual experience section"""
        lines = section.split('\n')
        
        exp = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Extract company name (look for patterns like "Company Name - Position")
            if ' - ' in line or ' at ' in line:
                parts = re.split(r'\s+[-–—]\s+|\s+at\s+', line, maxsplit=1)
                if len(parts) >= 2:
                    exp['company'] = parts[0].strip()
                    exp['position'] = parts[1].strip()
            
            # Extract dates
            date_pattern = r'(\d{4})\s*[-–—]\s*(\d{4}|present|current|now)'
            dates = re.findall(date_pattern, line, re.IGNORECASE)
            if dates:
                exp['start_date'] = dates[0][0]
                exp['end_date'] = dates[0][1]
            
            # Extract duration
            duration_pattern = r'(\d+)\s*(?:years?|months?|yrs?|mos?)'
            duration = re.findall(duration_pattern, line, re.IGNORECASE)
            if duration:
                exp['duration'] = f"{duration[0]} years"
        
        return exp if exp else None

    def _extract_education(self, text: str, lines: List[str]) -> List[Dict[str, str]]:
        """Extract education information"""
        education = []
        
        # Look for education sections
        education_sections = []
        in_education = False
        current_section = []
        
        for line in lines:
            line_lower = line.lower()
            
            # Check if we're entering an education section
            if any(keyword in line_lower for keyword in ['education', 'academic', 'degree']):
                if current_section:
                    education_sections.append('\n'.join(current_section))
                current_section = [line]
                in_education = True
            elif in_education:
                # Check if we're leaving education section
                if any(keyword in line_lower for keyword in ['experience', 'skills', 'projects', 'certificates']):
                    education_sections.append('\n'.join(current_section))
                    current_section = []
                    in_education = False
                else:
                    current_section.append(line)
        
        if current_section:
            education_sections.append('\n'.join(current_section))
        
        # Parse each education section
        for section in education_sections:
            edu = self._parse_education_section(section)
            if edu:
                education.append(edu)
        
        return education

    def _parse_education_section(self, section: str) -> Optional[Dict[str, str]]:
        """Parse individual education section"""
        lines = section.split('\n')
        
        edu = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Extract degree
            degree_patterns = [
                r'(bachelor|master|phd|doctorate|associate|diploma|certificate)',
                r'(ba|bs|ma|ms|mba|phd|bsc|msc)'
            ]
            
            for pattern in degree_patterns:
                degree_match = re.search(pattern, line, re.IGNORECASE)
                if degree_match:
                    edu['degree'] = degree_match.group(1)
                    break
            
            # Extract university/school name
            if any(keyword in line.lower() for keyword in ['university', 'college', 'school', 'institute']):
                edu['institution'] = line
            
            # Extract dates
            date_pattern = r'(\d{4})\s*[-–—]\s*(\d{4}|present|current|now)'
            dates = re.findall(date_pattern, line, re.IGNORECASE)
            if dates:
                edu['start_date'] = dates[0][0]
                edu['end_date'] = dates[0][1]
        
        return edu if edu else None

    def _extract_languages(self, text: str) -> List[str]:
        """Extract language skills"""
        languages = []
        
        # Check for known languages
        for language in self.tech_skills['languages']:
            if language in text:
                languages.append(language)
        
        # Look for language patterns
        language_patterns = [
            r'languages?[:\s]+([^.\n]+)',
            r'spoken languages?[:\s]+([^.\n]+)',
            r'fluent in[:\s]+([^.\n]+)'
        ]
        
        for pattern in language_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                lang_list = [lang.strip() for lang in match.split(',')]
                languages.extend(lang_list)
        
        return list(set(languages))

    def _extract_summary(self, text: str) -> str:
        """Extract summary/objective section"""
        summary_patterns = [
            r'summary[:\s]+([^.\n]+(?:\.[^.\n]+)*)',
            r'objective[:\s]+([^.\n]+(?:\.[^.\n]+)*)',
            r'profile[:\s]+([^.\n]+(?:\.[^.\n]+)*)'
        ]
        
        for pattern in summary_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # If no explicit summary, take first few sentences
        sentences = re.split(r'[.!?]+', text)
        if sentences:
            return sentences[0][:200] + "..." if len(sentences[0]) > 200 else sentences[0]
        
        return ""

    def parse_resume_from_base64(self, base64_content: str, file_type: str) -> Dict[str, Any]:
        """Parse resume from base64 encoded content"""
        try:
            file_content = base64.b64decode(base64_content)
            return self.parse_resume(file_content, file_type)
        except Exception as e:
            logger.error(f"Error parsing base64 resume: {str(e)}")
            return {'error': str(e)}

    def get_parsed_resume_summary(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get a summary of parsed resume data"""
        summary = {
            'has_personal_info': bool(parsed_data.get('personal_info')),
            'has_skills': bool(parsed_data.get('skills')),
            'has_experience': bool(parsed_data.get('experience')),
            'has_education': bool(parsed_data.get('education')),
            'has_languages': bool(parsed_data.get('languages')),
            'has_summary': bool(parsed_data.get('summary')),
            'total_skills': sum(len(skills) for skills in parsed_data.get('skills', {}).values()),
            'experience_count': len(parsed_data.get('experience', [])),
            'education_count': len(parsed_data.get('education', [])),
            'language_count': len(parsed_data.get('languages', [])),
            'parsed_at': parsed_data.get('parsed_at')
        }
        
        return summary