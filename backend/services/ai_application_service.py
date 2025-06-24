import aiohttp
import asyncio
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
import re
import json
import os
import logging
from datetime import datetime
import openai
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)

class AIApplicationService:
    """AI-powered job application service with form scraping and intelligent responses"""
    
    def __init__(self):
        self.openai_client = openai.AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def scrape_job_application_form(self, job_url: str) -> Dict[str, Any]:
        """
        Scrape job application form from URL and extract form fields
        """
        try:
            logger.info(f"Scraping application form from: {job_url}")
            
            async with self.session.get(job_url) as response:
                if response.status != 200:
                    raise Exception(f"Failed to fetch job page: HTTP {response.status}")
                
                html_content = await response.text()
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Extract application form information
                form_data = await self._extract_form_fields(soup, job_url)
                
                # Determine application flow type
                application_flow = self._determine_application_flow(soup, job_url)
                
                # Extract job details for context
                job_details = self._extract_job_details(soup)
                
                return {
                    "form_fields": form_data["fields"],
                    "form_action": form_data["action"],
                    "form_method": form_data["method"],
                    "application_flow": application_flow,
                    "job_details": job_details,
                    "scraped_at": datetime.utcnow().isoformat(),
                    "source_url": job_url
                }
                
        except Exception as e:
            logger.error(f"Error scraping job application form: {str(e)}")
            raise Exception(f"Failed to scrape application form: {str(e)}")

    async def _extract_form_fields(self, soup: BeautifulSoup, base_url: str) -> Dict[str, Any]:
        """Extract form fields from HTML"""
        forms = soup.find_all('form')
        application_form = None
        
        # Find the most relevant application form
        for form in forms:
            form_text = form.get_text().lower()
            if any(keyword in form_text for keyword in ['apply', 'application', 'resume', 'cv', 'cover letter']):
                application_form = form
                break
        
        if not application_form and forms:
            # Fallback to the largest form
            application_form = max(forms, key=lambda f: len(f.get_text()))
        
        if not application_form:
            return {"fields": [], "action": "", "method": "get"}
        
        form_action = application_form.get('action', '')
        if form_action and not form_action.startswith('http'):
            form_action = urljoin(base_url, form_action)
        
        form_method = application_form.get('method', 'get').lower()
        
        fields = []
        
        # Extract input fields
        inputs = application_form.find_all(['input', 'textarea', 'select'])
        
        for input_element in inputs:
            field_info = self._extract_field_info(input_element)
            if field_info:
                fields.append(field_info)
        
        return {
            "fields": fields,
            "action": form_action,
            "method": form_method
        }

    def _extract_field_info(self, element) -> Optional[Dict[str, Any]]:
        """Extract information about a form field"""
        field_type = element.name
        input_type = element.get('type', 'text') if field_type == 'input' else field_type
        
        # Skip hidden fields, buttons, and submit inputs
        if input_type in ['hidden', 'button', 'submit', 'reset', 'image']:
            return None
        
        name = element.get('name', '')
        id_attr = element.get('id', '')
        placeholder = element.get('placeholder', '')
        
        # Find associated label
        label_text = self._find_label_for_field(element)
        
        # Determine field category
        field_category = self._categorize_field(name, id_attr, label_text, placeholder)
        
        # Extract options for select fields
        options = []
        if field_type == 'select':
            option_elements = element.find_all('option')
            options = [{'value': opt.get('value', ''), 'text': opt.get_text().strip()} 
                      for opt in option_elements if opt.get('value')]
        
        return {
            "name": name,
            "id": id_attr,
            "type": input_type,
            "label": label_text,
            "placeholder": placeholder,
            "required": element.has_attr('required'),
            "category": field_category,
            "options": options
        }

    def _find_label_for_field(self, element) -> str:
        """Find the label associated with a form field"""
        # Try to find label by 'for' attribute
        field_id = element.get('id')
        if field_id:
            parent = element.find_parent('form') or element.find_parent('div', class_=True)
            if parent:
                label = parent.find('label', {'for': field_id})
                if label:
                    return label.get_text().strip()
        
        # Try to find label as parent or sibling
        parent = element.parent
        if parent:
            # Check if parent is a label
            if parent.name == 'label':
                return parent.get_text().replace(str(element), '').strip()
            
            # Check for label sibling
            label_sibling = parent.find('label')
            if label_sibling:
                return label_sibling.get_text().strip()
        
        return ""

    def _categorize_field(self, name: str, id_attr: str, label: str, placeholder: str) -> str:
        """Categorize form field based on its attributes"""
        text_to_analyze = f"{name} {id_attr} {label} {placeholder}".lower()
        
        # Personal Information
        if any(keyword in text_to_analyze for keyword in ['name', 'first', 'last', 'full']):
            if 'first' in text_to_analyze:
                return 'first_name'
            elif 'last' in text_to_analyze:
                return 'last_name'
            else:
                return 'full_name'
        
        if any(keyword in text_to_analyze for keyword in ['email', 'e-mail']):
            return 'email'
        
        if any(keyword in text_to_analyze for keyword in ['phone', 'mobile', 'tel', 'number']):
            return 'phone'
        
        if any(keyword in text_to_analyze for keyword in ['address', 'location', 'city', 'country']):
            return 'address'
        
        # Professional Information
        if any(keyword in text_to_analyze for keyword in ['resume', 'cv', 'curriculum']):
            return 'resume'
        
        if any(keyword in text_to_analyze for keyword in ['cover', 'letter', 'motivation']):
            return 'cover_letter'
        
        if any(keyword in text_to_analyze for keyword in ['experience', 'years', 'career']):
            return 'experience'
        
        if any(keyword in text_to_analyze for keyword in ['skill', 'technology', 'programming']):
            return 'skills'
        
        if any(keyword in text_to_analyze for keyword in ['education', 'degree', 'university', 'college']):
            return 'education'
        
        if any(keyword in text_to_analyze for keyword in ['salary', 'compensation', 'wage']):
            return 'salary'
        
        if any(keyword in text_to_analyze for keyword in ['start', 'available', 'date']):
            return 'start_date'
        
        # Questions
        if any(keyword in text_to_analyze for keyword in ['why', 'question', 'tell', 'describe']):
            return 'custom_question'
        
        return 'other'

    def _determine_application_flow(self, soup: BeautifulSoup, job_url: str) -> str:
        """Determine the type of application flow"""
        # Check for external redirect patterns
        apply_links = soup.find_all('a', href=True)
        for link in apply_links:
            href = link.get('href', '')
            link_text = link.get_text().lower()
            
            if 'apply' in link_text and any(domain in href for domain in ['greenhouse.io', 'lever.co', 'workday.com', 'bamboohr.com']):
                return 'external_ats'
        
        # Check for embedded forms
        forms = soup.find_all('form')
        if forms:
            return 'embedded_form'
        
        # Check for multi-step indicators
        if soup.find_all(['div', 'section'], class_=re.compile(r'step|wizard|progress')):
            return 'multi_step'
        
        return 'simple_redirect'

    def _extract_job_details(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract job details for context"""
        job_details = {}
        
        # Try to extract job title
        title_selectors = ['h1', '[class*="title"]', '[class*="job-title"]', '[id*="title"]']
        for selector in title_selectors:
            title_element = soup.select_one(selector)
            if title_element:
                job_details['title'] = title_element.get_text().strip()
                break
        
        # Try to extract company name
        company_selectors = ['[class*="company"]', '[class*="employer"]', '[data-company]']
        for selector in company_selectors:
            company_element = soup.select_one(selector)
            if company_element:
                job_details['company'] = company_element.get_text().strip()
                break
        
        # Extract description
        desc_selectors = ['[class*="description"]', '[class*="job-desc"]', '[id*="description"]']
        for selector in desc_selectors:
            desc_element = soup.select_one(selector)
            if desc_element:
                job_details['description'] = desc_element.get_text().strip()[:500] + "..."
                break
        
        return job_details

    async def generate_intelligent_responses(self, form_fields: List[Dict], user_profile: Dict, job_details: Dict) -> Dict[str, Any]:
        """Generate intelligent responses to form fields using AI"""
        try:
            logger.info("Generating AI responses for application form")
            
            responses = {}
            
            for field in form_fields:
                field_category = field.get('category', 'other')
                field_name = field.get('name', '')
                field_label = field.get('label', '')
                
                # Generate response based on field category
                if field_category in ['first_name', 'last_name', 'full_name', 'email', 'phone', 'address']:
                    # Use profile data directly for basic fields
                    responses[field_name] = self._get_profile_field(user_profile, field_category)
                
                elif field_category == 'cover_letter':
                    # Generate AI cover letter
                    cover_letter = await self._generate_cover_letter(user_profile, job_details)
                    responses[field_name] = cover_letter
                
                elif field_category == 'custom_question':
                    # Generate AI response to custom questions
                    ai_response = await self._generate_question_response(field_label, user_profile, job_details)
                    responses[field_name] = ai_response
                
                elif field_category in ['experience', 'skills', 'education']:
                    # Generate structured responses for professional fields
                    professional_response = self._get_professional_field(user_profile, field_category)
                    responses[field_name] = professional_response
                
                elif field_category == 'salary':
                    # Handle salary expectations
                    responses[field_name] = user_profile.get('salary_expectation', 'Competitive')
                
                elif field_category == 'start_date':
                    # Handle start date
                    responses[field_name] = user_profile.get('availability', 'Immediate')
            
            return responses
            
        except Exception as e:
            logger.error(f"Error generating AI responses: {str(e)}")
            raise Exception(f"Failed to generate intelligent responses: {str(e)}")

    def _get_profile_field(self, profile: Dict, category: str) -> str:
        """Get basic profile field value"""
        field_mapping = {
            'first_name': profile.get('first_name', ''),
            'last_name': profile.get('last_name', ''),
            'full_name': f"{profile.get('first_name', '')} {profile.get('last_name', '')}".strip(),
            'email': profile.get('email', ''),
            'phone': profile.get('phone', ''),
            'address': profile.get('location', '')
        }
        return field_mapping.get(category, '')

    def _get_professional_field(self, profile: Dict, category: str) -> str:
        """Get professional field value from profile"""
        if category == 'experience':
            experiences = profile.get('work_experience', [])
            if experiences:
                latest_exp = experiences[0]
                return f"{latest_exp.get('years', 0)} years of experience as {latest_exp.get('title', '')}"
            return "Experienced professional"
        
        elif category == 'skills':
            skills = profile.get('skills', [])
            return ', '.join(skills[:10]) if skills else "Relevant technical skills"
        
        elif category == 'education':
            education = profile.get('education', [])
            if education:
                latest_edu = education[0]
                return f"{latest_edu.get('degree', '')} in {latest_edu.get('field', '')}"
            return "Relevant educational background"
        
        return ""

    async def _generate_cover_letter(self, profile: Dict, job_details: Dict) -> str:
        """Generate AI-powered cover letter"""
        try:
            prompt = f"""
            Write a professional cover letter for the following job application:
            
            Job Title: {job_details.get('title', 'Software Position')}
            Company: {job_details.get('company', 'the company')}
            Job Description: {job_details.get('description', 'Not provided')}
            
            Candidate Profile:
            - Name: {profile.get('first_name', '')} {profile.get('last_name', '')}
            - Skills: {', '.join(profile.get('skills', [])[:5])}
            - Experience: {len(profile.get('work_experience', []))} positions
            - Education: {profile.get('education', [{}])[0].get('degree', 'University degree') if profile.get('education') else 'University graduate'}
            
            Requirements:
            - Keep it concise (150-250 words)
            - Professional tone
            - Highlight relevant experience and skills
            - Show enthusiasm for the role
            - Don't use overly AI-sounding language
            - Make it sound natural and human
            """
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional career advisor writing compelling cover letters."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            cover_letter = response.choices[0].message.content.strip()
            
            # Humanize the response
            humanized_letter = await self._humanize_text(cover_letter)
            
            return humanized_letter
            
        except Exception as e:
            logger.error(f"Error generating cover letter: {str(e)}")
            return f"I am excited to apply for the {job_details.get('title', 'position')} at {job_details.get('company', 'your company')}. With my background in technology and passion for innovation, I believe I would be a valuable addition to your team."

    async def _generate_question_response(self, question: str, profile: Dict, job_details: Dict) -> str:
        """Generate AI response to custom application questions"""
        try:
            prompt = f"""
            Answer this job application question professionally:
            
            Question: {question}
            
            Context:
            - Job: {job_details.get('title', 'Software Position')}
            - Company: {job_details.get('company', 'the company')}
            
            Candidate Background:
            - Skills: {', '.join(profile.get('skills', [])[:5])}
            - Experience: {len(profile.get('work_experience', []))} relevant positions
            
            Requirements:
            - Answer should be 50-150 words
            - Professional and specific
            - Relate to the candidate's background
            - Sound natural and human
            - Avoid clichés and buzzwords
            """
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are helping a candidate answer job application questions authentically."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.8
            )
            
            answer = response.choices[0].message.content.strip()
            
            # Humanize the response
            humanized_answer = await self._humanize_text(answer)
            
            return humanized_answer
            
        except Exception as e:
            logger.error(f"Error generating question response: {str(e)}")
            return "I'm excited about this opportunity and believe my experience aligns well with your requirements. I look forward to contributing to your team's success."

    async def _humanize_text(self, text: str) -> str:
        """Humanize AI-generated text to sound more natural"""
        try:
            prompt = f"""
            Make this text sound more natural and human while keeping the same meaning:
            
            Original text: {text}
            
            Requirements:
            - Remove overly formal language
            - Add subtle imperfections that humans make
            - Use more conversational tone
            - Keep the same length and meaning
            - Make it sound genuine
            """
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert at making AI text sound more human and natural."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=len(text.split()) * 2,
                temperature=0.9
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error humanizing text: {str(e)}")
            return text  # Return original if humanization fails

    async def submit_application(self, form_data: Dict, responses: Dict, job_url: str) -> Dict[str, Any]:
        """Submit the job application with generated responses"""
        try:
            logger.info(f"Submitting application to: {form_data.get('form_action', job_url)}")
            
            submit_url = form_data.get('form_action') or job_url
            method = form_data.get('form_method', 'post').upper()
            
            # Prepare form payload
            payload = {}
            for field in form_data.get('form_fields', []):
                field_name = field.get('name')
                if field_name and field_name in responses:
                    payload[field_name] = responses[field_name]
            
            # Submit the form
            if method == 'POST':
                async with self.session.post(submit_url, data=payload) as response:
                    response_text = await response.text()
                    success = self._detect_submission_success(response_text, response.status)
            else:
                async with self.session.get(submit_url, params=payload) as response:
                    response_text = await response.text()
                    success = self._detect_submission_success(response_text, response.status)
            
            return {
                "success": success,
                "status_code": response.status,
                "submitted_at": datetime.utcnow().isoformat(),
                "form_url": submit_url,
                "responses_count": len(payload)
            }
            
        except Exception as e:
            logger.error(f"Error submitting application: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "submitted_at": datetime.utcnow().isoformat()
            }

    def _detect_submission_success(self, response_text: str, status_code: int) -> bool:
        """Detect if form submission was successful"""
        # Check status code
        if status_code >= 400:
            return False
        
        # Check for success indicators in response text
        success_indicators = [
            'thank you', 'success', 'submitted', 'received', 'confirmation',
            'application sent', 'we will review', 'next steps'
        ]
        
        error_indicators = [
            'error', 'failed', 'invalid', 'required field', 'missing',
            'please try again', 'something went wrong'
        ]
        
        response_lower = response_text.lower()
        
        # Check for error indicators first
        if any(indicator in response_lower for indicator in error_indicators):
            return False
        
        # Check for success indicators
        if any(indicator in response_lower for indicator in success_indicators):
            return True
        
        # Default to success if no clear indicators and status is ok
        return status_code < 400

# Export the service
__all__ = ['AIApplicationService'] 