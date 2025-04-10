import os
import requests
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class CaptchaVerifier:
    """CAPTCHA doğrulama işlemleri"""
    
    @staticmethod
    def verify_recaptcha(recaptcha_response: str) -> bool:
        """
        Google reCAPTCHA doğrulaması yapar.
        
        Args:
            recaptcha_response: reCAPTCHA yanıtı
            
        Returns:
            bool: Doğrulama başarılıysa True, değilse False
        """
        recaptcha_secret = os.getenv("RECAPTCHA_SECRET_KEY")
        
        if not recaptcha_secret:
            logger.warning("RECAPTCHA_SECRET_KEY environment variable is not set")
            return True  # Geliştirme ortamında doğrulamayı atla
        
        try:
            response = requests.post(
                "https://www.google.com/recaptcha/api/siteverify",
                data={
                    "secret": recaptcha_secret,
                    "response": recaptcha_response
                }
            )
            
            result = response.json()
            return result.get("success", False)
        except Exception as e:
            logger.error(f"Error verifying reCAPTCHA: {str(e)}")
            return False
    
    @staticmethod
    def verify_hcaptcha(hcaptcha_response: str) -> bool:
        """
        hCaptcha doğrulaması yapar.
        
        Args:
            hcaptcha_response: hCaptcha yanıtı
            
        Returns:
            bool: Doğrulama başarılıysa True, değilse False
        """
        hcaptcha_secret = os.getenv("HCAPTCHA_SECRET_KEY")
        
        if not hcaptcha_secret:
            logger.warning("HCAPTCHA_SECRET_KEY environment variable is not set")
            return True  # Geliştirme ortamında doğrulamayı atla
        
        try:
            response = requests.post(
                "https://hcaptcha.com/siteverify",
                data={
                    "secret": hcaptcha_secret,
                    "response": hcaptcha_response
                }
            )
            
            result = response.json()
            return result.get("success", False)
        except Exception as e:
            logger.error(f"Error verifying hCaptcha: {str(e)}")
            return False 