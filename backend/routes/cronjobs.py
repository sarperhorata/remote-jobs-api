"""
Cronjob Routes for External Triggers
Handles HTTP endpoints that can be called from cron-job.org
"""

import asyncio
import logging
import os
import subprocess
import sys
from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import JSONResponse

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/cron", tags=["cronjobs"])

# Security token for cronjob endpoints
CRON_SECRET = os.getenv("CRON_SECRET_TOKEN", "buzz2remote_cron_2024")


def verify_cron_token(token: str = None):
    """Verify cronjob security token"""
    if not token or token != CRON_SECRET:
        raise HTTPException(status_code=401, detail="Invalid cron token")
    return True


async def run_script_async(script_path: str, script_name: str) -> Dict[str, Any]:
    """Run a cronjob script asynchronously"""
    try:
        # Get the virtual environment python path
        venv_python = os.path.join(project_root, ".venv", "bin", "python3")

        # Run the script
        process = await asyncio.create_subprocess_exec(
            venv_python,
            script_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=project_root,
        )

        stdout, stderr = await process.communicate()

        return {
            "script": script_name,
            "success": process.returncode == 0,
            "return_code": process.returncode,
            "stdout": stdout.decode("utf-8") if stdout else "",
            "stderr": stderr.decode("utf-8") if stderr else "",
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error running {script_name}: {e}")
        return {
            "script": script_name,
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


@router.get("/health")
async def cron_health():
    """Health check for cronjob system"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "message": "Cronjob system is operational",
    }


@router.post("/database-cleanup")
async def trigger_database_cleanup(
    background_tasks: BackgroundTasks, token: str = None
):
    """Trigger database cleanup cronjob"""
    verify_cron_token(token)

    script_path = os.path.join(project_root, "cron_database_cleanup.py")

    # Run in background
    background_tasks.add_task(run_script_async, script_path, "database_cleanup")

    return {
        "status": "triggered",
        "job": "database_cleanup",
        "timestamp": datetime.now().isoformat(),
        "message": "Database cleanup started in background",
    }


@router.post("/external-api-crawler")
async def trigger_external_api_crawler(
    background_tasks: BackgroundTasks, token: str = None
):
    """Trigger external API crawler cronjob"""
    verify_cron_token(token)

    script_path = os.path.join(project_root, "cron_external_apis.py")

    # Set environment variables
    os.environ["TELEGRAM_BOT_TOKEN"] = "8116251711:AAFhGxXtOJu2eCqCORoDr46XWq7ejqMeYnY"
    os.environ["TELEGRAM_CHAT_ID"] = "-1002424698891"

    # Run in background
    background_tasks.add_task(run_script_async, script_path, "external_api_crawler")

    return {
        "status": "triggered",
        "job": "external_api_crawler",
        "timestamp": datetime.now().isoformat(),
        "message": "External API crawler started in background",
    }


@router.post("/job-statistics")
async def trigger_job_statistics(background_tasks: BackgroundTasks, token: str = None):
    """Trigger job statistics generation cronjob"""
    verify_cron_token(token)

    script_path = os.path.join(project_root, "cron_job_statistics.py")

    # Run in background
    background_tasks.add_task(run_script_async, script_path, "job_statistics")

    return {
        "status": "triggered",
        "job": "job_statistics",
        "timestamp": datetime.now().isoformat(),
        "message": "Job statistics generation started in background",
    }


@router.post("/distill-crawler")
async def trigger_distill_crawler(background_tasks: BackgroundTasks, token: str = None):
    """Trigger Distill crawler cronjob"""
    verify_cron_token(token)

    script_path = os.path.join(project_root, "cron_distill_crawler.py")

    # Run in background
    background_tasks.add_task(run_script_async, script_path, "distill_crawler")

    return {
        "status": "triggered",
        "job": "distill_crawler",
        "timestamp": datetime.now().isoformat(),
        "message": "Distill crawler started in background",
    }


@router.post("/cron-status")
async def trigger_cron_status(background_tasks: BackgroundTasks, token: str = None):
    """Trigger cron status monitor cronjob"""
    verify_cron_token(token)

    script_path = os.path.join(project_root, "cron_status_monitor.py")

    # Run in background
    background_tasks.add_task(run_script_async, script_path, "cron_status")

    return {
        "status": "triggered",
        "job": "cron_status",
        "timestamp": datetime.now().isoformat(),
        "message": "Cron status monitor started in background",
    }


@router.post("/test-timeout")
async def trigger_test_timeout(background_tasks: BackgroundTasks, token: str = None):
    """Trigger test timeout monitor cronjob"""
    verify_cron_token(token)

    script_path = os.path.join(project_root, "cron_test_timeout.py")

    # Run in background
    background_tasks.add_task(run_script_async, script_path, "test_timeout")

    return {
        "status": "triggered",
        "job": "test_timeout",
        "timestamp": datetime.now().isoformat(),
        "message": "Test timeout monitor started in background",
    }


@router.get("/status")
async def get_cron_status(token: str = None):
    """Get status of all cronjobs"""
    verify_cron_token(token)

    # Run cron status script and return results
    try:
        script_path = os.path.join(project_root, "cron_status_monitor.py")
        result = await run_script_async(script_path, "cron_status_check")

        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "cron_status": result,
        }

    except Exception as e:
        logger.error(f"Error getting cron status: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


@router.post("/run-all")
async def trigger_all_cronjobs(background_tasks: BackgroundTasks, token: str = None):
    """Trigger all cronjobs (use with caution)"""
    verify_cron_token(token)

    jobs = [
        ("cron_database_cleanup.py", "database_cleanup"),
        ("cron_external_apis.py", "external_api_crawler"),
        ("cron_job_statistics.py", "job_statistics"),
        ("cron_distill_crawler.py", "distill_crawler"),
        ("cron_status_monitor.py", "cron_status"),
        ("cron_test_timeout.py", "test_timeout"),
    ]

    # Set environment variables for external API crawler
    os.environ["TELEGRAM_BOT_TOKEN"] = "8116251711:AAFhGxXtOJu2eCqCORoDr46XWq7ejqMeYnY"
    os.environ["TELEGRAM_CHAT_ID"] = "-1002424698891"

    for script_file, job_name in jobs:
        script_path = os.path.join(project_root, script_file)
        background_tasks.add_task(run_script_async, script_path, job_name)

    return {
        "status": "triggered",
        "jobs_count": len(jobs),
        "timestamp": datetime.now().isoformat(),
        "message": f"All {len(jobs)} cronjobs started in background",
    }


@router.get("/logs/{job_name}")
async def get_job_logs(job_name: str, token: str = None, lines: int = 100):
    """Get recent logs for a specific cronjob"""
    verify_cron_token(token)

    try:
        log_file = os.path.join(project_root, "logs", f"{job_name}.log")

        if not os.path.exists(log_file):
            raise HTTPException(
                status_code=404, detail=f"Log file not found: {job_name}"
            )

        # Read last N lines
        process = await asyncio.create_subprocess_exec(
            "tail",
            "-n",
            str(lines),
            log_file,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            raise HTTPException(status_code=500, detail="Error reading log file")

        return {
            "job": job_name,
            "lines": lines,
            "content": stdout.decode("utf-8"),
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error reading logs for {job_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Quick test endpoints (no auth required for debugging)
@router.get("/test-endpoints")
async def test_all_endpoints():
    """Test all cronjob endpoints (for debugging)"""
    endpoints = [
        f"/api/v1/cron/health",
        f"/api/v1/cron/database-cleanup?token={CRON_SECRET}",
        f"/api/v1/cron/external-api-crawler?token={CRON_SECRET}",
        f"/api/v1/cron/job-statistics?token={CRON_SECRET}",
        f"/api/v1/cron/distill-crawler?token={CRON_SECRET}",
        f"/api/v1/cron/cron-status?token={CRON_SECRET}",
        f"/api/v1/cron/test-timeout?token={CRON_SECRET}",
        f"/api/v1/cron/status?token={CRON_SECRET}",
        f"/api/v1/cron/run-all?token={CRON_SECRET}",
    ]

    return {
        "message": "Available cronjob endpoints",
        "endpoints": endpoints,
        "base_url": "https://buzz2remote-api.onrender.com",
        "cron_secret": CRON_SECRET,
        "instructions": {
            "health": "GET - No auth required",
            "other_endpoints": "POST - Requires token parameter",
            "status": "GET - Requires token parameter",
            "logs": "GET /logs/{job_name}?token=xxx - Get job logs",
        },
    }
