import pytest
import sys
import os

# Ensure the backend directory is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_pytest_is_working():
    """A simple sanity check to ensure pytest runs."""
    assert 1 + 1 == 2

def test_can_import_fastapi_app():
    """Checks if the main FastAPI app instance can be imported without errors."""
    try:
        from backend.main import app
        assert app is not None
    except ImportError as e:
        pytest.fail(f"Failed to import the FastAPI app from backend.main: {e}") 