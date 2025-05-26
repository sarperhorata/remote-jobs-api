import requests
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/health_check.log'),
        logging.StreamHandler()
    ]
)

def health_check():
    try:
        # API endpoint URL - correct Render URL
        api_url = "https://remote-jobs-api-k9v1.onrender.com/health"
        
        # Make the request
        response = requests.get(api_url, timeout=10)
        
        # Check if the request was successful
        if response.status_code == 200:
            logging.info(f"Health check successful at {datetime.now()}")
        else:
            logging.error(f"Health check failed with status code: {response.status_code}")
            
    except Exception as e:
        logging.error(f"Health check failed with error: {str(e)}")

if __name__ == "__main__":
    health_check() 