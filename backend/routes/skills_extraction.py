import os
import logging
import json
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File
from fastapi.responses import JSONResponse
from datetime import datetime
import openai
from bson import ObjectId

from ..database.db import get_async_db
from ..core.security import get_current_user
from ..models.user import UserResponse as User
from ..utils.premium import is_premium_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/skills", tags=["skills-extraction"])

# OpenAI configuration
openai.api_key = os.getenv("OPENAI_API_KEY")

class SkillsExtractionService:
    """Service for extracting skills from CV content"""
    
    def __init__(self):
        self.technical_skills = {
            'programming_languages': [
                'Python', 'JavaScript', 'TypeScript', 'Java', 'C++', 'C#', 'PHP', 'Ruby', 'Go', 'Rust', 'Swift', 'Kotlin', 'Scala', 'R', 'MATLAB'
            ],
            'frameworks': [
                'React', 'Angular', 'Vue', 'Svelte', 'Node.js', 'Express', 'Django', 'Flask', 'Spring', 'ASP.NET', 'Laravel', 'Rails', 'FastAPI'
            ],
            'databases': [
                'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Elasticsearch', 'SQLite', 'Oracle', 'SQL Server', 'Cassandra', 'DynamoDB'
            ],
            'cloud_platforms': [
                'AWS', 'Azure', 'GCP', 'Google Cloud', 'Heroku', 'DigitalOcean', 'Vercel', 'Netlify', 'Firebase'
            ],
            'devops_tools': [
                'Docker', 'Kubernetes', 'Jenkins', 'Travis CI', 'CircleCI', 'GitHub Actions', 'Terraform', 'Ansible', 'GitLab CI'
            ],
            'version_control': [
                'Git', 'GitHub', 'GitLab', 'Bitbucket', 'SVN'
            ],
            'api_technologies': [
                'REST', 'GraphQL', 'gRPC', 'WebSockets', 'SOAP', 'API'
            ],
            'architecture': [
                'Microservices', 'Serverless', 'Monolith', 'Event-Driven', 'Domain-Driven Design'
            ],
            'methodologies': [
                'CI/CD', 'DevOps', 'Agile', 'Scrum', 'Kanban', 'TDD', 'BDD', 'Lean'
            ]
        }
        
        self.soft_skills = [
            'Leadership', 'Communication', 'Teamwork', 'Problem Solving', 'Critical Thinking', 
            'Time Management', 'Adaptability', 'Creativity', 'Emotional Intelligence', 'Negotiation',
            'Project Management', 'Customer Service', 'Analytical Thinking', 'Strategic Planning'
        ]
        
        self.languages = [
            'English', 'Turkish', 'German', 'French', 'Spanish', 'Italian', 'Portuguese', 
            'Russian', 'Chinese', 'Japanese', 'Korean', 'Arabic', 'Dutch', 'Swedish', 'Norwegian'
        ]

    async def extract_skills_from_cv(self, cv_content: str, user: Dict[str, Any]) -> Dict[str, Any]:
        """Extract skills from CV content using AI and pattern matching"""
        try:
            # First, try AI extraction if available
            ai_skills = await self._extract_skills_with_ai(cv_content)
            
            # Then, use pattern matching as fallback
            pattern_skills = self._extract_skills_with_patterns(cv_content)
            
            # Merge and deduplicate skills
            merged_skills = self._merge_skills(ai_skills, pattern_skills)
            
            # Categorize skills
            categorized_skills = self._categorize_skills(merged_skills)
            
            # Calculate confidence scores
            skills_with_confidence = self._calculate_confidence_scores(categorized_skills, cv_content)
            
            return {
                "skills": skills_with_confidence,
                "summary": {
                    "total_skills": len(skills_with_confidence),
                    "technical_count": len([s for s in skills_with_confidence if s.get('category') == 'technical']),
                    "soft_count": len([s for s in skills_with_confidence if s.get('category') == 'soft']),
                    "languages_count": len([s for s in skills_with_confidence if s.get('category') == 'languages']),
                    "tools_count": len([s for s in skills_with_confidence if s.get('category') == 'tools']),
                    "certifications_count": len([s for s in skills_with_confidence if s.get('category') == 'certifications'])
                },
                "extraction_method": "ai_enhanced" if ai_skills else "pattern_matching",
                "confidence_score": self._calculate_overall_confidence(skills_with_confidence),
                "extracted_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error extracting skills from CV: {str(e)}")
            # Fallback to basic pattern matching
            return await self._fallback_extraction(cv_content)

    async def _extract_skills_with_ai(self, cv_content: str) -> List[Dict[str, Any]]:
        """Extract skills using OpenAI GPT-4"""
        if not openai.api_key:
            return []
            
        try:
            prompt = f"""
            Extract all skills, technologies, and expertise from this CV/resume. Return a JSON array of skills with the following structure:
            
            {{
                "skills": [
                    {{
                        "name": "skill name",
                        "category": "technical|soft|languages|tools|certifications",
                        "confidence": 0-100,
                        "source": "cv"
                    }}
                ]
            }}
            
            Guidelines:
            1. Focus on technical skills, programming languages, frameworks, tools, platforms
            2. Include soft skills like leadership, communication, teamwork
            3. Include languages (English, Turkish, etc.)
            4. Include certifications and qualifications
            5. Normalize skill names (e.g., "JS" -> "JavaScript", "React.js" -> "React")
            6. Set confidence based on how clearly the skill is mentioned
            7. Categorize appropriately
            
            CV Content:
            {cv_content[:3000]}
            """
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a professional CV parser specializing in skill extraction. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
                max_tokens=1000
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get("skills", [])
            
        except Exception as e:
            logger.error(f"AI skill extraction failed: {str(e)}")
            return []

    def _extract_skills_with_patterns(self, cv_content: str) -> List[Dict[str, Any]]:
        """Extract skills using pattern matching"""
        skills = []
        content_lower = cv_content.lower()
        
        # Extract technical skills
        for category, skill_list in self.technical_skills.items():
            for skill in skill_list:
                if skill.lower() in content_lower:
                    skills.append({
                        "name": skill,
                        "category": "technical",
                        "confidence": 85,
                        "source": "cv"
                    })
        
        # Extract soft skills
        for skill in self.soft_skills:
            if skill.lower() in content_lower:
                skills.append({
                    "name": skill,
                    "category": "soft",
                    "confidence": 80,
                    "source": "cv"
                })
        
        # Extract languages
        for language in self.languages:
            if language.lower() in content_lower:
                skills.append({
                    "name": language,
                    "category": "languages",
                    "confidence": 90,
                    "source": "cv"
                })
        
        return skills

    def _merge_skills(self, ai_skills: List[Dict], pattern_skills: List[Dict]) -> List[Dict[str, Any]]:
        """Merge AI and pattern extracted skills, removing duplicates"""
        merged = {}
        
        # Add pattern skills first
        for skill in pattern_skills:
            key = skill['name'].lower()
            merged[key] = skill
        
        # Add AI skills, preferring AI results for conflicts
        for skill in ai_skills:
            key = skill['name'].lower()
            if key in merged:
                # If AI confidence is higher, replace
                if skill.get('confidence', 0) > merged[key].get('confidence', 0):
                    merged[key] = skill
            else:
                merged[key] = skill
        
        return list(merged.values())

    def _categorize_skills(self, skills: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Categorize skills more accurately"""
        for skill in skills:
            if not skill.get('category'):
                skill['category'] = self._determine_category(skill['name'])
        
        return skills

    def _determine_category(self, skill_name: str) -> str:
        """Determine the category of a skill based on its name"""
        skill_lower = skill_name.lower()
        
        # Check technical skills
        for category, skills in self.technical_skills.items():
            if skill_lower in [s.lower() for s in skills]:
                return "technical"
        
        # Check soft skills
        if skill_lower in [s.lower() for s in self.soft_skills]:
            return "soft"
        
        # Check languages
        if skill_lower in [s.lower() for s in self.languages]:
            return "languages"
        
        # Default to tools if it looks like a tool/platform
        if any(keyword in skill_lower for keyword in ['tool', 'platform', 'software', 'system', 'service']):
            return "tools"
        
        return "technical"  # Default category

    def _calculate_confidence_scores(self, skills: List[Dict[str, Any]], cv_content: str) -> List[Dict[str, Any]]:
        """Calculate confidence scores for extracted skills"""
        for skill in skills:
            if 'confidence' not in skill:
                skill['confidence'] = self._calculate_skill_confidence(skill, cv_content)
        
        return skills

    def _calculate_skill_confidence(self, skill: Dict[str, Any], cv_content: str) -> int:
        """Calculate confidence score for a specific skill"""
        skill_name = skill['name'].lower()
        content_lower = cv_content.lower()
        
        # Base confidence
        confidence = 70
        
        # Increase confidence based on context
        if skill_name in content_lower:
            confidence += 10
            
            # Check for skill sections
            if any(section in content_lower for section in ['skills:', 'technologies:', 'tools:', 'languages:']):
                confidence += 10
            
            # Check for experience mentions
            if any(word in content_lower for word in ['experience', 'worked with', 'used', 'implemented']):
                confidence += 5
            
            # Check for project mentions
            if any(word in content_lower for word in ['project', 'developed', 'built', 'created']):
                confidence += 5
        
        return min(confidence, 100)

    def _calculate_overall_confidence(self, skills: List[Dict[str, Any]]) -> float:
        """Calculate overall confidence score for the extraction"""
        if not skills:
            return 0.0
        
        total_confidence = sum(skill.get('confidence', 0) for skill in skills)
        return round(total_confidence / len(skills), 1)

    async def _fallback_extraction(self, cv_content: str) -> Dict[str, Any]:
        """Fallback extraction method"""
        pattern_skills = self._extract_skills_with_patterns(cv_content)
        categorized_skills = self._categorize_skills(pattern_skills)
        skills_with_confidence = self._calculate_confidence_scores(categorized_skills, cv_content)
        
        return {
            "skills": skills_with_confidence,
            "summary": {
                "total_skills": len(skills_with_confidence),
                "technical_count": len([s for s in skills_with_confidence if s.get('category') == 'technical']),
                "soft_count": len([s for s in skills_with_confidence if s.get('category') == 'soft']),
                "languages_count": len([s for s in skills_with_confidence if s.get('category') == 'languages']),
                "tools_count": len([s for s in skills_with_confidence if s.get('category') == 'tools']),
                "certifications_count": len([s for s in skills_with_confidence if s.get('category') == 'certifications'])
            },
            "extraction_method": "pattern_matching",
            "confidence_score": self._calculate_overall_confidence(skills_with_confidence),
            "extracted_at": datetime.now().isoformat()
        }

# Initialize service
skills_service = SkillsExtractionService()

@router.post("/extract-from-cv")
async def extract_skills_from_cv(
    current_user: User = Depends(get_current_user),
    db = Depends(get_async_db)
):
    """
    Extract skills from user's uploaded CV
    """
    try:
        # Get user's CV data
        user = await db.users.find_one({"_id": current_user.id})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        profile = user.get("profile", {})
        
        # Check if user has CV uploaded
        if not profile.get("cv_url"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No CV uploaded. Please upload a CV first."
            )
        
        # Prepare CV content for analysis
        cv_content = ""
        
        # Add basic profile information
        if profile.get("name"):
            cv_content += f"Name: {profile['name']}\n"
        if profile.get("summary"):
            cv_content += f"Summary: {profile['summary']}\n"
        
        # Add existing skills
        if profile.get("skills"):
            cv_content += f"Skills: {', '.join(profile['skills'])}\n"
        
        # Add experience
        if profile.get("experience"):
            cv_content += "\nExperience:\n"
            for exp in profile["experience"]:
                cv_content += f"- {exp.get('title', '')} at {exp.get('company', '')}\n"
                cv_content += f"  {exp.get('description', '')}\n"
        
        # Add education
        if profile.get("education"):
            cv_content += "\nEducation:\n"
            for edu in profile["education"]:
                cv_content += f"- {edu.get('degree', '')} in {edu.get('field', '')} from {edu.get('school', '')}\n"
        
        # Extract skills
        extraction_result = await skills_service.extract_skills_from_cv(cv_content, user)
        
        # Update user profile with extracted skills
        extracted_skills = extraction_result["skills"]
        skill_names = [skill["name"] for skill in extracted_skills]
        
        await db.users.update_one(
            {"_id": current_user.id},
            {
                "$set": {
                    "profile.skills": skill_names,
                    "profile.extracted_skills": extracted_skills,
                    "profile.skills_extracted_at": datetime.now(),
                    "updated_at": datetime.now()
                }
            }
        )
        
        logger.info(f"Skills extracted successfully for user {current_user.id}: {len(extracted_skills)} skills found")
        
        return JSONResponse({
            "success": True,
            "message": f"Successfully extracted {len(extracted_skills)} skills from your CV",
            "data": extraction_result
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error extracting skills: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while extracting skills"
        )

@router.post("/extract-from-file")
async def extract_skills_from_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db = Depends(get_async_db)
):
    """
    Extract skills from uploaded CV file
    """
    try:
        # Validate file type
        allowed_extensions = ['.pdf', '.doc', '.docx', '.txt']
        file_extension = '.' + file.filename.split('.')[-1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file format. Allowed formats: {', '.join(allowed_extensions)}"
            )
        
        # Read file content
        file_content = await file.read()
        
        # For now, we'll assume text content
        # In a real implementation, you'd use a PDF/DOC parser
        cv_content = file_content.decode('utf-8', errors='ignore')
        
        # Get user data
        user = await db.users.find_one({"_id": current_user.id})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Extract skills
        extraction_result = await skills_service.extract_skills_from_cv(cv_content, user)
        
        return JSONResponse({
            "success": True,
            "message": f"Successfully extracted {len(extraction_result['skills'])} skills from uploaded file",
            "data": extraction_result
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error extracting skills from file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing the file"
        )

@router.get("/user-skills")
async def get_user_skills(
    current_user: User = Depends(get_current_user),
    db = Depends(get_async_db)
):
    """
    Get user's extracted skills
    """
    try:
        user = await db.users.find_one({"_id": current_user.id})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        profile = user.get("profile", {})
        extracted_skills = profile.get("extracted_skills", [])
        skills = profile.get("skills", [])
        
        return {
            "skills": skills,
            "extracted_skills": extracted_skills,
            "skills_extracted_at": profile.get("skills_extracted_at"),
            "total_skills": len(skills)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user skills: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching skills"
        )

@router.put("/update-skills")
async def update_user_skills(
    skills_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db = Depends(get_async_db)
):
    """
    Update user's skills
    """
    try:
        skills = skills_data.get("skills", [])
        
        # Update user profile
        await db.users.update_one(
            {"_id": current_user.id},
            {
                "$set": {
                    "profile.skills": skills,
                    "profile.extracted_skills": skills_data.get("extracted_skills", []),
                    "updated_at": datetime.now()
                }
            }
        )
        
        logger.info(f"Skills updated for user {current_user.id}: {len(skills)} skills")
        
        return {
            "success": True,
            "message": "Skills updated successfully",
            "total_skills": len(skills)
        }
        
    except Exception as e:
        logger.error(f"Error updating user skills: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating skills"
        )

@router.get("/suggestions")
async def get_skill_suggestions(
    query: str = "",
    limit: int = 10,
    current_user: User = Depends(get_current_user)
):
    """
    Get skill suggestions for autocomplete
    """
    try:
        if not query or len(query) < 2:
            return {"suggestions": []}
        
        # Combine all available skills
        all_skills = []
        
        # Add technical skills
        for category, skills in skills_service.technical_skills.items():
            all_skills.extend(skills)
        
        # Add soft skills
        all_skills.extend(skills_service.soft_skills)
        
        # Add languages
        all_skills.extend(skills_service.languages)
        
        # Filter by query
        suggestions = [
            skill for skill in all_skills 
            if query.lower() in skill.lower()
        ][:limit]
        
        return {
            "suggestions": suggestions,
            "query": query
        }
        
    except Exception as e:
        logger.error(f"Error getting skill suggestions: {str(e)}")
        return {"suggestions": [], "query": query} 