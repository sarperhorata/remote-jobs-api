import html
import re
from typing import Any, Dict, Optional

from bs4 import BeautifulSoup


def clean_html_tags(text: Optional[str]) -> str:
    """
    HTML taglerini temizle ve metni düzenle

    Args:
        text: Temizlenecek metin

    Returns:
        Temizlenmiş metin
    """
    if not text:
        return ""

    # String olduğundan emin ol
    if not isinstance(text, str):
        text = str(text)

    # HTML entities'leri decode et
    text = html.unescape(text)

    # BeautifulSoup ile HTML taglerini temizle
    soup = BeautifulSoup(text, "html.parser")
    clean_text = soup.get_text()

    # Fazla boşlukları temizle
    clean_text = re.sub(r"\s+", " ", clean_text)
    clean_text = clean_text.strip()

    return clean_text


def clean_job_description(description: Optional[str], max_length: int = 2000) -> str:
    """
    İş ilanı açıklamasını temizle ve formatla

    Args:
        description: İş ilanı açıklaması
        max_length: Maksimum uzunluk

    Returns:
        Temizlenmiş açıklama
    """
    if not description:
        return ""

    # HTML taglerini temizle
    clean_desc = clean_html_tags(description)

    # Uzunluğu sınırla
    if len(clean_desc) > max_length:
        clean_desc = clean_desc[: max_length - 3] + "..."

    return clean_desc


def clean_job_title(title: Optional[str]) -> str:
    """
    İş başlığını temizle

    Args:
        title: İş başlığı

    Returns:
        Temizlenmiş başlık
    """
    if not title:
        return ""

    # HTML taglerini temizle
    clean_title = clean_html_tags(title)

    # Fazla boşlukları temizle
    clean_title = re.sub(r"\s+", " ", clean_title)
    clean_title = clean_title.strip()

    return clean_title


def clean_company_name(company: Optional[str]) -> str:
    """
    Şirket adını temizle

    Args:
        company: Şirket adı

    Returns:
        Temizlenmiş şirket adı
    """
    if not company:
        return ""

    # HTML taglerini temizle
    clean_company = clean_html_tags(company)

    # Fazla boşlukları temizle
    clean_company = re.sub(r"\s+", " ", clean_company)
    clean_company = clean_company.strip()

    return clean_company


def clean_job_data(job_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    İş ilanı verilerini toplu olarak temizle

    Args:
        job_data: İş ilanı verisi

    Returns:
        Temizlenmiş iş ilanı verisi
    """
    cleaned_data = job_data.copy()

    # Temizlenecek alanlar
    fields_to_clean = {
        "title": clean_job_title,
        "description": clean_job_description,
        "company": clean_company_name,
        "location": clean_html_tags,
        "requirements": clean_html_tags,
        "benefits": clean_html_tags,
        "responsibilities": clean_html_tags,
    }

    for field, cleaner_func in fields_to_clean.items():
        if field in cleaned_data:
            # None değerleri boş string'e çevir
            if cleaned_data[field] is None:
                cleaned_data[field] = ""
            elif cleaned_data[field]:  # Boş olmayan değerleri temizle
                cleaned_data[field] = cleaner_func(cleaned_data[field])

    # İç içe dictionary'leri de temizle
    for key, value in cleaned_data.items():
        if isinstance(value, dict):
            cleaned_data[key] = clean_job_data(value)

    return cleaned_data
