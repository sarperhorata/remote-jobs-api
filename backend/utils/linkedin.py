import requests
import os
import logging
import json
from typing import Dict, Optional, List
import re
from datetime import datetime

logger = logging.getLogger(__name__)

class LinkedInIntegration:
    def __init__(self):
        self.client_id = os.getenv("LINKEDIN_CLIENT_ID")
        self.client_secret = os.getenv("LINKEDIN_CLIENT_SECRET")
        self.redirect_uri = os.getenv("LINKEDIN_REDIRECT_URI", "http://localhost:3000/auth/linkedin/callback")
        
    def get_authorization_url(self, state: str = None) -> str:
        """
        Generate LinkedIn OAuth authorization URL
        """
        base_url = "https://www.linkedin.com/oauth/v2/authorization"
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "r_liteprofile r_emailaddress r_basicprofile w_member_social",
            "state": state or "random_state"
        }
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{base_url}?{query_string}"
    
    def exchange_code_for_token(self, code: str) -> Optional[str]:
        """
        Exchange authorization code for access token
        """
        try:
            url = "https://www.linkedin.com/oauth/v2/accessToken"
            data = {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": self.redirect_uri,
                "client_id": self.client_id,
                "client_secret": self.client_secret
            }
            
            response = requests.post(url, data=data)
            if response.status_code == 200:
                return response.json().get("access_token")
            else:
                logger.error(f"LinkedIn token exchange failed: {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error exchanging LinkedIn code: {str(e)}")
            return None
    
    def get_user_profile(self, access_token: str) -> Optional[Dict]:
        """
        Get user profile data from LinkedIn API
        """
        try:
            headers = {"Authorization": f"Bearer {access_token}"}
            
            # Get basic profile
            profile_url = "https://api.linkedin.com/v2/people/~"
            profile_response = requests.get(profile_url, headers=headers)
            
            # Get email
            email_url = "https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))"
            email_response = requests.get(email_url, headers=headers)
            
            if profile_response.status_code == 200:
                profile_data = profile_response.json()
                email_data = email_response.json() if email_response.status_code == 200 else {}
                
                return self._format_profile_data(profile_data, email_data)
            else:
                logger.error(f"LinkedIn profile fetch failed: {profile_response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching LinkedIn profile: {str(e)}")
            return None

    def get_user_cv_data(self, access_token: str) -> Optional[Dict]:
        """
        Get comprehensive CV data from LinkedIn including experience, education, skills
        """
        try:
            headers = {"Authorization": f"Bearer {access_token}"}
            
            # Get basic profile
            profile_data = self.get_user_profile(access_token)
            if not profile_data:
                return None
            
            # Get experience
            experience_data = self._get_experience(access_token)
            
            # Get education
            education_data = self._get_education(access_token)
            
            # Get skills
            skills_data = self._get_skills(access_token)
            
            # Combine all data
            cv_data = {
                **profile_data,
                "experience": experience_data,
                "education": education_data,
                "skills": skills_data,
                "cv_source": "linkedin",
                "cv_updated_at": datetime.now().isoformat()
            }
            
            return cv_data
            
        except Exception as e:
            logger.error(f"Error fetching LinkedIn CV data: {str(e)}")
            return None

    def _get_experience(self, access_token: str) -> List[Dict]:
        """
        Get user's work experience from LinkedIn
        """
        try:
            headers = {"Authorization": f"Bearer {access_token}"}
            
            # LinkedIn API v2 for positions
            positions_url = "https://api.linkedin.com/v2/people/~:(positions)?projection=(elements*(id,title,company,startDate,endDate,summary,location))"
            response = requests.get(positions_url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                positions = data.get("positions", {}).get("elements", [])
                
                experience_list = []
                for position in positions:
                    exp = {
                        "title": position.get("title", ""),
                        "company": position.get("company", {}).get("name", ""),
                        "start_date": position.get("startDate", {}).get("year", ""),
                        "end_date": position.get("endDate", {}).get("year", "") if position.get("endDate") else "Present",
                        "summary": position.get("summary", ""),
                        "location": position.get("location", {}).get("name", "")
                    }
                    experience_list.append(exp)
                
                return experience_list
            else:
                logger.warning(f"Could not fetch experience: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching experience: {str(e)}")
            return []

    def _get_education(self, access_token: str) -> List[Dict]:
        """
        Get user's education from LinkedIn
        """
        try:
            headers = {"Authorization": f"Bearer {access_token}"}
            
            # LinkedIn API v2 for education
            education_url = "https://api.linkedin.com/v2/people/~:(educations)?projection=(elements*(id,schoolName,degreeName,fieldOfStudy,startDate,endDate,grade,activities,description))"
            response = requests.get(education_url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                educations = data.get("educations", {}).get("elements", [])
                
                education_list = []
                for education in educations:
                    edu = {
                        "school": education.get("schoolName", ""),
                        "degree": education.get("degreeName", ""),
                        "field": education.get("fieldOfStudy", ""),
                        "start_date": education.get("startDate", {}).get("year", ""),
                        "end_date": education.get("endDate", {}).get("year", ""),
                        "grade": education.get("grade", ""),
                        "activities": education.get("activities", ""),
                        "description": education.get("description", "")
                    }
                    education_list.append(edu)
                
                return education_list
            else:
                logger.warning(f"Could not fetch education: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching education: {str(e)}")
            return []

    def _get_skills(self, access_token: str) -> List[Dict]:
        """
        Get user's skills from LinkedIn
        """
        try:
            headers = {"Authorization": f"Bearer {access_token}"}
            
            # LinkedIn API v2 for skills
            skills_url = "https://api.linkedin.com/v2/people/~:(skills)?projection=(elements*(skill~(name,id)))"
            response = requests.get(skills_url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                skills = data.get("skills", {}).get("elements", [])
                
                skills_list = []
                for skill in skills:
                    skill_data = skill.get("skill", {})
                    skills_list.append({
                        "name": skill_data.get("name", ""),
                        "id": skill_data.get("id", "")
                    })
                
                return skills_list
            else:
                logger.warning(f"Could not fetch skills: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching skills: {str(e)}")
            return []
    
    def _format_profile_data(self, profile_data: Dict, email_data: Dict) -> Dict:
        """
        Format LinkedIn API response to our user schema
        """
        formatted_data = {
            "name": "",
            "email": "",
            "linkedin_url": "",
            "title": "",
            "profile_photo_url": "",
            "summary": "",
            "location": "",
            "industry": ""
        }
        
        # Extract name
        first_name = profile_data.get("localizedFirstName", "")
        last_name = profile_data.get("localizedLastName", "")
        formatted_data["name"] = f"{first_name} {last_name}".strip()
        
        # Extract email
        if email_data.get("elements"):
            email_element = email_data["elements"][0]
            formatted_data["email"] = email_element.get("handle~", {}).get("emailAddress", "")
        
        # Extract profile photo
        if "profilePicture" in profile_data:
            display_image = profile_data["profilePicture"].get("displayImage~", {})
            if display_image.get("elements"):
                largest_image = max(display_image["elements"], 
                                  key=lambda x: x.get("data", {}).get("com.linkedin.digitalmedia.mediaartifact.StillImage", {}).get("storageSize", {}).get("width", 0))
                formatted_data["profile_photo_url"] = largest_image.get("identifiers", [{}])[0].get("identifier", "")
        
        # Extract other profile fields
        formatted_data["title"] = profile_data.get("headline", "")
        formatted_data["summary"] = profile_data.get("summary", "")
        formatted_data["location"] = profile_data.get("location", {}).get("name", "")
        formatted_data["industry"] = profile_data.get("industry", "")
        
        return formatted_data

    def parse_linkedin_pdf_export(self, pdf_path: str) -> Optional[Dict]:
        """
        Parse LinkedIn PDF export to extract profile data
        """
        try:
            import pypdf
            
            with open(pdf_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
            
            return self._extract_data_from_linkedin_text(text)
            
        except Exception as e:
            logger.error(f"Error parsing LinkedIn PDF: {str(e)}")
            return None
    
    def _extract_data_from_linkedin_text(self, text: str) -> Dict:
        """
        Extract structured data from LinkedIn PDF text
        """
        data = {
            "name": "",
            "title": "",
            "experience": "",
            "education": "",
            "skills": "",
            "summary": ""
        }
        
        lines = text.split('\n')
        
        # Extract name (usually first line)
        if lines:
            data["name"] = lines[0].strip()
        
        # Extract title (usually second line)
        if len(lines) > 1:
            data["title"] = lines[1].strip()
        
        # Extract experience section
        experience_section = self._extract_section(text, "Experience", "Education")
        if experience_section:
            data["experience"] = experience_section
        
        # Extract education section
        education_section = self._extract_section(text, "Education", "Skills")
        if education_section:
            data["education"] = education_section
        
        # Extract skills section
        skills_section = self._extract_section(text, "Skills", "")
        if skills_section:
            data["skills"] = skills_section
        
        return data
    
    def _extract_section(self, text: str, start_marker: str, end_marker: str) -> str:
        """
        Extract text between two markers
        """
        start_idx = text.find(start_marker)
        if start_idx == -1:
            return ""
        
        if end_marker:
            end_idx = text.find(end_marker, start_idx)
            if end_idx != -1:
                return text[start_idx:end_idx].strip()
        
        return text[start_idx:].strip()

# Legacy function for backward compatibility
def fetch_linkedin_data(linkedin_url: str) -> Dict:
    """
    Basic LinkedIn profile data extraction from URL (limited)
    """
    try:
        # This is a simplified version - real implementation would need web scraping
        # or LinkedIn API integration
        return {
            "name": "",
            "title": "",
            "linkedin_url": linkedin_url
        }
    except Exception as e:
        logger.error(f"Error fetching LinkedIn data from URL: {str(e)}")
        return {} 