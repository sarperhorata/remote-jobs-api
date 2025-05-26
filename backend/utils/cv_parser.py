import os
import logging
import re
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)
    
class CVParser:
    def __init__(self):
        self.supported_formats = ['.pdf', '.doc', '.docx', '.txt']
        
    def parse_cv_file(self, file_path: str) -> Dict:
        """
        Main CV parsing function that handles different file formats
        """
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.pdf':
                text = self._extract_pdf_text(file_path)
            elif file_ext in ['.doc', '.docx']:
                text = self._extract_word_text(file_path)
            elif file_ext == '.txt':
                text = self._extract_txt_text(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_ext}")
            
            if not text:
                return {"error": "Could not extract text from CV"}
            
            parsed_data = self._parse_cv_text(text)
            
            # Add metadata
            parsed_data["source_file"] = os.path.basename(file_path)
            parsed_data["parsed_at"] = datetime.now().isoformat()
            parsed_data["requires_review"] = True
            parsed_data["confidence_score"] = self._calculate_confidence_score(parsed_data)
            
            return parsed_data
            
        except Exception as e:
            logger.error(f"Error parsing CV file {file_path}: {str(e)}")
            return {"error": str(e)}
    
    def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            import PyPDF2
            
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
                    
        except Exception as e:
            logger.error(f"Error extracting PDF text: {str(e)}")
            return ""
    
    def _extract_word_text(self, file_path: str) -> str:
        """Extract text from Word document"""
        try:
            from docx import Document
            
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
            
        except Exception as e:
            logger.error(f"Error extracting Word text: {str(e)}")
            return ""
    
    def _extract_txt_text(self, file_path: str) -> str:
        """Extract text from plain text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            logger.error(f"Error reading text file: {str(e)}")
            return ""
    
    def _parse_cv_text(self, text: str) -> Dict:
        """Parse extracted text and structure it into profile data"""
        parsed_data = {
            "name": "",
            "email": "",
            "phone": "",
            "title": "",
            "summary": "",
            "experience": [],
            "education": [],
            "skills": [],
            "languages": [],
            "certifications": [],
            "projects": [],
            "links": {
                "linkedin": "",
                "github": "",
                "portfolio": ""
            }
        }
        
        # Extract basic contact information
        parsed_data["name"] = self._extract_name(text)
        parsed_data["email"] = self._extract_email(text)
        parsed_data["phone"] = self._extract_phone(text)
        parsed_data["links"] = self._extract_links(text)
        
        # Extract professional information
        parsed_data["title"] = self._extract_title(text)
        parsed_data["summary"] = self._extract_summary(text)
        parsed_data["experience"] = self._extract_experience(text)
        parsed_data["education"] = self._extract_education(text)
        parsed_data["skills"] = self._extract_skills(text)
        
        return parsed_data
    
    def _extract_name(self, text: str) -> str:
        """Extract person's name from CV"""
        lines = text.split('\n')
        
        # Name is usually in the first few lines
        for line in lines[:5]:
            line = line.strip()
            if len(line) > 0 and len(line) < 100:
                # Check if line contains common name patterns
                words = line.split()
                if 2 <= len(words) <= 4 and all(word.replace('-', '').replace("'", '').isalpha() for word in words):
                    return line
        return ""
    
    def _extract_email(self, text: str) -> str:
        """Extract email address"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.findall(email_pattern, text)
        return matches[0] if matches else ""
    
    def _extract_phone(self, text: str) -> str:
        """Extract phone number"""
        phone_patterns = [
            r'\+?1?\d{9,15}',
            r'\(\d{3}\)\s*\d{3}-\d{4}',
            r'\d{3}-\d{3}-\d{4}',
            r'\d{3}\.\d{3}\.\d{4}'
        ]
        
        for pattern in phone_patterns:
            matches = re.findall(pattern, text)
            if matches:
                return matches[0]
        return ""
    
    def _extract_links(self, text: str) -> Dict[str, str]:
        """Extract social media and portfolio links"""
        links = {
            "linkedin": "",
            "github": "",
            "portfolio": ""
        }
        
        # LinkedIn
        linkedin_pattern = r'(?:https?://)?(?:www\.)?linkedin\.com/in/[A-Za-z0-9_-]+'
        linkedin_matches = re.findall(linkedin_pattern, text, re.IGNORECASE)
        if linkedin_matches:
            links["linkedin"] = linkedin_matches[0]
        
        # GitHub
        github_pattern = r'(?:https?://)?(?:www\.)?github\.com/[A-Za-z0-9_-]+'
        github_matches = re.findall(github_pattern, text, re.IGNORECASE)
        if github_matches:
            links["github"] = github_matches[0]
        
        return links
    
    def _extract_title(self, text: str) -> str:
        """Extract job title/professional title"""
        lines = text.split('\n')
        
        # Title usually follows name or is in first few lines
        job_keywords = ['developer', 'engineer', 'manager', 'analyst', 'designer', 
                       'consultant', 'specialist', 'coordinator', 'director', 'lead']
        
        for line in lines[:10]:
            line_lower = line.lower().strip()
            if any(keyword in line_lower for keyword in job_keywords) and len(line.strip()) < 100:
                return line.strip()
        
        return ""
    
    def _extract_summary(self, text: str) -> str:
        """Extract professional summary/objective"""
        summary_keywords = ['summary', 'objective', 'profile', 'about', 'overview']
        
        for keyword in summary_keywords:
            pattern = rf'{keyword}[:\s]*(.*?)(?=\n\n|\n[A-Z][A-Z\s]+\n|$)'
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            if matches:
                return matches[0].strip()
        
        return ""
    
    def _extract_experience(self, text: str) -> List[Dict]:
        """Extract work experience"""
        experience_keywords = ['experience', 'work experience', 'employment', 'career']
        experience_section = ""
        
        for keyword in experience_keywords:
            pattern = rf'{keyword}[:\s]*(.*?)(?=\n(?:education|skills|projects)|$)'
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            if matches:
                experience_section = matches[0].strip()
                break
        
        if not experience_section:
            return []
        
        # Basic experience parsing - can be enhanced
        experiences = []
        lines = [line.strip() for line in experience_section.split('\n') if line.strip()]
        
        current_job = {}
        for line in lines:
            if len(line) > 10 and not line.startswith('-') and not line.startswith('•'):
                if current_job:
                    experiences.append(current_job)
                current_job = {"title": line, "description": ""}
            elif current_job:
                current_job["description"] += line + " "
        
        if current_job:
            experiences.append(current_job)
        
        return experiences
    
    def _extract_education(self, text: str) -> List[Dict]:
        """Extract education information"""
        education_keywords = ['education', 'academic', 'qualifications']
        education_section = ""
        
        for keyword in education_keywords:
            pattern = rf'{keyword}[:\s]*(.*?)(?=\n(?:experience|skills|projects)|$)'
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            if matches:
                education_section = matches[0].strip()
                break
        
        if not education_section:
            return []
        
        # Basic education parsing
        educations = []
        lines = [line.strip() for line in education_section.split('\n') if line.strip()]
        
        for line in lines:
            if len(line) > 10:
                educations.append({"degree": line, "institution": "", "year": ""})
        
        return educations
    
    def _extract_skills(self, text: str) -> List[str]:
        """Extract skills list"""
        skills_keywords = ['skills', 'technical skills', 'competencies']
        skills_section = ""
        
        for keyword in skills_keywords:
            pattern = rf'{keyword}[:\s]*(.*?)(?=\n(?:experience|education|projects)|$)'
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            if matches:
                skills_section = matches[0].strip()
                break
        
        if not skills_section:
            return []
        
        # Common skill separators
        skills = re.split(r'[,•\n\t]+', skills_section)
        return [skill.strip() for skill in skills if skill.strip() and len(skill.strip()) > 1]
    
    def _calculate_confidence_score(self, parsed_data: Dict) -> float:
        """Calculate confidence score based on extracted data quality"""
        score = 0.0
        max_score = 100.0
        
        # Basic info (40 points)
        if parsed_data.get("name"):
            score += 15
        if parsed_data.get("email"):
            score += 15
        if parsed_data.get("phone"):
            score += 10
        
        # Professional info (40 points)
        if parsed_data.get("title"):
            score += 10
        if parsed_data.get("experience") and len(parsed_data["experience"]) > 0:
            score += 20
        if parsed_data.get("skills") and len(parsed_data["skills"]) > 2:
            score += 10
        
        # Additional info (20 points)
        if parsed_data.get("education") and len(parsed_data["education"]) > 0:
            score += 10
        if parsed_data.get("summary"):
            score += 5
        if parsed_data.get("links", {}).get("linkedin"):
            score += 5
        
        return min(score, max_score)

# Legacy function for backward compatibility
def parse_cv_file(file_path: str) -> Dict:
    """Legacy function that uses the new CVParser class"""
    parser = CVParser()
    return parser.parse_cv_file(file_path) 