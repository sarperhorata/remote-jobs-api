import os
import re
import PyPDF2
import docx
from typing import Dict, Any, Optional

def parse_cv_file(file_path: str) -> Optional[Dict[str, Any]]:
    """
    CV dosyasını parse eder ve içindeki bilgileri çıkarır.
    
    Args:
        file_path: CV dosyasının yolu
        
    Returns:
        Dict[str, Any]: CV'den çıkarılan bilgiler
    """
    file_ext = os.path.splitext(file_path)[1].lower()
    
    if file_ext == '.pdf':
        return parse_pdf(file_path)
    elif file_ext in ['.doc', '.docx']:
        return parse_docx(file_path)
    else:
        return None

def parse_pdf(file_path: str) -> Optional[Dict[str, Any]]:
    """
    PDF formatındaki CV'yi parse eder.
    
    Args:
        file_path: PDF dosyasının yolu
        
    Returns:
        Dict[str, Any]: CV'den çıkarılan bilgiler
    """
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            
            return extract_cv_data(text)
    except Exception as e:
        print(f"PDF parse error: {e}")
        return None

def parse_docx(file_path: str) -> Optional[Dict[str, Any]]:
    """
    DOCX formatındaki CV'yi parse eder.
    
    Args:
        file_path: DOCX dosyasının yolu
        
    Returns:
        Dict[str, Any]: CV'den çıkarılan bilgiler
    """
    try:
        doc = docx.Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        
        return extract_cv_data(text)
    except Exception as e:
        print(f"DOCX parse error: {e}")
        return None

def extract_cv_data(text: str) -> Dict[str, Any]:
    """
    CV metninden bilgileri çıkarır.
    
    Args:
        text: CV metni
        
    Returns:
        Dict[str, Any]: CV'den çıkarılan bilgiler
    """
    cv_data = {
        'name': None,
        'email': None,
        'phone': None,
        'title': None,
        'experience': [],
        'education': [],
        'skills': []
    }
    
    # İsim
    name_pattern = r'^([A-Z][a-z]+ [A-Z][a-z]+)'
    name_match = re.search(name_pattern, text, re.MULTILINE)
    if name_match:
        cv_data['name'] = name_match.group(1)
    
    # E-posta
    email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
    email_match = re.search(email_pattern, text)
    if email_match:
        cv_data['email'] = email_match.group(0)
    
    # Telefon
    phone_pattern = r'(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    phone_match = re.search(phone_pattern, text)
    if phone_match:
        cv_data['phone'] = phone_match.group(0)
    
    # Başlık/Unvan
    title_pattern = r'(Software Engineer|Developer|Programmer|Designer|Manager|Director|Consultant|Architect)'
    title_match = re.search(title_pattern, text, re.IGNORECASE)
    if title_match:
        cv_data['title'] = title_match.group(1)
    
    # Deneyim
    experience_pattern = r'(Experience|Work History|Employment)(.*?)(Education|Skills|$)'
    experience_match = re.search(experience_pattern, text, re.IGNORECASE | re.DOTALL)
    if experience_match:
        experience_text = experience_match.group(2)
        # Deneyim bölümünü satırlara ayır
        experience_lines = re.split(r'\n+', experience_text)
        for line in experience_lines:
            if line.strip() and not re.match(r'^(Experience|Work History|Employment)$', line, re.IGNORECASE):
                cv_data['experience'].append(line.strip())
    
    # Eğitim
    education_pattern = r'(Education|Academic Background)(.*?)(Experience|Skills|$)'
    education_match = re.search(education_pattern, text, re.IGNORECASE | re.DOTALL)
    if education_match:
        education_text = education_match.group(2)
        # Eğitim bölümünü satırlara ayır
        education_lines = re.split(r'\n+', education_text)
        for line in education_lines:
            if line.strip() and not re.match(r'^(Education|Academic Background)$', line, re.IGNORECASE):
                cv_data['education'].append(line.strip())
    
    # Beceriler
    skills_pattern = r'(Skills|Technical Skills|Core Competencies)(.*?)(Experience|Education|$)'
    skills_match = re.search(skills_pattern, text, re.IGNORECASE | re.DOTALL)
    if skills_match:
        skills_text = skills_match.group(2)
        # Beceriler bölümünü virgülle ayır
        skills_list = re.split(r'[,;]', skills_text)
        for skill in skills_list:
            if skill.strip() and not re.match(r'^(Skills|Technical Skills|Core Competencies)$', skill, re.IGNORECASE):
                cv_data['skills'].append(skill.strip())
    
    return cv_data 