import unittest
import os
import asyncio
from unittest.mock import patch, MagicMock
import sys
import logging

# Add the parent directory to the path to import modules from backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.scheduler import setup_scheduler
from utils.cronjob import wake_up_render

logging.basicConfig(level=logging.INFO)

class TestScheduler(unittest.TestCase):
    """Tests for the scheduler and cronjob functionality"""
    
    @patch('requests.get')
    def test_wake_up_render(self, mock_get):
        """Test wake_up_render function"""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        # Call the function
        wake_up_render()
        
        # Verify the request was made with the correct URL
        render_url = os.getenv('RENDER_URL', 'https://remote-jobs-62gn.onrender.com')
        mock_get.assert_called_once_with(f"{render_url}/health", timeout=10)
    
    @patch('utils.job_archiver.archive_old_jobs')
    @patch('utils.cronjob.wake_up_render')
    def test_scheduler_setup(self, mock_wake_up, mock_archive):
        """Test that the scheduler sets up jobs correctly"""
        # Make the mocks async
        mock_archive.__aenter__ = MagicMock()
        mock_archive.__aexit__ = MagicMock()
        
        # Set up the scheduler
        scheduler = setup_scheduler()
        
        # Verify jobs were added
        job_ids = [job.id for job in scheduler.get_jobs()]
        self.assertIn('archive_old_jobs', job_ids)
        self.assertIn('wake_up_render', job_ids)
        
        # Clean up
        scheduler.shutdown()

if __name__ == '__main__':
    unittest.main() 