import os
import sys
import logging

# Add the parent directory to the path to import modules from backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.cronjob import wake_up_render

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def main():
    """
    Test the wake-up function manually
    """
    logger.info("Testing wake_up_render function...")
    
    # Check if RENDER_URL is set
    render_url = os.getenv('RENDER_URL')
    if not render_url:
        logger.warning("RENDER_URL environment variable is not set. Using default URL.")
    else:
        logger.info(f"Using RENDER_URL: {render_url}")
    
    # Call the wake_up_render function
    try:
        wake_up_render()
        logger.info("wake_up_render function completed")
    except Exception as e:
        logger.error(f"Error testing wake_up_render: {str(e)}")

if __name__ == "__main__":
    main() 