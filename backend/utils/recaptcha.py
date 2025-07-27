import os

import requests


def verify_recaptcha(response: str) -> bool:
    """
    Verify reCAPTCHA response token.

    Args:
        response: reCAPTCHA response token

    Returns:
        bool: Is the response valid?
    """
    try:
        secret_key = os.getenv("RECAPTCHA_SECRET_KEY")
        if not secret_key:
            return True  # Skip verification if no secret key is set

        verify_url = "https://www.google.com/recaptcha/api/siteverify"
        data = {"secret": secret_key, "response": response}

        result = requests.post(verify_url, data=data)
        result_json = result.json()

        return result_json.get("success", False)
    except Exception as e:
        print(f"Error verifying reCAPTCHA: {str(e)}")
        return False
