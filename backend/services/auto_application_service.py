import asyncio
import aiohttp
from typing import Dict, List, Any, Optional, Tuple
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging
import time
import os
from .job_scraping_service import JobScrapingService

logger = logging.getLogger(__name__)

class AutoApplicationService:
    """
    Service for automated job applications with AI assistance (v3)
    """
    
    def __init__(self):
        self.driver = None
        self.scraping_service = JobScrapingService()
        
    def _setup_driver(self) -> webdriver.Chrome:
        """
        Setup Chrome WebDriver for automation
        """
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Run in background
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        
        # Add additional options for better compatibility
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        
        try:
            driver = webdriver.Chrome(options=chrome_options)
            # Execute script to hide webdriver presence
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            return driver
        except Exception as e:
            logger.error(f"Failed to setup Chrome driver: {str(e)}")
            raise

    async def submit_automated_application(
        self,
        job_data: Dict[str, Any],
        user_profile: Dict[str, Any],
        application_url: str,
        preferences: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Submit automated application using Selenium and AI
        """
        try:
            self.driver = self._setup_driver()
            
            # Step 1: Navigate to application page
            logger.info(f"Navigating to application URL: {application_url}")
            self.driver.get(application_url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            
            # Step 2: Detect and handle different application flow types
            application_flow = await self._detect_application_flow()
            
            if application_flow == "external_redirect":
                return await self._handle_external_redirect()
            elif application_flow == "embedded_form":
                return await self._handle_embedded_form(job_data, user_profile, preferences)
            elif application_flow == "multi_step":
                return await self._handle_multi_step_application(job_data, user_profile, preferences)
            else:
                return {
                    "success": False,
                    "error": "Could not determine application flow type",
                    "suggestions": ["Try applying manually on the company website"]
                }
                
        except Exception as e:
            logger.error(f"Error in automated application: {str(e)}")
            return {
                "success": False,
                "error": f"Automation failed: {str(e)}",
                "fallback_required": True
            }
        finally:
            if self.driver:
                self.driver.quit()

    async def _detect_application_flow(self) -> str:
        """
        Detect the type of application flow on the current page
        """
        try:
            # Look for form elements
            forms = self.driver.find_elements(By.TAG_NAME, "form")
            
            # Check for external apply buttons
            external_buttons = self.driver.find_elements(
                By.XPATH, 
                "//a[contains(text(), 'Apply') or contains(text(), 'apply')] | //button[contains(text(), 'Apply') or contains(text(), 'apply')]"
            )
            
            # Check if there are forms with job application fields
            if forms:
                for form in forms:
                    form_text = form.text.lower()
                    if any(keyword in form_text for keyword in ['name', 'email', 'resume', 'cv', 'experience']):
                        # Check if it's a multi-step form
                        step_indicators = self.driver.find_elements(
                            By.XPATH,
                            "//*[contains(text(), 'step') or contains(text(), 'Step') or contains(@class, 'step')]"
                        )
                        if step_indicators:
                            return "multi_step"
                        else:
                            return "embedded_form"
            
            # If external buttons found but no embedded forms
            if external_buttons:
                return "external_redirect"
            
            return "unknown"
            
        except Exception as e:
            logger.error(f"Error detecting application flow: {str(e)}")
            return "unknown"

    async def _handle_external_redirect(self) -> Dict[str, Any]:
        """
        Handle external redirect applications
        """
        try:
            # Find and click apply button
            apply_buttons = self.driver.find_elements(
                By.XPATH,
                "//a[contains(text(), 'Apply') or contains(text(), 'apply')] | //button[contains(text(), 'Apply') or contains(text(), 'apply')]"
            )
            
            if apply_buttons:
                original_window = self.driver.current_window_handle
                apply_buttons[0].click()
                
                # Wait for potential new tab/window
                time.sleep(3)
                
                # Check if new window opened
                if len(self.driver.window_handles) > 1:
                    self.driver.switch_to.window(self.driver.window_handles[-1])
                
                new_url = self.driver.current_url
                
                return {
                    "success": True,
                    "message": "Redirected to external application page",
                    "details": {
                        "redirect_url": new_url,
                        "requires_manual_completion": True
                    },
                    "next_action": "manual_completion"
                }
            else:
                return {
                    "success": False,
                    "error": "No apply button found",
                    "suggestions": ["Look for application links manually"]
                }
                
        except Exception as e:
            logger.error(f"Error handling external redirect: {str(e)}")
            return {
                "success": False,
                "error": f"External redirect failed: {str(e)}"
            }

    async def _handle_embedded_form(
        self,
        job_data: Dict[str, Any],
        user_profile: Dict[str, Any],
        preferences: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Handle embedded application forms
        """
        try:
            # Find form elements
            form_elements = self._find_form_elements()
            
            if not form_elements:
                return {
                    "success": False,
                    "error": "No form elements found"
                }
            
            # Auto-fill form with user data
            filled_fields = await self._auto_fill_form(form_elements, user_profile, job_data)
            
            # Handle file uploads (resume, cover letter)
            upload_results = await self._handle_file_uploads(user_profile)
            
            # Submit the form
            submission_result = await self._submit_form()
            
            if submission_result["success"]:
                return {
                    "success": True,
                    "message": "Application submitted successfully",
                    "details": {
                        "filled_fields": len(filled_fields),
                        "uploaded_files": upload_results,
                        "submission_confirmation": submission_result.get("confirmation")
                    },
                    "auto_fill_data": filled_fields
                }
            else:
                return {
                    "success": False,
                    "error": "Form submission failed",
                    "details": submission_result
                }
                
        except Exception as e:
            logger.error(f"Error handling embedded form: {str(e)}")
            return {
                "success": False,
                "error": f"Embedded form processing failed: {str(e)}"
            }

    async def _handle_multi_step_application(
        self,
        job_data: Dict[str, Any],
        user_profile: Dict[str, Any],
        preferences: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Handle multi-step application processes
        """
        try:
            steps_completed = 0
            max_steps = 10  # Safety limit
            
            while steps_completed < max_steps:
                # Detect current step
                current_step = self._detect_current_step()
                
                if current_step == "personal_info":
                    await self._fill_personal_info_step(user_profile)
                elif current_step == "resume_upload":
                    await self._fill_resume_step(user_profile)
                elif current_step == "cover_letter":
                    await self._fill_cover_letter_step(user_profile, job_data)
                elif current_step == "questions":
                    await self._fill_questions_step(user_profile, job_data)
                elif current_step == "review":
                    await self._handle_review_step()
                elif current_step == "complete":
                    break
                else:
                    # Generic form filling
                    form_elements = self._find_form_elements()
                    if form_elements:
                        await self._auto_fill_form(form_elements, user_profile, job_data)
                
                # Try to go to next step
                if not await self._go_to_next_step():
                    break
                    
                steps_completed += 1
                time.sleep(2)  # Wait between steps
            
            # Check if application was completed
            if self._is_application_completed():
                return {
                    "success": True,
                    "message": "Multi-step application completed successfully",
                    "details": {
                        "steps_completed": steps_completed,
                        "completion_detected": True
                    }
                }
            else:
                return {
                    "success": False,
                    "error": "Application process did not complete",
                    "details": {
                        "steps_completed": steps_completed,
                        "last_step": current_step
                    }
                }
                
        except Exception as e:
            logger.error(f"Error handling multi-step application: {str(e)}")
            return {
                "success": False,
                "error": f"Multi-step application failed: {str(e)}"
            }

    def _find_form_elements(self) -> List[Dict[str, Any]]:
        """
        Find and categorize form elements on the page
        """
        elements = []
        
        # Find input fields
        inputs = self.driver.find_elements(By.TAG_NAME, "input")
        for input_elem in inputs:
            input_type = input_elem.get_attribute("type") or "text"
            if input_type not in ["hidden", "submit", "button"]:
                elements.append({
                    "element": input_elem,
                    "type": input_type,
                    "name": input_elem.get_attribute("name"),
                    "id": input_elem.get_attribute("id"),
                    "label": self._find_element_label(input_elem),
                    "required": input_elem.get_attribute("required") is not None
                })
        
        # Find textarea elements
        textareas = self.driver.find_elements(By.TAG_NAME, "textarea")
        for textarea in textareas:
            elements.append({
                "element": textarea,
                "type": "textarea",
                "name": textarea.get_attribute("name"),
                "id": textarea.get_attribute("id"),
                "label": self._find_element_label(textarea),
                "required": textarea.get_attribute("required") is not None
            })
        
        # Find select elements
        selects = self.driver.find_elements(By.TAG_NAME, "select")
        for select in selects:
            elements.append({
                "element": select,
                "type": "select",
                "name": select.get_attribute("name"),
                "id": select.get_attribute("id"),
                "label": self._find_element_label(select),
                "required": select.get_attribute("required") is not None
            })
        
        return elements

    def _find_element_label(self, element) -> str:
        """
        Find the label text for a form element
        """
        try:
            # Try to find label by 'for' attribute
            element_id = element.get_attribute("id")
            if element_id:
                label = self.driver.find_element(By.XPATH, f"//label[@for='{element_id}']")
                if label:
                    return label.text.strip()
        except:
            pass
        
        try:
            # Try to find label in parent container
            parent = element.find_element(By.XPATH, "./..")
            label = parent.find_element(By.TAG_NAME, "label")
            if label:
                return label.text.strip()
        except:
            pass
        
        # Fallback to name or placeholder
        name = element.get_attribute("name") or ""
        placeholder = element.get_attribute("placeholder") or ""
        
        return placeholder or name.replace("_", " ").title()

    async def _auto_fill_form(
        self,
        form_elements: List[Dict[str, Any]],
        user_profile: Dict[str, Any],
        job_data: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Auto-fill form elements based on user profile and job data
        """
        filled_fields = {}
        
        for elem_info in form_elements:
            try:
                element = elem_info["element"]
                label = elem_info["label"].lower()
                elem_type = elem_info["type"]
                
                # Determine appropriate value based on label
                value = self._get_field_value(label, user_profile, job_data, elem_type)
                
                if value and element.is_displayed() and element.is_enabled():
                    if elem_type == "select":
                        self._fill_select_field(element, value)
                    elif elem_type == "textarea":
                        element.clear()
                        element.send_keys(value)
                    elif elem_type in ["text", "email", "tel", "number"]:
                        element.clear()
                        element.send_keys(value)
                    
                    filled_fields[elem_info["name"] or elem_info["id"]] = value
                    
            except Exception as e:
                logger.warning(f"Failed to fill field {elem_info.get('name', 'unknown')}: {str(e)}")
                continue
        
        return filled_fields

    def _get_field_value(
        self,
        label: str,
        user_profile: Dict[str, Any],
        job_data: Dict[str, Any],
        field_type: str
    ) -> Optional[str]:
        """
        Determine the appropriate value for a form field based on its label
        """
        # Name fields
        if any(keyword in label for keyword in ['name', 'full name', 'first name', 'last name']):
            if 'first' in label:
                return user_profile.get('name', '').split()[0] if user_profile.get('name') else ''
            elif 'last' in label:
                name_parts = user_profile.get('name', '').split()
                return name_parts[-1] if len(name_parts) > 1 else ''
            else:
                return user_profile.get('name', '')
        
        # Email fields
        if 'email' in label:
            return user_profile.get('email', '')
        
        # Phone fields
        if any(keyword in label for keyword in ['phone', 'mobile', 'telephone']):
            return user_profile.get('phone', '')
        
        # Location fields
        if any(keyword in label for keyword in ['location', 'city', 'address', 'where']):
            return user_profile.get('location', '')
        
        # Experience fields
        if any(keyword in label for keyword in ['experience', 'years']):
            return str(user_profile.get('experience_years', ''))
        
        # Skills fields
        if 'skill' in label:
            skills = user_profile.get('skills', [])
            return ', '.join(skills[:5]) if skills else ''
        
        # Cover letter / Why interested
        if any(keyword in label for keyword in ['cover letter', 'why', 'interest', 'motivation']):
            return self._generate_cover_letter_excerpt(user_profile, job_data)
        
        # Current/Previous company
        if any(keyword in label for keyword in ['company', 'employer', 'current']):
            return user_profile.get('current_company', '')
        
        # LinkedIn profile
        if 'linkedin' in label:
            return user_profile.get('linkedin_url', '')
        
        # Portfolio/Website
        if any(keyword in label for keyword in ['portfolio', 'website', 'github']):
            return user_profile.get('portfolio_url', '')
        
        return None

    def _generate_cover_letter_excerpt(
        self,
        user_profile: Dict[str, Any],
        job_data: Dict[str, Any]
    ) -> str:
        """
        Generate a brief cover letter excerpt
        """
        company = job_data.get('company', 'the company')
        position = job_data.get('title', 'this position')
        skills = user_profile.get('skills', [])
        experience = user_profile.get('experience_years', 'several')
        
        excerpt = f"I am excited to apply for the {position} role at {company}. "
        
        if skills:
            excerpt += f"With {experience} years of experience in {', '.join(skills[:3])}, "
        
        excerpt += f"I believe I would be a valuable addition to your team. "
        excerpt += f"I am particularly drawn to {company}'s mission and would love to contribute to your continued success."
        
        return excerpt

    def _fill_select_field(self, select_element, desired_value: str):
        """
        Fill a select field with the most appropriate option
        """
        try:
            select = Select(select_element)
            options = [option.text.lower() for option in select.options]
            desired_lower = desired_value.lower()
            
            # Try exact match first
            for i, option_text in enumerate(options):
                if option_text == desired_lower:
                    select.select_by_index(i)
                    return
            
            # Try partial match
            for i, option_text in enumerate(options):
                if desired_lower in option_text or option_text in desired_lower:
                    select.select_by_index(i)
                    return
                    
        except Exception as e:
            logger.warning(f"Failed to fill select field: {str(e)}")

    async def _handle_file_uploads(self, user_profile: Dict[str, Any]) -> Dict[str, str]:
        """
        Handle file upload fields (resume, cover letter, etc.)
        """
        upload_results = {}
        
        try:
            # Find file input elements
            file_inputs = self.driver.find_elements(By.XPATH, "//input[@type='file']")
            
            for file_input in file_inputs:
                label = self._find_element_label(file_input).lower()
                
                if any(keyword in label for keyword in ['resume', 'cv']):
                    resume_path = user_profile.get('resume_path')
                    if resume_path and os.path.exists(resume_path):
                        file_input.send_keys(resume_path)
                        upload_results['resume'] = 'uploaded'
                    else:
                        upload_results['resume'] = 'not_available'
                
                elif any(keyword in label for keyword in ['cover letter', 'letter']):
                    cover_letter_path = user_profile.get('cover_letter_path')
                    if cover_letter_path and os.path.exists(cover_letter_path):
                        file_input.send_keys(cover_letter_path)
                        upload_results['cover_letter'] = 'uploaded'
                    else:
                        upload_results['cover_letter'] = 'not_available'
        
        except Exception as e:
            logger.error(f"Error handling file uploads: {str(e)}")
            upload_results['error'] = str(e)
        
        return upload_results

    async def _submit_form(self) -> Dict[str, Any]:
        """
        Submit the application form
        """
        try:
            # Find submit button
            submit_buttons = self.driver.find_elements(
                By.XPATH,
                "//button[@type='submit'] | //input[@type='submit'] | //button[contains(text(), 'Submit') or contains(text(), 'Apply')]"
            )
            
            if not submit_buttons:
                return {
                    "success": False,
                    "error": "No submit button found"
                }
            
            # Click submit button
            submit_button = submit_buttons[0]
            self.driver.execute_script("arguments[0].click();", submit_button)
            
            # Wait for response/redirect
            time.sleep(5)
            
            # Check for success indicators
            page_text = self.driver.page_source.lower()
            success_indicators = [
                'thank you', 'thanks', 'success', 'submitted', 'received',
                'confirmation', 'applied', 'application received'
            ]
            
            is_success = any(indicator in page_text for indicator in success_indicators)
            
            return {
                "success": is_success,
                "current_url": self.driver.current_url,
                "confirmation": self._extract_confirmation_from_page()
            }
            
        except Exception as e:
            logger.error(f"Error submitting form: {str(e)}")
            return {
                "success": False,
                "error": f"Form submission failed: {str(e)}"
            }

    def _extract_confirmation_from_page(self) -> Optional[str]:
        """
        Extract confirmation message or number from current page
        """
        try:
            # Look for confirmation elements
            confirmation_elements = self.driver.find_elements(
                By.XPATH,
                "//*[contains(text(), 'confirmation') or contains(text(), 'reference') or contains(text(), 'application id')]"
            )
            
            if confirmation_elements:
                return confirmation_elements[0].text[:200]
            
            return None
            
        except Exception:
            return None

    def _detect_current_step(self) -> str:
        """
        Detect the current step in a multi-step application
        """
        page_text = self.driver.page_source.lower()
        
        if any(keyword in page_text for keyword in ['personal', 'contact', 'name', 'email']):
            return "personal_info"
        elif any(keyword in page_text for keyword in ['resume', 'cv', 'upload']):
            return "resume_upload"
        elif any(keyword in page_text for keyword in ['cover letter', 'letter']):
            return "cover_letter"
        elif any(keyword in page_text for keyword in ['questions', 'questionnaire', 'additional']):
            return "questions"
        elif any(keyword in page_text for keyword in ['review', 'confirm', 'summary']):
            return "review"
        elif any(keyword in page_text for keyword in ['complete', 'thank you', 'submitted']):
            return "complete"
        else:
            return "unknown"

    async def _go_to_next_step(self) -> bool:
        """
        Try to navigate to the next step in the application
        """
        try:
            # Look for next/continue buttons
            next_buttons = self.driver.find_elements(
                By.XPATH,
                "//button[contains(text(), 'Next') or contains(text(), 'Continue') or contains(text(), 'Save and Continue')]"
            )
            
            if next_buttons:
                next_buttons[0].click()
                time.sleep(3)
                return True
            
            return False
            
        except Exception:
            return False

    def _is_application_completed(self) -> bool:
        """
        Check if the application process is completed
        """
        page_text = self.driver.page_source.lower()
        completion_indicators = [
            'thank you', 'thanks', 'success', 'submitted', 'received',
            'confirmation', 'applied', 'application received', 'complete'
        ]
        
        return any(indicator in page_text for indicator in completion_indicators)

    async def _fill_personal_info_step(self, user_profile: Dict[str, Any]):
        """Fill personal information step"""
        form_elements = self._find_form_elements()
        await self._auto_fill_form(form_elements, user_profile, {})

    async def _fill_resume_step(self, user_profile: Dict[str, Any]):
        """Fill resume upload step"""
        await self._handle_file_uploads(user_profile)

    async def _fill_cover_letter_step(self, user_profile: Dict[str, Any], job_data: Dict[str, Any]):
        """Fill cover letter step"""
        form_elements = self._find_form_elements()
        await self._auto_fill_form(form_elements, user_profile, job_data)

    async def _fill_questions_step(self, user_profile: Dict[str, Any], job_data: Dict[str, Any]):
        """Fill additional questions step"""
        form_elements = self._find_form_elements()
        await self._auto_fill_form(form_elements, user_profile, job_data)

    async def _handle_review_step(self):
        """Handle review/confirmation step"""
        # Just proceed to next step for review
        pass 