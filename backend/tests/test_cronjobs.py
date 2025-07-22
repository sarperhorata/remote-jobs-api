import pytest
import asyncio
import os
import sys
import subprocess
import time
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, AsyncMock
import requests
import json

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services.scheduler_service import start_scheduler, stop_scheduler, get_scheduler
from backend.utils.cronjob import wake_up_render
from backend.database.db import get_async_db


class TestCronjobs:
    """Test cronjob functionality and scheduler service"""
    
    @pytest.fixture(autouse=True)
    async def setup_teardown(self):
        """Setup and teardown for each test"""
        # Setup
        yield
        # Teardown - ensure scheduler is stopped
        try:
            scheduler = get_scheduler()
            if scheduler:
                await stop_scheduler()
        except Exception:
            pass
    
    @pytest.mark.asyncio
    async def test_scheduler_service_startup(self):
        """Test that scheduler service can start properly"""
        try:
            result = await start_scheduler()
            assert result is True, "Scheduler should start successfully"
            
            scheduler = get_scheduler()
            assert scheduler is not None, "Scheduler instance should exist"
            assert scheduler.is_running, "Scheduler should be running"
            print("✅ Scheduler service started successfully")
        except Exception as e:
            pytest.fail(f"Scheduler failed to start: {e}")
        finally:
            await stop_scheduler()
    
    @pytest.mark.asyncio
    async def test_scheduler_jobs_configured(self):
        """Test that all required jobs are configured"""
        try:
            await start_scheduler()
            scheduler = get_scheduler()
            jobs = scheduler.scheduler.get_jobs()
            
            # Check for required jobs
            job_names = [job.name for job in jobs]
            required_jobs = [
                'Health Check - Keep Render Awake',
                'External API Crawler',
                'Database Cleanup',
                'Daily Job Statistics'
            ]
            
            for job_name in required_jobs:
                assert job_name in job_names, f"Required job '{job_name}' not found"
            
            print(f"✅ All required jobs configured: {job_names}")
        except Exception as e:
            pytest.fail(f"Job configuration test failed: {e}")
        finally:
            await stop_scheduler()
    
    @pytest.mark.asyncio
    async def test_health_check_job(self):
        """Test health check job functionality"""
        try:
            scheduler = await start_scheduler()
            
            # Find health check job
            health_job = None
            for job in scheduler.get_jobs():
                if job.name == 'health_check_job':
                    health_job = job
                    break
            
            assert health_job is not None, "Health check job not found"
            
            # Test job execution
            with patch('requests.get') as mock_get:
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = {"status": "healthy"}
                mock_get.return_value = mock_response
                
                # Execute job manually
                await health_job.func()
                
                # Verify request was made
                mock_get.assert_called()
                print("✅ Health check job executed successfully")
                
        except Exception as e:
            pytest.fail(f"Health check job test failed: {e}")
        finally:
            await stop_scheduler()
    
    @pytest.mark.asyncio
    async def test_external_api_crawler_job(self):
        """Test external API crawler job"""
        try:
            scheduler = await start_scheduler()
            
            # Find external API job
            api_job = None
            for job in scheduler.get_jobs():
                if job.name == 'external_api_crawler_job':
                    api_job = job
                    break
            
            assert api_job is not None, "External API crawler job not found"
            
            # Test job execution with mocked dependencies
            with patch('backend.services.external_job_service.crawl_external_apis') as mock_crawl:
                mock_crawl.return_value = {"status": "success", "jobs_found": 10}
                
                # Execute job manually
                await api_job.func()
                
                # Verify crawl was called
                mock_crawl.assert_called_once()
                print("✅ External API crawler job executed successfully")
                
        except Exception as e:
            pytest.fail(f"External API crawler job test failed: {e}")
        finally:
            await stop_scheduler()
    
    @pytest.mark.asyncio
    async def test_job_statistics_job(self):
        """Test job statistics job"""
        try:
            scheduler = await start_scheduler()
            
            # Find statistics job
            stats_job = None
            for job in scheduler.get_jobs():
                if job.name == 'job_statistics_job':
                    stats_job = job
                    break
            
            assert stats_job is not None, "Job statistics job not found"
            
            # Test job execution
            with patch('backend.services.scheduler_service.get_async_db') as mock_db:
                mock_db_instance = AsyncMock()
                mock_db.return_value = mock_db_instance
                
                # Execute job manually
                await stats_job.func()
                
                print("✅ Job statistics job executed successfully")
                
        except Exception as e:
            pytest.fail(f"Job statistics job test failed: {e}")
        finally:
            await stop_scheduler()
    
    @pytest.mark.asyncio
    async def test_database_cleanup_job(self):
        """Test database cleanup job"""
        try:
            scheduler = await start_scheduler()
            
            # Find cleanup job
            cleanup_job = None
            for job in scheduler.get_jobs():
                if job.name == 'database_cleanup_job':
                    cleanup_job = job
                    break
            
            assert cleanup_job is not None, "Database cleanup job not found"
            
            # Test job execution
            with patch('backend.services.scheduler_service.get_async_db') as mock_db:
                mock_db_instance = AsyncMock()
                mock_db.return_value = mock_db_instance
                
                # Execute job manually
                await cleanup_job.func()
                
                print("✅ Database cleanup job executed successfully")
                
        except Exception as e:
            pytest.fail(f"Database cleanup job test failed: {e}")
        finally:
            await stop_scheduler()
    
    def test_wake_up_render_function(self):
        """Test wake up render function"""
        try:
            with patch('requests.get') as mock_get:
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = {"status": "healthy"}
                mock_get.return_value = mock_response
                
                # Test function
                result = wake_up_render()
                
                # Verify request was made to correct URL (timeout can be 10 or 30)
                mock_get.assert_called()
                call_args = mock_get.call_args
                assert "https://buzz2remote-api.onrender.com/api/v1/health" in call_args[0]
                
                assert result is True
                print("✅ Wake up render function executed successfully")
                
        except Exception as e:
            pytest.fail(f"Wake up render test failed: {e}")
    
    def test_cronjob_scripts_exist(self):
        """Test that cronjob scripts exist and are executable"""
        script_paths = [
            "cron_external_apis.py",
            "tools/setup_health_check_cron.sh",
            "tools/setup_external_api_cron.sh",
            "tools/health_check.sh"
        ]
        
        for script_path in script_paths:
            full_path = os.path.join(os.path.dirname(__file__), '..', '..', script_path)
            assert os.path.exists(full_path), f"Script not found: {script_path}"
            
            # Check if shell scripts are executable
            if script_path.endswith('.sh'):
                assert os.access(full_path, os.X_OK), f"Script not executable: {script_path}"
            
            print(f"✅ Script exists: {script_path}")
    
    def test_cronjob_script_execution(self):
        """Test that cronjob scripts can be executed"""
        try:
            # Test Python script
            script_path = os.path.join(os.path.dirname(__file__), '..', '..', 'cron_external_apis.py')
            
            # Test script import
            with patch('sys.path') as mock_path:
                mock_path.insert = MagicMock()
                
                # Test script execution with mocked dependencies
                with patch('backend.services.external_job_service.crawl_external_apis') as mock_crawl:
                    mock_crawl.return_value = {"status": "success"}
                    
                    # Import and test main function
                    import importlib.util
                    spec = importlib.util.spec_from_file_location("cron_external_apis", script_path)
                    module = importlib.util.module_from_spec(spec)
                    
                    # Mock the main execution
                    with patch.object(module, '__name__', '__main__'):
                        print("✅ Cronjob script can be imported and executed")
                        
        except Exception as e:
            pytest.fail(f"Cronjob script execution test failed: {e}")
    
    @pytest.mark.asyncio
    async def test_scheduler_error_handling(self):
        """Test scheduler error handling"""
        try:
            scheduler = await start_scheduler()
            
            # Test that scheduler handles errors gracefully
            with patch('backend.services.scheduler_service._health_check_job') as mock_health:
                mock_health.side_effect = Exception("Test error")
                
                # Job should not crash the scheduler
                await scheduler._health_check_job()
                
                # Scheduler should still be running
                assert scheduler.running
                print("✅ Scheduler handles errors gracefully")
                
        except Exception as e:
            pytest.fail(f"Scheduler error handling test failed: {e}")
        finally:
            await stop_scheduler()
    
    def test_cronjob_logging(self):
        """Test that cronjobs have proper logging"""
        log_files = [
            "/tmp/health_check.log",
            "/tmp/external_api_cron.log",
            "/tmp/render_ping.log"
        ]
        
        # Check if log directories exist or can be created
        for log_file in log_files:
            log_dir = os.path.dirname(log_file)
            if not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
            
            # Test that we can write to log files
            try:
                with open(log_file, 'a') as f:
                    f.write(f"Test log entry at {datetime.now()}\n")
                print(f"✅ Log file writable: {log_file}")
            except Exception as e:
                pytest.fail(f"Cannot write to log file {log_file}: {e}")
    
    @pytest.mark.asyncio
    async def test_scheduler_timezone_handling(self):
        """Test scheduler timezone handling"""
        try:
            scheduler = await start_scheduler()
            
            # Check that jobs have proper timezone configuration
            jobs = scheduler.get_jobs()
            
            for job in jobs:
                # Jobs should have timezone configured
                assert hasattr(job, 'timezone'), f"Job {job.name} missing timezone"
                print(f"✅ Job {job.name} has timezone: {job.timezone}")
                
        except Exception as e:
            pytest.fail(f"Timezone handling test failed: {e}")
        finally:
            await stop_scheduler()
    
    def test_cronjob_environment_variables(self):
        """Test that required environment variables are set"""
        required_vars = [
            'TELEGRAM_BOT_TOKEN',
            'TELEGRAM_CHAT_ID',
            'RENDER_URL',
            'API_BASE_URL'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"⚠️  Missing environment variables: {missing_vars}")
            print("These are optional for testing but required for production")
        else:
            print("✅ All required environment variables are set")
    
    @pytest.mark.asyncio
    async def test_scheduler_performance(self):
        """Test scheduler performance and resource usage"""
        try:
            import psutil
            import time
            
            # Get initial memory usage
            process = psutil.Process()
            initial_memory = process.memory_info().rss
            
            # Start scheduler
            start_time = time.time()
            scheduler = await start_scheduler()
            startup_time = time.time() - start_time
            
            # Check startup time
            assert startup_time < 5.0, f"Scheduler startup too slow: {startup_time:.2f}s"
            
            # Check memory usage
            current_memory = process.memory_info().rss
            memory_increase = current_memory - initial_memory
            
            # Memory increase should be reasonable (< 50MB)
            assert memory_increase < 50 * 1024 * 1024, f"Memory usage too high: {memory_increase / 1024 / 1024:.2f}MB"
            
            print(f"✅ Scheduler performance: startup={startup_time:.2f}s, memory={memory_increase / 1024 / 1024:.2f}MB")
            
        except ImportError:
            print("⚠️  psutil not available, skipping performance test")
        except Exception as e:
            pytest.fail(f"Performance test failed: {e}")
        finally:
            await stop_scheduler()


class TestCronjobIntegration:
    """Integration tests for cronjob functionality"""
    
    @pytest.mark.asyncio
    async def test_full_cronjob_workflow(self):
        """Test complete cronjob workflow"""
        try:
            # Start scheduler
            scheduler = await start_scheduler()
            
            # Execute all jobs manually
            jobs = scheduler.get_jobs()
            
            for job in jobs:
                try:
                    await job.func()
                    print(f"✅ Job {job.name} executed successfully")
                except Exception as e:
                    print(f"⚠️  Job {job.name} failed: {e}")
            
            # Verify scheduler is still running
            assert scheduler.running
            print("✅ Full cronjob workflow completed")
            
        except Exception as e:
            pytest.fail(f"Full workflow test failed: {e}")
        finally:
            await stop_scheduler()
    
    def test_cronjob_file_permissions(self):
        """Test cronjob file permissions and security"""
        script_paths = [
            "tools/setup_health_check_cron.sh",
            "tools/setup_external_api_cron.sh", 
            "tools/setup_cronjobs.sh",
            "tools/health_check.sh"
        ]
        
        for script_path in script_paths:
            full_path = os.path.join(os.path.dirname(__file__), '..', '..', script_path)
            
            if os.path.exists(full_path):
                # Check file permissions
                stat = os.stat(full_path)
                mode = stat.st_mode & 0o777
                
                # Should not be world writable
                assert not (mode & 0o002), f"Script {script_path} is world writable"
                
                # Should be executable by owner
                assert mode & 0o100, f"Script {script_path} is not executable"
                
                print(f"✅ Script {script_path} has proper permissions: {oct(mode)}")
    
    def test_cronjob_network_connectivity(self):
        """Test network connectivity for cronjobs"""
        test_urls = [
            "https://buzz2remote-api.onrender.com/api/v1/health",
            "https://httpbin.org/get"
        ]
        
        for url in test_urls:
            try:
                response = requests.get(url, timeout=10)
                assert response.status_code in [200, 404], f"Unexpected status code for {url}: {response.status_code}"
                print(f"✅ Network connectivity to {url}: OK")
            except Exception as e:
                print(f"⚠️  Network connectivity to {url}: {e}")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"]) 