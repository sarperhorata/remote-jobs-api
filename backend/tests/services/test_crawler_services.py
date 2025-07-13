import pytest
from backend.crawler.job_crawler import JobCrawler
from backend.crawler.job_board_parser import JobBoardParser
from backend.crawler.monitor_manager import MonitorManager
from backend.crawler.jobs_from_space_parser import JobsFromSpaceParser
from backend.crawler.linkedin_parser import LinkedInParser
from backend.crawler.remotive_parser import RemotiveParser

class TestJobCrawler:
    def test_job_crawler_initialization(self):
        crawler = JobCrawler()
        assert crawler is not None
        # Temel attribute kontrolü
        assert hasattr(crawler, '__class__')

class TestJobBoardParser:
    def test_parser_initialization(self):
        parser = JobBoardParser()
        assert parser is not None
        assert hasattr(parser, '__class__')

class TestMonitorManager:
    def test_monitor_manager_initialization(self):
        manager = MonitorManager()
        assert manager is not None
        assert hasattr(manager, '__class__')

class TestJobsFromSpaceParser:
    def test_parser_initialization(self):
        parser = JobsFromSpaceParser()
        assert parser is not None
        assert hasattr(parser, '__class__')

class TestLinkedInParser:
    def test_parser_initialization(self):
        parser = LinkedInParser()
        assert parser is not None
        assert hasattr(parser, '__class__')

class TestRemotiveParser:
    def test_parser_initialization(self):
        parser = RemotiveParser()
        assert parser is not None
        assert hasattr(parser, '__class__') 