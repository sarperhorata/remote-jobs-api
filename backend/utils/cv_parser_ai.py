#!/usr/bin/env python3

import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional

from openai import OpenAI

# Import existing parser as fallback
from .cv_parser import CVParser

logger = logging.getLogger(__name__)


class CVParserAI:
    def __init__(self):
        self.openai_client = None
        self.fallback_parser = CVParser()
        self._initialize_openai()

    def _initialize_openai(self):
        """Initialize OpenAI client if API key is available"""
        api_key = os.getenv("OPENAI_API_KEY")

        if api_key:
            try:
                self.openai_client = OpenAI(api_key=api_key)
                logger.info("✅ OpenAI client initialized")
            except Exception as e:
                logger.warning(f"⚠️ OpenAI initialization failed: {str(e)}")
                self.openai_client = None
        else:
            logger.warning("⚠️ OPENAI_API_KEY not found, using fallback parser")

    def parse_cv_file_enhanced(self, file_path: str) -> Dict:
        """
        Enhanced CV parsing with OpenAI GPT-4o Mini
        Falls back to basic parser if OpenAI is not available
        """
        try:
            # First, extract text using basic parser
            basic_result = self.fallback_parser.parse_cv_file(file_path)

            if basic_result.get("error"):
                return basic_result

            # If OpenAI is available, enhance the parsing
            if self.openai_client:
                logger.info(f"🤖 Enhancing CV parsing with OpenAI: {file_path}")
                enhanced_result = self._enhance_with_openai(basic_result, file_path)

                # Merge results
                final_result = self._merge_results(basic_result, enhanced_result)
                final_result["parsing_method"] = "openai_enhanced"
                final_result["ai_confidence"] = enhanced_result.get("confidence", 0.0)

                return final_result
            else:
                # Return basic result if OpenAI not available
                basic_result["parsing_method"] = "basic_fallback"
                return basic_result

        except Exception as e:
            logger.error(f"❌ Enhanced CV parsing failed: {str(e)}")
            # Return basic parsing as fallback
            return self.fallback_parser.parse_cv_file(file_path)

    def _enhance_with_openai(self, basic_result: Dict, file_path: str) -> Dict:
        """Use OpenAI to enhance CV parsing results"""
        try:
            # Extract raw text for AI processing
            file_ext = os.path.splitext(file_path)[1].lower()

            if file_ext == ".pdf":
                raw_text = self.fallback_parser._extract_pdf_text(file_path)
            elif file_ext in [".doc", ".docx"]:
                raw_text = self.fallback_parser._extract_word_text(file_path)
            elif file_ext == ".txt":
                raw_text = self.fallback_parser._extract_txt_text(file_path)
            else:
                return {}

            if not raw_text or len(raw_text) < 50:
                logger.warning("⚠️ Insufficient text for OpenAI processing")
                return {}

            # Prepare prompt for GPT-4o Mini
            prompt = self._create_cv_analysis_prompt(raw_text)

            # Call OpenAI API
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert CV/Resume parser. Extract structured information from CV text and return valid JSON.",
                    },
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
                max_tokens=2000,
            )

            # Parse response
            ai_result = json.loads(response.choices[0].message.content)
            logger.info("✅ OpenAI parsing successful")

            return ai_result

        except Exception as e:
            logger.error(f"❌ OpenAI enhancement failed: {str(e)}")
            return {}

    def _create_cv_analysis_prompt(self, cv_text: str) -> str:
        """Create a structured prompt for CV analysis"""

        # Limit text length for API efficiency (keep first 4000 chars)
        truncated_text = cv_text[:4000] if len(cv_text) > 4000 else cv_text

        prompt = f"""
Analyze this CV/Resume text and extract structured information. Return a JSON object with the following structure:

{{
    "name": "Full name of the person",
    "email": "Email address",
    "phone": "Phone number in standard format",
    "title": "Current or target job title/position",
    "summary": "Professional summary or objective",
    "skills": ["List", "of", "technical", "and", "professional", "skills"],
    "languages": ["Language1", "Language2"],
    "experience": [
        {{
            "title": "Job title",
            "company": "Company name", 
            "duration": "Start - End dates",
            "description": "Key responsibilities and achievements",
            "technologies": ["Tech1", "Tech2"]
        }}
    ],
    "education": [
        {{
            "degree": "Degree title",
            "institution": "School/University name",
            "year": "Graduation year or duration",
            "field": "Field of study"
        }}
    ],
    "certifications": ["Certification1", "Certification2"],
    "projects": [
        {{
            "name": "Project name",
            "description": "Brief description",
            "technologies": ["Tech1", "Tech2"]
        }}
    ],
    "links": {{
        "linkedin": "LinkedIn URL",
        "github": "GitHub URL", 
        "portfolio": "Portfolio URL",
        "other": "Other professional URLs"
    }},
    "confidence": 0.95,
    "notes": "Any additional observations about the CV"
}}

Important guidelines:
1. Extract information accurately from the text
2. For skills, focus on technical skills, programming languages, tools, frameworks
3. Normalize job titles (e.g., "Sr. Software Engineer" -> "Senior Software Engineer")
4. Extract years/durations in consistent format
5. Include confidence score (0.0-1.0) based on text clarity
6. If information is missing, use empty string or empty array
7. For Turkish CVs, translate key information to English while preserving original company names

CV Text:
{truncated_text}
"""
        return prompt

    def _merge_results(self, basic_result: Dict, ai_result: Dict) -> Dict:
        """Merge basic parser results with AI enhancements"""

        merged = basic_result.copy()

        # AI results take precedence for key fields
        ai_priority_fields = [
            "name",
            "email",
            "phone",
            "title",
            "summary",
            "skills",
            "languages",
            "certifications",
        ]

        for field in ai_priority_fields:
            if field in ai_result and ai_result[field]:
                merged[field] = ai_result[field]

        # Merge experience with more detailed AI parsing
        if "experience" in ai_result and ai_result["experience"]:
            merged["experience"] = ai_result["experience"]

        # Merge education with better structure
        if "education" in ai_result and ai_result["education"]:
            merged["education"] = ai_result["education"]

        # Add AI-specific fields
        if "projects" in ai_result:
            merged["projects"] = ai_result["projects"]

        if "links" in ai_result:
            merged["links"] = ai_result["links"]

        if "notes" in ai_result:
            merged["ai_notes"] = ai_result["notes"]

        # Recalculate confidence score
        ai_confidence = ai_result.get("confidence", 0.0)
        basic_confidence = basic_result.get("confidence_score", 0.0) / 100.0

        # Weighted average (AI gets higher weight if available)
        if ai_confidence > 0:
            merged["confidence_score"] = (
                ai_confidence * 0.7 + basic_confidence * 0.3
            ) * 100
        else:
            merged["confidence_score"] = basic_confidence * 100

        # Update metadata
        merged["enhanced_at"] = datetime.now().isoformat()
        merged["requires_review"] = merged["confidence_score"] < 80

        return merged

    def extract_skills_from_text(self, text: str) -> List[str]:
        """Enhanced skill extraction using OpenAI"""

        if not self.openai_client:
            # Fallback to basic skill extraction
            return self._basic_skill_extraction(text)

        try:
            prompt = f"""
Extract technical skills, programming languages, frameworks, and tools from this text.
Return a JSON array of skills, focusing on:
- Programming languages (Python, JavaScript, Java, etc.)
- Frameworks (React, Django, Flask, etc.)  
- Tools (Git, Docker, AWS, etc.)
- Databases (MySQL, MongoDB, PostgreSQL, etc.)
- Technologies (REST API, GraphQL, etc.)

Text: {text[:2000]}

Return format: {{"skills": ["skill1", "skill2", "skill3"]}}
"""

            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a technical recruiter extracting skills from job descriptions or CVs.",
                    },
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
                max_tokens=500,
            )

            result = json.loads(response.choices[0].message.content)
            return result.get("skills", [])

        except Exception as e:
            logger.error(f"❌ AI skill extraction failed: {str(e)}")
            return self._basic_skill_extraction(text)

    def _basic_skill_extraction(self, text: str) -> List[str]:
        """Fallback basic skill extraction"""
        common_skills = [
            "Python",
            "JavaScript",
            "Java",
            "C++",
            "C#",
            "PHP",
            "Ruby",
            "Go",
            "Rust",
            "React",
            "Vue",
            "Angular",
            "Node.js",
            "Django",
            "Flask",
            "Laravel",
            "AWS",
            "Azure",
            "GCP",
            "Docker",
            "Kubernetes",
            "Jenkins",
            "SQL",
            "MongoDB",
            "PostgreSQL",
            "Redis",
            "Elasticsearch",
            "Git",
            "Linux",
            "API",
            "REST",
            "GraphQL",
            "Microservices",
        ]

        found_skills = []
        text_lower = text.lower()

        for skill in common_skills:
            if skill.lower() in text_lower:
                found_skills.append(skill)

        return found_skills


# Legacy function for backward compatibility
def parse_cv_file_enhanced(file_path: str) -> Dict:
    """Enhanced CV parsing function using AI"""
    parser = CVParserAI()
    return parser.parse_cv_file_enhanced(file_path)
