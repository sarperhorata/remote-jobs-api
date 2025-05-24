import os
import logging
import aiohttp
import json
from typing import Optional, Dict, Any, Union

logger = logging.getLogger(__name__)

class CaptchaVerifier:
    # Get secret keys from environment variables
    RECAPTCHA_SECRET_KEY = os.getenv("RECAPTCHA_SECRET_KEY")
    HCAPTCHA_SECRET_KEY = os.getenv("HCAPTCHA_SECRET_KEY")
    
    # Verification endpoints
    RECAPTCHA_VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"
    HCAPTCHA_VERIFY_URL = "https://hcaptcha.com/siteverify"
    
    @classmethod
    async def verify_token(cls, token: str, remote_ip: Optional[str] = None) -> bool:
        """
        Verify a CAPTCHA token. Automatically detects whether it's reCAPTCHA or hCaptcha.
        
        Args:
            token: The CAPTCHA token from the client
            remote_ip: The IP address of the client (optional)
            
        Returns:
            bool: True if verification succeeded, False otherwise
        """
        # Skip verification in development mode if configured
        if os.getenv("CAPTCHA_SKIP_VERIFICATION") == "true":
            logger.warning("CAPTCHA verification skipped due to CAPTCHA_SKIP_VERIFICATION=true")
            return True
            
        # Determine which CAPTCHA service to use based on token prefix
        if token.startswith("hc-"):
            return await cls.verify_hcaptcha(token, remote_ip)
        else:
            return await cls.verify_recaptcha(token, remote_ip)
    
    @classmethod
    async def verify_recaptcha(cls, token: str, remote_ip: Optional[str] = None) -> bool:
        """
        Verify a Google reCAPTCHA token
        
        Args:
            token: The reCAPTCHA token from the client
            remote_ip: The IP address of the client (optional)
            
        Returns:
            bool: True if verification succeeded, False otherwise
        """
        if not cls.RECAPTCHA_SECRET_KEY:
            logger.error("reCAPTCHA secret key not configured")
            return False
            
        try:
            data = {
                "secret": cls.RECAPTCHA_SECRET_KEY,
                "response": token
            }
            
            if remote_ip:
                data["remoteip"] = remote_ip
                
            async with aiohttp.ClientSession() as session:
                async with session.post(cls.RECAPTCHA_VERIFY_URL, data=data) as response:
                    if response.status != 200:
                        logger.error(f"reCAPTCHA verification failed with status {response.status}")
                        return False
                        
                    result = await response.json()
                    success = result.get("success", False)
                    
                    if not success:
                        error_codes = result.get("error-codes", [])
                        logger.warning(f"reCAPTCHA verification failed: {error_codes}")
                        
                    return success
                    
        except Exception as e:
            logger.error(f"Error during reCAPTCHA verification: {str(e)}")
            return False
    
    @classmethod
    async def verify_hcaptcha(cls, token: str, remote_ip: Optional[str] = None) -> bool:
        """
        Verify an hCaptcha token
        
        Args:
            token: The hCaptcha token from the client
            remote_ip: The IP address of the client (optional)
            
        Returns:
            bool: True if verification succeeded, False otherwise
        """
        if not cls.HCAPTCHA_SECRET_KEY:
            logger.error("hCaptcha secret key not configured")
            return False
            
        try:
            data = {
                "secret": cls.HCAPTCHA_SECRET_KEY,
                "response": token
            }
            
            if remote_ip:
                data["remoteip"] = remote_ip
                
            async with aiohttp.ClientSession() as session:
                async with session.post(cls.HCAPTCHA_VERIFY_URL, data=data) as response:
                    if response.status != 200:
                        logger.error(f"hCaptcha verification failed with status {response.status}")
                        return False
                        
                    result = await response.json()
                    success = result.get("success", False)
                    
                    if not success:
                        error_codes = result.get("error-codes", [])
                        logger.warning(f"hCaptcha verification failed: {error_codes}")
                        
                    return success
                    
        except Exception as e:
            logger.error(f"Error during hCaptcha verification: {str(e)}")
            return False 