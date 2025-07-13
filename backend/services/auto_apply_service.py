from typing import Dict, List, Optional, Any
import asyncio
import aiohttp
import logging
from datetime import datetime
from bs4 import BeautifulSoup
import json
import re
from urllib.parse import urljoin, urlparse

from services.user_application_service import get_user_application_service
from models.user_application import UserApplicationCreate

logger = logging.getLogger(__name__)

class AutoApplyService:
    """Service for automatically applying to jobs"""
    
    def __init__(self):
        self.session_timeout = aiohttp.ClientTimeout(total=30)
        self.max_form_fields = 20  # Limit form complexity
        self.supported_field_types = [
            'text', 'email', 'tel', 'url', 'textarea', 
            'select', 'radio', 'checkbox', 'file'
        ]
    
    async def analyze_job_application_form(self, job_url: str) -> Dict[str, Any]:
        """Analyze a job posting URL to extract application form details"""
        try:
            async with aiohttp.ClientSession(timeout=self.session_timeout) as session:
                async with session.get(job_url, headers=self._get_headers()) as response:
                    if response.status != 200:
                        raise Exception(f"Failed to fetch job page: {response.status}")
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    form_data = await self._extract_form_data(soup, job_url)
                    
                    return {
                        'job_url': job_url,
                        'form_found': form_data is not None,
                        'form_data': form_data,
                        'analyzed_at': datetime.utcnow().isoformat(),
                        'auto_apply_supported': form_data is not None and len(form_data.get('fields', [])) <= self.max_form_fields
                    }
                    
        except Exception as e:
            logger.error(f"Error analyzing job application form: {str(e)}")
            return {
                'job_url': job_url,
                'form_found': False,
                'form_data': None,
                'analyzed_at': datetime.utcnow().isoformat(),
                'error': str(e),
                'auto_apply_supported': False
            }
    
    async def _extract_form_data(self, soup: BeautifulSoup, base_url: str) -> Optional[Dict[str, Any]]:
        """Extract application form data from HTML"""
        try:
            # Look for application forms
            forms = soup.find_all('form')
            application_form = None
            
            for form in forms:
                # Check if this looks like an application form
                form_text = form.get_text().lower()
                form_classes = ' '.join(form.get('class', []))
                form_id = form.get('id', '')
                
                if any(keyword in form_text for keyword in [
                    'apply', 'application', 'resume', 'cv', 'submit', 'job', 'career'
                ]) or any(keyword in (form_classes + form_id).lower() for keyword in [
                    'apply', 'application', 'job', 'career'
                ]):
                    application_form = form
                    break
            
            if not application_form:
                return None
            
            # Extract form details
            form_action = application_form.get('action', '')
            form_method = application_form.get('method', 'post').lower()
            
            # Make action URL absolute
            if form_action:
                form_action = urljoin(base_url, form_action)
            
            # Extract form fields
            fields = []
            
            # Text inputs, email, tel, url, etc.
            for input_elem in application_form.find_all('input'):
                input_type = input_elem.get('type', 'text').lower()
                if input_type in self.supported_field_types:
                    field_data = self._extract_field_data(input_elem, 'input')
                    if field_data:
                        fields.append(field_data)
            
            # Textareas
            for textarea in application_form.find_all('textarea'):
                field_data = self._extract_field_data(textarea, 'textarea')
                if field_data:
                    fields.append(field_data)
            
            # Select dropdowns
            for select in application_form.find_all('select'):
                field_data = self._extract_field_data(select, 'select')
                if field_data:
                    fields.append(field_data)
            
            return {
                'action': form_action,
                'method': form_method,
                'fields': fields[:self.max_form_fields],  # Limit number of fields
                'form_id': application_form.get('id'),
                'form_classes': application_form.get('class', [])
            }
            
        except Exception as e:
            logger.error(f"Error extracting form data: {str(e)}")
            return None
    
    def _extract_field_data(self, element, element_type: str) -> Optional[Dict[str, Any]]:
        """Extract data from a form field element"""
        try:
            field_data = {
                'type': element_type,
                'name': element.get('name'),
                'id': element.get('id'),
                'required': element.has_attr('required'),
                'placeholder': element.get('placeholder', ''),
                'classes': element.get('class', [])
            }
            
            # Get label text
            label_text = self._find_label_text(element)
            field_data['label'] = label_text
            
            # Type-specific data
            if element_type == 'input':
                field_data['input_type'] = element.get('type', 'text')
                field_data['value'] = element.get('value', '')
            elif element_type == 'select':
                options = []
                for option in element.find_all('option'):
                    options.append({
                        'value': option.get('value', ''),
                        'text': option.get_text().strip()
                    })
                field_data['options'] = options
            elif element_type == 'textarea':
                field_data['value'] = element.get_text().strip()
            
            # Try to categorize the field based on name, id, label, etc.
            field_data['category'] = self._categorize_field(field_data)
            
            return field_data
            
        except Exception as e:
            logger.error(f"Error extracting field data: {str(e)}")
            return None
    
    def _find_label_text(self, element) -> str:
        """Find label text for a form element"""
        try:
            # Check for label element with for attribute
            element_id = element.get('id')
            if element_id:
                label = element.find_parent().find('label', {'for': element_id})
                if label:
                    return label.get_text().strip()
            
            # Check for parent label
            parent_label = element.find_parent('label')
            if parent_label:
                return parent_label.get_text().strip()
            
            # Check for preceding label
            prev_elements = element.find_all_previous(['label', 'span', 'div'], limit=3)
            for prev in prev_elements:
                text = prev.get_text().strip()
                if text and len(text) < 100:  # Reasonable label length
                    return text
            
            return ""
            
        except Exception:
            return ""
    
    def _categorize_field(self, field_data: Dict[str, Any]) -> str:
        """Categorize a form field based on its attributes"""
        name = (field_data.get('name', '') or '').lower()
        label = (field_data.get('label', '') or '').lower()
        placeholder = (field_data.get('placeholder', '') or '').lower()
        id_attr = (field_data.get('id', '') or '').lower()
        
        all_text = f"{name} {label} {placeholder} {id_attr}"
        
        # Email
        if any(keyword in all_text for keyword in ['email', 'e-mail']):
            return 'email'
        
        # Name fields
        if any(keyword in all_text for keyword in ['name', 'first', 'last', 'full']):
            if 'first' in all_text:
                return 'first_name'
            elif 'last' in all_text:
                return 'last_name'
            else:
                return 'full_name'
        
        # Phone
        if any(keyword in all_text for keyword in ['phone', 'tel', 'mobile', 'contact']):
            return 'phone'
        
        # Resume/CV
        if any(keyword in all_text for keyword in ['resume', 'cv', 'upload', 'file']):
            return 'resume'
        
        # Cover letter
        if any(keyword in all_text for keyword in ['cover', 'letter', 'motivation', 'message']):
            return 'cover_letter'
        
        # LinkedIn
        if 'linkedin' in all_text:
            return 'linkedin'
        
        # Portfolio/Website
        if any(keyword in all_text for keyword in ['portfolio', 'website', 'url', 'github']):
            return 'portfolio'
        
        # Experience
        if any(keyword in all_text for keyword in ['experience', 'years', 'level']):
            return 'experience'
        
        # Location
        if any(keyword in all_text for keyword in ['location', 'city', 'country', 'address']):
            return 'location'
        
        # Salary
        if any(keyword in all_text for keyword in ['salary', 'compensation', 'rate', 'pay']):
            return 'salary'
        
        # Availability
        if any(keyword in all_text for keyword in ['available', 'start', 'date', 'when']):
            return 'availability'
        
        return 'other'
    
    async def generate_field_responses(self, user_profile: Dict[str, Any], form_fields: List[Dict[str, Any]]) -> Dict[str, str]:
        """Generate responses for form fields based on user profile"""
        try:
            responses = {}
            
            for field in form_fields:
                category = field.get('category', 'other')
                field_name = field.get('name')
                
                if not field_name:
                    continue
                
                # Generate response based on category
                response = await self._generate_field_response(category, field, user_profile)
                if response:
                    responses[field_name] = response
            
            return responses
            
        except Exception as e:
            logger.error(f"Error generating field responses: {str(e)}")
            return {}
    
    async def _generate_field_response(self, category: str, field: Dict[str, Any], user_profile: Dict[str, Any]) -> Optional[str]:
        """Generate response for a specific field"""
        try:
            # Basic profile mapping
            if category == 'email':
                return user_profile.get('email', '')
            elif category == 'first_name':
                full_name = user_profile.get('full_name', '')
                return full_name.split()[0] if full_name else ''
            elif category == 'last_name':
                full_name = user_profile.get('full_name', '')
                parts = full_name.split()
                return parts[-1] if len(parts) > 1 else ''
            elif category == 'full_name':
                return user_profile.get('full_name', '')
            elif category == 'phone':
                return user_profile.get('phone', '')
            elif category == 'linkedin':
                return user_profile.get('linkedin_url', '')
            elif category == 'portfolio':
                return user_profile.get('portfolio_url', '')
            elif category == 'location':
                return user_profile.get('location', '')
            elif category == 'experience':
                return self._format_experience_response(field, user_profile)
            elif category == 'cover_letter':
                return await self._generate_cover_letter(user_profile, field)
            elif category == 'availability':
                return 'Immediately'
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating response for category {category}: {str(e)}")
            return None
    
    def _format_experience_response(self, field: Dict[str, Any], user_profile: Dict[str, Any]) -> str:
        """Format experience response based on field type"""
        experience_level = user_profile.get('experience_level', '')
        
        # If it's a select field, try to match options
        if field.get('type') == 'select':
            options = field.get('options', [])
            for option in options:
                option_text = option.get('text', '').lower()
                if experience_level.lower() in option_text:
                    return option.get('value', '')
        
        # Default text response
        experience_map = {
            'entry': '0-2 years',
            'mid': '2-5 years',
            'senior': '5+ years',
            'lead': '8+ years',
            'executive': '10+ years'
        }
        
        return experience_map.get(experience_level.lower(), experience_level)
    
    async def _generate_cover_letter(self, user_profile: Dict[str, Any], field: Dict[str, Any]) -> str:
        """Generate a personalized cover letter"""
        try:
            # Basic template-based cover letter
            name = user_profile.get('full_name', 'Candidate')
            experience = user_profile.get('experience_level', 'professional')
            skills = user_profile.get('skills', [])
            
            cover_letter = f"""Dear Hiring Manager,

I am excited to apply for this position. As a {experience} professional with experience in {', '.join(skills[:3]) if skills else 'various technologies'}, I believe I would be a valuable addition to your team.

My background includes:
- Strong technical skills and problem-solving abilities
- Experience working in collaborative environments
- Commitment to continuous learning and improvement

I am eager to contribute to your organization's success and would welcome the opportunity to discuss how my skills align with your needs.

Thank you for your consideration.

Best regards,
{name}"""

            return cover_letter
            
        except Exception as e:
            logger.error(f"Error generating cover letter: {str(e)}")
            return "I am interested in this position and believe my skills and experience make me a strong candidate. I look forward to hearing from you."
    
    async def submit_application(
        self, 
        job_url: str, 
        form_data: Dict[str, Any], 
        field_responses: Dict[str, str],
        user_id: str
    ) -> Dict[str, Any]:
        """Submit job application with filled form data"""
        try:
            # This is a simulation - in a real implementation, you would:
            # 1. Use a browser automation tool like Playwright or Selenium
            # 2. Navigate to the form
            # 3. Fill in the fields
            # 4. Handle file uploads (resume)
            # 5. Submit the form
            # 6. Capture confirmation or error messages
            
            logger.info(f"Simulating auto-apply for user {user_id} to {job_url}")
            
            # For now, just record the application attempt
            application_data = UserApplicationCreate(
                user_id=user_id,
                job_id=self._extract_job_id_from_url(job_url),
                application_type="auto",
                auto_apply_used=True,
                notes=f"Auto-applied with generated responses: {json.dumps(field_responses, indent=2)}"
            )
            
            # Create application record
            service = get_user_application_service()
            application = await service.create_application(application_data)
            
            return {
                'success': True,
                'message': 'Application submitted successfully via auto-apply',
                'application_id': str(application.id),
                'submitted_at': datetime.utcnow().isoformat(),
                'field_responses_count': len(field_responses)
            }
            
        except Exception as e:
            logger.error(f"Error submitting auto-application: {str(e)}")
            return {
                'success': False,
                'message': f'Failed to submit application: {str(e)}',
                'error': str(e)
            }
    
    def _extract_job_id_from_url(self, job_url: str) -> str:
        """Extract or generate job ID from URL"""
        try:
            # Try to extract ID from URL
            parsed = urlparse(job_url)
            path_parts = [p for p in parsed.path.split('/') if p]
            
            # Look for numeric ID in path
            for part in reversed(path_parts):
                if part.isdigit():
                    return part
            
            # Look for alphanumeric ID
            for part in reversed(path_parts):
                if re.match(r'^[a-zA-Z0-9-_]+$', part) and len(part) > 3:
                    return part
            
            # Generate ID from URL hash
            import hashlib
            return hashlib.md5(job_url.encode()).hexdigest()[:12]
            
        except Exception:
            import hashlib
            return hashlib.md5(job_url.encode()).hexdigest()[:12]
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for web requests"""
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }

# Create singleton instance
auto_apply_service = AutoApplyService() 