import logging
import asyncio
from datetime import datetime
from typing import List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGODB_URL, OPENAI_API_KEY
import openai

logger = logging.getLogger(__name__)

class JobAnalyzer:
    def __init__(self):
        self.client = AsyncIOMotorClient(MONGODB_URL)
        self.db = self.client.buzz2remote
        self.jobs_collection = self.db.jobs
        
        # Initialize OpenAI
        openai.api_key = OPENAI_API_KEY
    
    async def analyze_all_jobs(self):
        """Analyze all unanalyzed jobs"""
        try:
            # Get unanalyzed jobs
            unanalyzed_jobs = await self.jobs_collection.find({
                "analyzed": {"$ne": True}
            }).to_list(length=None)
            
            if not unanalyzed_jobs:
                logger.info("No unanalyzed jobs found")
                return
            
            logger.info(f"Found {len(unanalyzed_jobs)} unanalyzed jobs")
            
            # Process jobs in batches
            batch_size = 10
            for i in range(0, len(unanalyzed_jobs), batch_size):
                batch = unanalyzed_jobs[i:i + batch_size]
                tasks = [self.analyze_job(job) for job in batch]
                await asyncio.gather(*tasks, return_exceptions=True)
                
                logger.info(f"Processed batch {i//batch_size + 1}/{(len(unanalyzed_jobs) + batch_size - 1)//batch_size}")
        
        except Exception as e:
            logger.error(f"Error analyzing jobs: {str(e)}")
            raise
    
    async def analyze_job(self, job: Dict[str, Any]):
        """Analyze a single job using OpenAI"""
        try:
            # Prepare job description for analysis
            description = f"Title: {job['title']}\nCompany: {job['company']}\nDescription: {job['description']}"
            
            # Get analysis from OpenAI
            analysis = await self._get_openai_analysis(description)
            
            # Update job with analysis results
            await self.jobs_collection.update_one(
                {"_id": job["_id"]},
                {
                    "$set": {
                        "analyzed": True,
                        "analysis": analysis,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            logger.info(f"Successfully analyzed job: {job['title']} at {job['company']}")
        
        except Exception as e:
            logger.error(f"Error analyzing job {job.get('_id')}: {str(e)}")
            raise
    
    async def _get_openai_analysis(self, description: str) -> Dict[str, Any]:
        """Get job analysis from OpenAI"""
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": """Analyze the job posting and provide the following information:
                        1. Required skills and technologies
                        2. Experience level (Junior, Mid, Senior)
                        3. Job category (e.g., Frontend, Backend, Full Stack, DevOps)
                        4. Salary range (if mentioned)
                        5. Key responsibilities
                        6. Company culture indicators
                        7. Remote work specifics
                        Format the response as a JSON object with these fields."""
                    },
                    {
                        "role": "user",
                        "content": description
                    }
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            # Parse the response
            analysis_text = response.choices[0].message.content
            return {
                "skills": self._extract_skills(analysis_text),
                "experience_level": self._extract_experience_level(analysis_text),
                "category": self._extract_category(analysis_text),
                "salary_range": self._extract_salary_range(analysis_text),
                "responsibilities": self._extract_responsibilities(analysis_text),
                "company_culture": self._extract_company_culture(analysis_text),
                "remote_specifics": self._extract_remote_specifics(analysis_text),
                "raw_analysis": analysis_text
            }
        
        except Exception as e:
            logger.error(f"Error getting OpenAI analysis: {str(e)}")
            raise
    
    def _extract_skills(self, analysis: str) -> List[str]:
        """Extract required skills from analysis"""
        # Implementation depends on the exact format of the analysis
        # This is a placeholder implementation
        return []
    
    def _extract_experience_level(self, analysis: str) -> str:
        """Extract experience level from analysis"""
        # Implementation depends on the exact format of the analysis
        # This is a placeholder implementation
        return "Not specified"
    
    def _extract_category(self, analysis: str) -> str:
        """Extract job category from analysis"""
        # Implementation depends on the exact format of the analysis
        # This is a placeholder implementation
        return "Not specified"
    
    def _extract_salary_range(self, analysis: str) -> str:
        """Extract salary range from analysis"""
        # Implementation depends on the exact format of the analysis
        # This is a placeholder implementation
        return "Not specified"
    
    def _extract_responsibilities(self, analysis: str) -> List[str]:
        """Extract key responsibilities from analysis"""
        # Implementation depends on the exact format of the analysis
        # This is a placeholder implementation
        return []
    
    def _extract_company_culture(self, analysis: str) -> List[str]:
        """Extract company culture indicators from analysis"""
        # Implementation depends on the exact format of the analysis
        # This is a placeholder implementation
        return []
    
    def _extract_remote_specifics(self, analysis: str) -> Dict[str, Any]:
        """Extract remote work specifics from analysis"""
        # Implementation depends on the exact format of the analysis
        # This is a placeholder implementation
        return {
            "timezone_requirements": "Not specified",
            "location_restrictions": "Not specified",
            "communication_tools": "Not specified"
        }

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Run the analyzer
    analyzer = JobAnalyzer()
    asyncio.run(analyzer.analyze_all_jobs()) 