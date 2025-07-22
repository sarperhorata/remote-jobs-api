from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from typing import Dict, Any, List
import logging
import os
from datetime import datetime
import openai
from pydantic import BaseModel

from ..database.db import get_async_db
from ..core.security import get_current_user
from ..utils.premium import is_premium_user
from ..models.user import UserResponse as User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/ai", tags=["ai"])

# Initialize OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

class CVAnalysisRequest(BaseModel):
    cv_url: str

class CVAnalysisResponse(BaseModel):
    overall_score: int
    strengths: List[str]
    weaknesses: List[str]
    suggestions: List[str]
    keyword_optimization: Dict[str, List[str]]
    industry_match: Dict[str, Any]
    salary_range: Dict[str, Any]
    job_recommendations: List[Dict[str, Any]]
    ai_insights: List[str]

@router.post("/cv-analysis")
async def analyze_cv(
    request: CVAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db = Depends(get_async_db)
):
    """
    Analyze CV using AI - Premium feature only
    """
    try:
        # Check if user is premium
        if not is_premium_user(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="AI CV analysis is a premium feature. Please upgrade to Premium to access this feature."
            )
        
        # Get user's CV data
        user = await db.users.find_one({"_id": current_user.id})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        profile = user.get("profile", {})
        
        # Prepare CV content for analysis
        cv_content = ""
        
        # Add basic profile information
        if profile.get("name"):
            cv_content += f"Name: {profile['name']}\n"
        if profile.get("summary"):
            cv_content += f"Summary: {profile['summary']}\n"
        
        # Add skills
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
        
        if not cv_content.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No CV content found. Please upload a CV first."
            )
        
        # Analyze CV using OpenAI
        analysis_result = await analyze_cv_with_ai(cv_content, user)
        
        # Log the analysis for premium users
        logger.info(f"AI CV analysis completed for premium user {current_user.id}")
        
        return JSONResponse({
            "success": True,
            "message": "CV analysis completed successfully",
            "data": analysis_result
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing CV: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while analyzing the CV"
        )

async def analyze_cv_with_ai(cv_content: str, user: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze CV content using OpenAI GPT-4
    """
    try:
        # Create a comprehensive prompt for CV analysis
        prompt = f"""
        Analyze the following CV and provide a comprehensive analysis. Return the result as a JSON object with the following structure:
        
        {{
            "overall_score": <score from 0-100>,
            "strengths": ["strength1", "strength2", "strength3"],
            "weaknesses": ["weakness1", "weakness2", "weakness3"],
            "suggestions": ["suggestion1", "suggestion2", "suggestion3"],
            "keyword_optimization": {{
                "missing": ["keyword1", "keyword2"],
                "suggested": ["keyword1", "keyword2"]
            }},
            "industry_match": {{
                "score": <score from 0-100>,
                "top_industries": ["industry1", "industry2", "industry3"]
            }},
            "salary_range": {{
                "min": <minimum salary>,
                "max": <maximum salary>,
                "currency": "USD"
            }},
            "job_recommendations": [
                {{
                    "title": "job title",
                    "match_score": <score from 0-100>,
                    "reason": "reason for recommendation"
                }}
            ],
            "ai_insights": ["insight1", "insight2", "insight3"]
        }}
        
        CV Content:
        {cv_content}
        
        User Profile:
        - Location: {user.get('location', 'Unknown')}
        - Experience Level: {len(user.get('profile', {}).get('experience', []))} positions
        - Skills: {len(user.get('profile', {}).get('skills', []))} skills listed
        
        Please provide a detailed, professional analysis focusing on:
        1. Overall CV quality and presentation
        2. Strengths and areas for improvement
        3. Keyword optimization for ATS systems
        4. Industry matching based on skills and experience
        5. Realistic salary range estimation
        6. Job title recommendations
        7. Actionable insights for improvement
        
        Be specific, constructive, and provide actionable feedback.
        """
        
        # Call OpenAI API
        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert CV/resume analyst and career advisor. Provide detailed, professional analysis with actionable insights."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=2000,
            temperature=0.3
        )
        
        # Parse the response
        ai_response = response.choices[0].message.content
        
        # Try to extract JSON from the response
        import json
        import re
        
        # Find JSON in the response
        json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
        if json_match:
            analysis_data = json.loads(json_match.group())
        else:
            # Fallback: create a basic analysis
            analysis_data = create_fallback_analysis(cv_content)
        
        return analysis_data
        
    except Exception as e:
        logger.error(f"Error in AI analysis: {str(e)}")
        # Return fallback analysis if AI fails
        return create_fallback_analysis(cv_content)

def create_fallback_analysis(cv_content: str) -> Dict[str, Any]:
    """
    Create a fallback analysis when AI is not available
    """
    # Basic analysis based on content length and structure
    content_length = len(cv_content)
    has_experience = "experience" in cv_content.lower()
    has_skills = "skills" in cv_content.lower()
    has_education = "education" in cv_content.lower()
    
    score = 50  # Base score
    
    if has_experience:
        score += 20
    if has_skills:
        score += 15
    if has_education:
        score += 10
    if content_length > 500:
        score += 5
    
    return {
        "overall_score": min(score, 100),
        "strengths": [
            "CV contains professional information",
            "Structured format detected",
            "Includes relevant sections"
        ],
        "weaknesses": [
            "Limited AI analysis available",
            "Consider adding more specific achievements",
            "Include quantifiable results where possible"
        ],
        "suggestions": [
            "Add specific achievements and metrics",
            "Include relevant keywords for your industry",
            "Consider professional CV review"
        ],
        "keyword_optimization": {
            "missing": ["achievement", "metrics", "results"],
            "suggested": ["leadership", "project management", "analytics"]
        },
        "industry_match": {
            "score": 60,
            "top_industries": ["Technology", "Business", "General"]
        },
        "salary_range": {
            "min": 50000,
            "max": 80000,
            "currency": "USD"
        },
        "job_recommendations": [
            {
                "title": "Professional Role",
                "match_score": 70,
                "reason": "Based on general professional experience"
            }
        ],
        "ai_insights": [
            "Consider upgrading to Premium for detailed AI analysis",
            "CV structure appears professional",
            "Add more specific achievements for better impact"
        ]
    }

@router.get("/cv-analysis/status")
async def get_cv_analysis_status(
    current_user: User = Depends(get_current_user)
):
    """
    Check if user can access CV analysis
    """
    try:
        is_premium = is_premium_user(current_user)
        
        return JSONResponse({
            "success": True,
            "data": {
                "can_access": is_premium,
                "feature": "AI CV Analysis",
                "subscription_required": not is_premium,
                "message": "Premium subscription required" if not is_premium else "Access granted"
            }
        })
        
    except Exception as e:
        logger.error(f"Error checking CV analysis status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while checking access status"
        ) 