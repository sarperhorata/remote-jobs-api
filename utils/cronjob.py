import requests
import os
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def wake_up_render():
    """Keep the Render service active by sending a request every 14 minutes."""
    try:
        render_url = os.getenv('RENDER_URL', 'https://remote-jobs-62gn.onrender.com')
        response = requests.get(f"{render_url}/health")
        if response.status_code == 200:
            logger.info(f"Successfully woke up Render service at {datetime.now()}")
        else:
            logger.error(f"Failed to wake up Render service. Status code: {response.status_code}")
    except Exception as e:
        logger.error(f"Error waking up Render service: {str(e)}") 