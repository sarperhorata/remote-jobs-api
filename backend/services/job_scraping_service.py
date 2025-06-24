import asyncio
import aiohttp
import re
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin, urlparse
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class FormField:
    id: str
    name: str
    label: str
    type: str
    required: bool
    placeholder: Optional[str] = None
    options: Optional[List[str]] = None
    max_length: Optional[int] = None

class JobScrapingService:
    """
    Service for scraping job application forms and submitting applications (v2)
    """
    
    def __init__(self):
        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def scrape_application_form(self, url: str) -> Dict[str, Any]:
        """
        Scrape job application form fields from the given URL
        """
        try:
            if not self.session:
                self.session = aiohttp.ClientSession(
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                )

            async with self.session.get(url) as response:
                if response.status != 200:
                    return {
                        "success": False,
                        "error": f"Failed to fetch page: HTTP {response.status}"
                    }

                html_content = await response.text()
                soup = BeautifulSoup(html_content, 'html.parser')

                # Find application forms
                forms = soup.find_all('form')
                application_form = None

                # Look for forms that likely contain job applications
                for form in forms:
                    form_text = form.get_text().lower()
                    form_action = form.get('action', '').lower()
                    form_class = ' '.join(form.get('class', [])).lower()
                    form_id = form.get('id', '').lower()

                    # Check if this is likely an application form
                    application_indicators = [
                        'apply', 'application', 'job', 'resume', 'cv', 'hire',
                        'career', 'submit', 'candidate', 'employment'
                    ]

                    if any(indicator in form_text or 
                          indicator in form_action or 
                          indicator in form_class or 
                          indicator in form_id 
                          for indicator in application_indicators):
                        application_form = form
                        break

                if not application_form:
                    # If no specific application form found, use the largest form
                    application_form = max(forms, key=lambda f: len(f.find_all(['input', 'textarea', 'select'])), default=None)

                if not application_form:
                    return {
                        "success": False,
                        "error": "No application form found on the page"
                    }

                # Extract form fields
                fields = self._extract_form_fields(application_form)
                
                if not fields:
                    return {
                        "success": False,
                        "error": "No form fields found"
                    }

                # Get form action and method
                form_action = application_form.get('action')
                if form_action:
                    form_action = urljoin(url, form_action)
                else:
                    form_action = url

                form_method = application_form.get('method', 'POST').upper()

                return {
                    "success": True,
                    "fields": [field.__dict__ for field in fields],
                    "form_action": form_action,
                    "form_method": form_method,
                    "total_fields": len(fields)
                }

        except Exception as e:
            logger.error(f"Error scraping application form from {url}: {str(e)}")
            return {
                "success": False,
                "error": f"Scraping failed: {str(e)}"
            }

    def _extract_form_fields(self, form) -> List[FormField]:
        """
        Extract form fields from a BeautifulSoup form element
        """
        fields = []
        field_counter = 0

        # Process input fields
        for input_tag in form.find_all('input'):
            field = self._process_input_field(input_tag, field_counter)
            if field:
                fields.append(field)
                field_counter += 1

        # Process textarea fields
        for textarea in form.find_all('textarea'):
            field = self._process_textarea_field(textarea, field_counter)
            if field:
                fields.append(field)
                field_counter += 1

        # Process select fields
        for select in form.find_all('select'):
            field = self._process_select_field(select, field_counter)
            if field:
                fields.append(field)
                field_counter += 1

        return fields

    def _process_input_field(self, input_tag, counter: int) -> Optional[FormField]:
        """
        Process an HTML input element and convert to FormField
        """
        input_type = input_tag.get('type', 'text').lower()
        
        # Skip certain input types
        if input_type in ['hidden', 'submit', 'button', 'reset', 'image']:
            return None

        name = input_tag.get('name')
        input_id = input_tag.get('id') or f"field_{counter}"
        
        if not name:
            return None

        # Find label
        label = self._find_field_label(input_tag, name)
        
        # Determine if field is required
        required = input_tag.get('required') is not None or \
                  'required' in input_tag.get('class', []) or \
                  '*' in label

        # Get placeholder
        placeholder = input_tag.get('placeholder')

        # Get max length
        max_length = input_tag.get('maxlength')
        if max_length:
            try:
                max_length = int(max_length)
            except ValueError:
                max_length = None

        return FormField(
            id=input_id,
            name=name,
            label=label,
            type=self._normalize_field_type(input_type),
            required=required,
            placeholder=placeholder,
            max_length=max_length
        )

    def _process_textarea_field(self, textarea, counter: int) -> Optional[FormField]:
        """
        Process an HTML textarea element and convert to FormField
        """
        name = textarea.get('name')
        textarea_id = textarea.get('id') or f"textarea_{counter}"
        
        if not name:
            return None

        label = self._find_field_label(textarea, name)
        required = textarea.get('required') is not None or \
                  'required' in textarea.get('class', []) or \
                  '*' in label

        placeholder = textarea.get('placeholder')
        
        # Get max length
        max_length = textarea.get('maxlength')
        if max_length:
            try:
                max_length = int(max_length)
            except ValueError:
                max_length = None

        return FormField(
            id=textarea_id,
            name=name,
            label=label,
            type='textarea',
            required=required,
            placeholder=placeholder,
            max_length=max_length
        )

    def _process_select_field(self, select, counter: int) -> Optional[FormField]:
        """
        Process an HTML select element and convert to FormField
        """
        name = select.get('name')
        select_id = select.get('id') or f"select_{counter}"
        
        if not name:
            return None

        label = self._find_field_label(select, name)
        required = select.get('required') is not None or \
                  'required' in select.get('class', []) or \
                  '*' in label

        # Extract options
        options = []
        for option in select.find_all('option'):
            option_text = option.get_text().strip()
            if option_text and option_text.lower() not in ['select', 'choose', 'pick']:
                options.append(option_text)

        return FormField(
            id=select_id,
            name=name,
            label=label,
            type='select',
            required=required,
            options=options
        )

    def _find_field_label(self, field_element, field_name: str) -> str:
        """
        Find the label for a form field
        """
        # Try to find label by 'for' attribute
        field_id = field_element.get('id')
        if field_id:
            label = field_element.find_parent().find('label', {'for': field_id})
            if label:
                return label.get_text().strip()

        # Try to find label by searching nearby elements
        parent = field_element.find_parent()
        if parent:
            # Look for label in same container
            label = parent.find('label')
            if label:
                return label.get_text().strip()

            # Look for text before the field
            for sibling in field_element.previous_siblings:
                if sibling.name == 'label':
                    return sibling.get_text().strip()
                elif hasattr(sibling, 'get_text'):
                    text = sibling.get_text().strip()
                    if text and len(text) < 100:  # Reasonable label length
                        return text

        # Fallback to field name
        return field_name.replace('_', ' ').replace('-', ' ').title()

    def _normalize_field_type(self, input_type: str) -> str:
        """
        Normalize HTML input types to standard form field types
        """
        type_mapping = {
            'text': 'text',
            'email': 'email',
            'tel': 'phone',
            'phone': 'phone',
            'url': 'text',
            'password': 'text',
            'number': 'text',
            'date': 'text',
            'file': 'file',
            'checkbox': 'checkbox',
            'radio': 'checkbox'
        }
        
        return type_mapping.get(input_type.lower(), 'text')

    async def submit_application(
        self, 
        form_url: str,
        form_action: str,
        form_method: str,
        field_values: Dict[str, str],
        documents: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Submit the application form with provided values
        """
        try:
            if not self.session:
                self.session = aiohttp.ClientSession(
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=60)
                )

            # Prepare form data
            form_data = aiohttp.FormData()
            
            for field_name, value in field_values.items():
                if value:  # Only add non-empty values
                    form_data.add_field(field_name, str(value))

            # Add document uploads if provided
            if documents:
                for doc_field, doc_info in documents.items():
                    if doc_info and doc_info.get('content'):
                        form_data.add_field(
                            doc_field,
                            doc_info['content'],
                            filename=doc_info.get('filename', 'document.pdf'),
                            content_type=doc_info.get('content_type', 'application/pdf')
                        )

            # Submit the form
            submit_method = getattr(self.session, form_method.lower(), self.session.post)
            
            async with submit_method(form_action, data=form_data) as response:
                response_text = await response.text()
                
                # Check for success indicators
                success_indicators = [
                    'thank you', 'thanks', 'success', 'submitted', 'received',
                    'confirmation', 'applied', 'application received'
                ]
                
                response_lower = response_text.lower()
                is_success = any(indicator in response_lower for indicator in success_indicators)
                
                # Also consider status codes
                if response.status in [200, 201, 302]:
                    is_success = True
                elif response.status >= 400:
                    is_success = False

                result = {
                    "success": is_success,
                    "status_code": response.status,
                    "response_url": str(response.url)
                }

                if is_success:
                    # Try to extract confirmation message or number
                    confirmation = self._extract_confirmation(response_text)
                    if confirmation:
                        result["confirmation"] = confirmation
                    result["message"] = "Application submitted successfully"
                else:
                    result["error"] = f"Submission may have failed (HTTP {response.status})"
                    # Try to extract error message
                    error_msg = self._extract_error_message(response_text)
                    if error_msg:
                        result["error"] = error_msg

                return result

        except Exception as e:
            logger.error(f"Error submitting application to {form_action}: {str(e)}")
            return {
                "success": False,
                "error": f"Submission failed: {str(e)}"
            }

    def _extract_confirmation(self, html_content: str) -> Optional[str]:
        """
        Extract confirmation message or number from response
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Look for confirmation patterns
        confirmation_patterns = [
            r'application\s+(?:id|number|ref(?:erence)?)\s*:?\s*([a-zA-Z0-9-]+)',
            r'confirmation\s+(?:id|number|code)\s*:?\s*([a-zA-Z0-9-]+)',
            r'reference\s+(?:id|number)\s*:?\s*([a-zA-Z0-9-]+)'
        ]
        
        text_content = soup.get_text()
        for pattern in confirmation_patterns:
            match = re.search(pattern, text_content, re.IGNORECASE)
            if match:
                return match.group(1)
        
        # Look for success messages
        success_elements = soup.find_all(text=re.compile(r'thank you|success|submitted|received', re.IGNORECASE))
        if success_elements:
            return success_elements[0].strip()[:200]  # Limit length
        
        return None

    def _extract_error_message(self, html_content: str) -> Optional[str]:
        """
        Extract error message from response
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Look for error elements
        error_selectors = [
            '.error', '.alert-error', '.alert-danger', 
            '[class*="error"]', '[class*="danger"]'
        ]
        
        for selector in error_selectors:
            error_elements = soup.select(selector)
            if error_elements:
                return error_elements[0].get_text().strip()[:200]
        
        # Look for error text patterns
        error_patterns = [
            r'error\s*:?\s*(.{1,200})',
            r'failed\s*:?\s*(.{1,200})',
            r'invalid\s*:?\s*(.{1,200})'
        ]
        
        text_content = soup.get_text()
        for pattern in error_patterns:
            match = re.search(pattern, text_content, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None

    async def close(self):
        """
        Clean up resources
        """
        if self.session:
            await self.session.close()
            self.session = None 