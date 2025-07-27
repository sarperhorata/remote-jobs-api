import os
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from services.scheduler_service import SchedulerService


class TestSchedulerService:
    """Scheduler Service testleri"""

    @pytest.fixture
    def mock_scheduler(self):
        """Mock APScheduler"""
        mock_scheduler = Mock()
        mock_scheduler.start = Mock()
        mock_scheduler.shutdown = Mock()
        mock_scheduler.add_job = Mock()
        mock_scheduler.get_jobs = Mock(return_value=[])
        mock_scheduler.remove_job = Mock()
        mock_scheduler.pause_job = Mock()
        mock_scheduler.resume_job = Mock()
        return mock_scheduler

    @pytest.fixture
    def scheduler_service(self, mock_scheduler):
        """Scheduler service instance"""
        with patch(
            "services.scheduler_service.AsyncIOScheduler", return_value=mock_scheduler
        ):
            service = SchedulerService()
            service.scheduler = mock_scheduler
            return service

    @pytest.fixture
    def mock_external_services(self):
        """Mock external services"""
        with patch(
            "services.scheduler_service.ExternalJobAPIManager"
        ) as mock_api_manager, patch(
            "services.scheduler_service.ServiceNotifier"
        ) as mock_notifier, patch(
            "services.scheduler_service.DistillCrawler"
        ) as mock_crawler:

            mock_api_manager.return_value.fetch_all_jobs.return_value = []
            mock_api_manager.return_value.save_jobs_to_database.return_value = {
                "api1": 10,
                "api2": 5,
            }

            mock_notifier.return_value._send_message = Mock()

            mock_crawler.return_value.load_companies_data = Mock()
            mock_crawler.return_value.companies_data = [
                {"name": "Company1"},
                {"name": "Company2"},
            ]
            mock_crawler.return_value.crawl_all_companies = AsyncMock(
                return_value={"total_jobs": 15}
            )

            yield {
                "api_manager": mock_api_manager,
                "notifier": mock_notifier,
                "crawler": mock_crawler,
            }

    def test_service_initialization(self, scheduler_service):
        """Service başlatma testi"""
        assert scheduler_service is not None
        assert hasattr(scheduler_service, "scheduler")
        assert hasattr(scheduler_service, "is_running")
        assert hasattr(scheduler_service, "job_logs")
        assert scheduler_service.is_running is False

    @pytest.mark.asyncio
    async def test_start_scheduler_success(
        self, scheduler_service, mock_external_services
    ):
        """Başarılı scheduler başlatma testi"""
        result = await scheduler_service.start()

        assert result is True
        assert scheduler_service.is_running is True
        scheduler_service.scheduler.start.assert_called_once()
        scheduler_service.scheduler.add_job.assert_called()

    @pytest.mark.asyncio
    async def test_start_scheduler_disabled(self, scheduler_service):
        """Scheduler disabled olduğunda test"""
        with patch.dict(os.environ, {"DISABLE_SCHEDULER": "true"}):
            result = await scheduler_service.start()

            assert result is False
            assert scheduler_service.is_running is False
            scheduler_service.scheduler.start.assert_not_called()

    @pytest.mark.asyncio
    async def test_start_scheduler_already_running(self, scheduler_service):
        """Scheduler zaten çalışıyorken test"""
        scheduler_service.is_running = True

        result = await scheduler_service.start()

        assert result is True
        scheduler_service.scheduler.start.assert_not_called()

    @pytest.mark.asyncio
    async def test_start_scheduler_error(self, scheduler_service):
        """Scheduler başlatma hatası test"""
        scheduler_service.scheduler.start.side_effect = Exception("Scheduler error")

        result = await scheduler_service.start()

        assert result is False
        assert scheduler_service.is_running is False

    @pytest.mark.asyncio
    async def test_stop_scheduler_success(self, scheduler_service):
        """Başarılı scheduler durdurma testi"""
        scheduler_service.is_running = True

        await scheduler_service.stop()

        assert scheduler_service.is_running is False
        scheduler_service.scheduler.shutdown.assert_called_once()

    @pytest.mark.asyncio
    async def test_stop_scheduler_not_running(self, scheduler_service):
        """Scheduler çalışmıyorken durdurma test"""
        scheduler_service.is_running = False

        await scheduler_service.stop()

        scheduler_service.scheduler.shutdown.assert_not_called()

    @pytest.mark.asyncio
    async def test_stop_scheduler_error(self, scheduler_service):
        """Scheduler durdurma hatası test"""
        scheduler_service.is_running = True
        scheduler_service.scheduler.shutdown.side_effect = Exception("Shutdown error")

        with pytest.raises(Exception, match="Shutdown error"):
            await scheduler_service.stop()

    @pytest.mark.asyncio
    async def test_setup_jobs(self, scheduler_service):
        """Job setup testi"""
        await scheduler_service._setup_jobs()

        # Verify that all expected jobs are added
        add_job_calls = scheduler_service.scheduler.add_job.call_args_list

        # Check for health check job
        health_check_calls = [
            call for call in add_job_calls if "health_check" in str(call)
        ]
        assert len(health_check_calls) > 0

        # Check for external API crawler job
        external_api_calls = [
            call for call in add_job_calls if "external_api_crawler" in str(call)
        ]
        assert len(external_api_calls) > 0

        # Check for distill crawler job
        distill_calls = [
            call for call in add_job_calls if "distill_crawler" in str(call)
        ]
        assert len(distill_calls) > 0

        # Check for database cleanup job
        cleanup_calls = [
            call for call in add_job_calls if "database_cleanup" in str(call)
        ]
        assert len(cleanup_calls) > 0

    @pytest.mark.asyncio
    async def test_health_check_job(self, scheduler_service):
        """Health check job testi"""
        with patch("services.scheduler_service.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response

            await scheduler_service._health_check_job()

            mock_get.assert_called()

    @pytest.mark.asyncio
    async def test_external_api_crawler_job(
        self, scheduler_service, mock_external_services
    ):
        """External API crawler job testi"""
        await scheduler_service._external_api_crawler_job()

        # Verify that external services are called
        mock_external_services[
            "api_manager"
        ].return_value.fetch_all_jobs.assert_called_once()
        mock_external_services[
            "api_manager"
        ].return_value.save_jobs_to_database.assert_called_once()
        mock_external_services["notifier"].return_value._send_message.assert_called()

    @pytest.mark.asyncio
    async def test_distill_crawler_job(self, scheduler_service, mock_external_services):
        """Distill crawler job testi"""
        await scheduler_service._distill_crawler_job()

        # Verify that crawler services are called
        mock_external_services[
            "crawler"
        ].return_value.load_companies_data.assert_called_once()
        mock_external_services[
            "crawler"
        ].return_value.crawl_all_companies.assert_called_once()
        mock_external_services["notifier"].return_value._send_message.assert_called()

    @pytest.mark.asyncio
    async def test_database_cleanup_job(self, scheduler_service):
        """Database cleanup job testi"""
        with patch("services.scheduler_service.get_db") as mock_get_db:
            mock_db = Mock()
            mock_db.jobs.delete_many = AsyncMock(return_value=Mock(deleted_count=5))
            mock_db.users.delete_many = AsyncMock(return_value=Mock(deleted_count=2))
            mock_get_db.return_value = mock_db

            await scheduler_service._database_cleanup_job()

            mock_db.jobs.delete_many.assert_called_once()
            mock_db.users.delete_many.assert_called_once()

    @pytest.mark.asyncio
    async def test_log_job_run(self, scheduler_service):
        """Job run logging testi"""
        job_name = "test_job"
        status = "success"
        message = "Test job completed"
        metadata = {"test": "data"}

        await scheduler_service._log_job_run(job_name, status, message, metadata)

        # Verify that job log is stored
        assert job_name in scheduler_service.job_logs
        log_entry = scheduler_service.job_logs[job_name]
        assert log_entry["status"] == status
        assert log_entry["message"] == message
        assert log_entry["metadata"] == metadata
        assert "timestamp" in log_entry

    def test_get_job_status(self, scheduler_service):
        """Job status get testi"""
        job_name = "test_job"
        scheduler_service.job_logs[job_name] = {
            "status": "success",
            "message": "Test completed",
            "timestamp": datetime.now(),
        }

        status = scheduler_service.get_job_status(job_name)

        assert status is not None
        assert status["status"] == "success"
        assert status["message"] == "Test completed"

    def test_get_job_status_not_found(self, scheduler_service):
        """Job status bulunamadığında test"""
        status = scheduler_service.get_job_status("nonexistent_job")

        assert status is None

    def test_get_all_job_statuses(self, scheduler_service):
        """Tüm job status'ları get testi"""
        scheduler_service.job_logs = {
            "job1": {"status": "success", "timestamp": datetime.now()},
            "job2": {"status": "running", "timestamp": datetime.now()},
        }

        statuses = scheduler_service.get_all_job_statuses()

        assert len(statuses) == 2
        assert "job1" in statuses
        assert "job2" in statuses

    @pytest.mark.asyncio
    async def test_pause_job(self, scheduler_service):
        """Job pause testi"""
        job_id = "test_job"

        await scheduler_service.pause_job(job_id)

        scheduler_service.scheduler.pause_job.assert_called_once_with(job_id)

    @pytest.mark.asyncio
    async def test_resume_job(self, scheduler_service):
        """Job resume testi"""
        job_id = "test_job"

        await scheduler_service.resume_job(job_id)

        scheduler_service.scheduler.resume_job.assert_called_once_with(job_id)

    @pytest.mark.asyncio
    async def test_remove_job(self, scheduler_service):
        """Job remove testi"""
        job_id = "test_job"

        await scheduler_service.remove_job(job_id)

        scheduler_service.scheduler.remove_job.assert_called_once_with(job_id)

    def test_get_jobs_count(self, scheduler_service):
        """Jobs count get testi"""
        scheduler_service.scheduler.get_jobs.return_value = [Mock(), Mock(), Mock()]

        count = scheduler_service.get_jobs_count()

        assert count == 3
        scheduler_service.scheduler.get_jobs.assert_called_once()

    def test_is_job_running(self, scheduler_service):
        """Job running status testi"""
        job_id = "test_job"
        mock_job = Mock()
        mock_job.id = job_id
        mock_job.next_run_time = datetime.now() + timedelta(hours=1)
        scheduler_service.scheduler.get_jobs.return_value = [mock_job]

        is_running = scheduler_service.is_job_running(job_id)

        assert is_running is True

    def test_is_job_running_not_found(self, scheduler_service):
        """Job bulunamadığında running status test"""
        scheduler_service.scheduler.get_jobs.return_value = []

        is_running = scheduler_service.is_job_running("nonexistent_job")

        assert is_running is False

    def test_service_methods_exist(self, scheduler_service):
        """Service metodlarının varlığını test et"""
        required_methods = [
            "start",
            "stop",
            "_setup_jobs",
            "_health_check_job",
            "_external_api_crawler_job",
            "_distill_crawler_job",
            "_database_cleanup_job",
            "_log_job_run",
            "get_job_status",
            "get_all_job_statuses",
            "pause_job",
            "resume_job",
            "remove_job",
            "get_jobs_count",
            "is_job_running",
        ]

        for method in required_methods:
            assert hasattr(scheduler_service, method)
            assert callable(getattr(scheduler_service, method))

    @pytest.mark.asyncio
    async def test_service_integration(self, scheduler_service, mock_external_services):
        """Service integration testi"""
        # Test full lifecycle

        # Start scheduler
        result = await scheduler_service.start()
        assert result is True
        assert scheduler_service.is_running is True

        # Check job status
        statuses = scheduler_service.get_all_job_statuses()
        assert isinstance(statuses, dict)

        # Check jobs count
        count = scheduler_service.get_jobs_count()
        assert count >= 0

        # Stop scheduler
        await scheduler_service.stop()
        assert scheduler_service.is_running is False
