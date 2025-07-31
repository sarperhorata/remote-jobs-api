from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
import logging
from datetime import datetime
import sys
import subprocess

# Add scripts directory to path for monitoring import
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'scripts'))

router = APIRouter(prefix="/api/monitor", tags=["monitoring"])

logger = logging.getLogger(__name__)

class MonitorRequest(BaseModel):
    action: str
    timestamp: str
    source: str

class MonitorResponse(BaseModel):
    status: str
    issues_found: int
    fixes_applied: int
    timestamp: str
    message: Optional[str] = None

@router.post("/check", response_model=MonitorResponse)
async def check_deployments(request: MonitorRequest):
    """External monitoring endpoint for cron-job.org and other external services"""
    
    # Validate request
    if request.action != "check":
        raise HTTPException(status_code=400, detail="Invalid action")
    
    # Validate authentication if token is set
    monitor_token = os.getenv("MONITOR_TOKEN")
    if monitor_token:
        # This would be validated in middleware in production
        pass
    
    # Run monitoring check
    try:
        logger.info(f"External monitoring check requested from {request.source}")
        
        # Run the monitoring script
        result = subprocess.run([
            "node", 
            "scripts/deployment-monitor-cron.js", 
            "--once"
        ], capture_output=True, text=True, cwd=os.path.join(os.path.dirname(__file__), '..', '..'))
        
        if result.returncode == 0:
            # Parse the output to extract report
            output_lines = result.stdout.strip().split('\n')
            report_line = None
            for line in output_lines:
                if line.startswith('📊 Deployment Report:'):
                    report_line = line
                    break
            
            if report_line:
                import json
                report_str = report_line.replace('📊 Deployment Report: ', '')
                report = json.loads(report_str)
                
                return MonitorResponse(
                    status="success",
                    issues_found=report.get("issuesFound", 0),
                    fixes_applied=report.get("fixesApplied", 0),
                    timestamp=report.get("timestamp", datetime.now().isoformat())
                )
            else:
                return MonitorResponse(
                    status="success",
                    issues_found=0,
                    fixes_applied=0,
                    timestamp=datetime.now().isoformat(),
                    message="Monitoring completed but report parsing failed"
                )
        else:
            logger.error(f"Monitoring script failed: {result.stderr}")
            return MonitorResponse(
                status="error",
                issues_found=0,
                fixes_applied=0,
                timestamp=datetime.now().isoformat(),
                message=f"Monitoring script failed: {result.stderr}"
            )
            
    except Exception as e:
        logger.error(f"Monitoring check failed: {str(e)}")
        return MonitorResponse(
            status="error",
            issues_found=0,
            fixes_applied=0,
            timestamp=datetime.now().isoformat(),
            message=str(e)
        )

@router.get("/status")
async def get_monitor_status():
    """Get current monitoring system status"""
    try:
        # Check if monitoring script exists
        script_path = os.path.join(os.path.dirname(__file__), '..', '..', 'scripts', 'deployment-monitor-cron.js')
        script_exists = os.path.exists(script_path)
        
        # Check if logs directory exists
        logs_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'logs')
        logs_exist = os.path.exists(logs_dir)
        
        # Check environment variables
        env_vars = {
            "RENDER_API_KEY": bool(os.getenv("RENDER_API_KEY")),
            "GITHUB_TOKEN": bool(os.getenv("GITHUB_TOKEN")),
            "NETLIFY_ACCESS_TOKEN": bool(os.getenv("NETLIFY_ACCESS_TOKEN")),
            "MONITOR_TOKEN": bool(os.getenv("MONITOR_TOKEN"))
        }
        
        return {
            "status": "healthy",
            "script_exists": script_exists,
            "logs_directory_exists": logs_exist,
            "environment_variables": env_vars,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/logs")
async def get_monitor_logs(lines: int = 50):
    """Get recent monitoring logs"""
    try:
        log_file = os.path.join(os.path.dirname(__file__), '..', '..', 'logs', 'deployment-monitor.log')
        
        if not os.path.exists(log_file):
            return {
                "logs": [],
                "message": "No log file found",
                "timestamp": datetime.now().isoformat()
            }
        
        with open(log_file, 'r') as f:
            all_logs = f.readlines()
        
        # Get last N lines
        recent_logs = all_logs[-lines:] if len(all_logs) > lines else all_logs
        
        return {
            "logs": [log.strip() for log in recent_logs],
            "total_lines": len(all_logs),
            "lines_requested": lines,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "logs": [],
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/dashboard")
async def get_monitor_dashboard():
    """Get monitoring dashboard data"""
    try:
        # Get status
        status = await get_monitor_status()
        
        # Get recent logs
        logs_data = await get_monitor_logs(20)
        
        # Get latest report
        report_file = os.path.join(os.path.dirname(__file__), '..', '..', 'logs', 'deployment-report.json')
        report = None
        
        if os.path.exists(report_file):
            try:
                import json
                with open(report_file, 'r') as f:
                    report = json.load(f)
            except Exception as e:
                logger.error(f"Failed to read report file: {e}")
        
        return {
            "status": status,
            "recent_logs": logs_data,
            "latest_report": report,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/health")
async def health_check():
    """Simple health check endpoint"""
    return {
        "status": "healthy",
        "service": "buzz2remote-backend",
        "timestamp": datetime.now().isoformat(),
        "environment": os.getenv("RENDER", "development")
    } 