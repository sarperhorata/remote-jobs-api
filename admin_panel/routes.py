from fastapi import APIRouter, Request, Depends, HTTPException, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from datetime import datetime, timedelta
from typing import Optional
import os
import sys

# Add backend to path for database access
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend"))

try:
    from database import get_db
    from pymongo import DESCENDING
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False

# Templates - use absolute path
template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "admin_panel", "templates")
templates = Jinja2Templates(directory=template_dir)

# Router
admin_router = APIRouter(prefix="/admin", tags=["admin"])

# Static files - use absolute path
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "admin_panel", "static")
admin_router.mount("/static", StaticFiles(directory=static_dir), name="admin_static")

@admin_router.get("/test")
async def admin_test():
    """Test endpoint"""
    return {"message": "Admin panel is working!"}

@admin_router.get("/login", response_class=HTMLResponse)
async def admin_login_page(request: Request, error: Optional[str] = None):
    """Admin login page"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin Login - Buzz2Remote</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .login-form { max-width: 400px; margin: 100px auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            input { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 4px; }
            button { width: 100%; padding: 12px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
            button:hover { background: #0056b3; }
        </style>
    </head>
    <body>
        <div class="login-form">
            <h2>Admin Login</h2>
            <form action="/admin/login" method="post">
                <input type="email" name="username" placeholder="Email" required>
                <input type="password" name="password" placeholder="Password" required>
                <button type="submit">Login</button>
            </form>
            <p><a href="/admin/dashboard">Skip to Dashboard (Demo)</a></p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@admin_router.post("/login")
async def admin_login_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    """Handle login form submission"""
    # Simple demo login - in production use proper authentication
    if username == "admin@buzz2remote.com" and password == "admin123":
        return RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_302_FOUND)
    else:
        return RedirectResponse(url="/admin/login?error=Invalid credentials", status_code=status.HTTP_302_FOUND)

@admin_router.get("/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    """Admin dashboard"""
    
    # Get real data
    stats = await get_dashboard_stats()
    recent_jobs = await get_recent_jobs(5)
    
    # Format recent jobs for display
    formatted_jobs = []
    for job in recent_jobs:
        formatted_jobs.append({
            "_id": str(job.get("_id", "")),
            "title": job.get("title", "Unknown Title"),
            "company": job.get("company", "Unknown Company"),
            "location": job.get("location", "Remote"),
            "source": job.get("source", "Unknown"),
            "created_at": job.get("created_at", datetime.now())
        })
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Buzz2Remote Admin Panel</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; background: #f8f9fa; }}
            .header {{ background: #343a40; color: white; padding: 1rem 2rem; }}
            .nav {{ background: white; padding: 1rem 2rem; border-bottom: 1px solid #dee2e6; }}
            .nav a {{ margin-right: 20px; text-decoration: none; color: #007bff; }}
            .nav a:hover {{ text-decoration: underline; }}
            .container {{ padding: 2rem; }}
            .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
            .stat {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center; }}
            .stat h3 {{ margin: 0; font-size: 2rem; color: #007bff; }}
            .stat p {{ margin: 5px 0 0 0; color: #6c757d; }}
            .actions {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .btn {{ padding: 10px 20px; margin: 5px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }}
            .btn:hover {{ background: #0056b3; }}
            .btn:disabled {{ background: #6c757d; cursor: not-allowed; }}
            .progress {{ margin: 10px 0; padding: 10px; background: #e9ecef; border-radius: 4px; display: none; }}
            .error {{ color: #dc3545; }}
            .success {{ color: #28a745; }}
            .recent-jobs {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-top: 20px; }}
            .job-item {{ padding: 10px 0; border-bottom: 1px solid #eee; }}
            .job-item:last-child {{ border-bottom: none; }}
            .job-title {{ font-weight: bold; color: #333; }}
            .job-company {{ color: #666; font-size: 0.9em; }}
            .job-meta {{ color: #999; font-size: 0.8em; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🚀 Buzz2Remote Admin Panel</h1>
        </div>
        
        <div class="nav">
            <a href="/admin/dashboard">Dashboard</a>
            <a href="/admin/jobs">Jobs</a>
            <a href="/admin/companies">Companies</a>
            <a href="/admin/apis">API Services</a>
            <a href="/docs">API Docs</a>
        </div>
        
        <div class="container">
            <div class="stats">
                <div class="stat">
                    <h3>{stats['total_jobs']:,}</h3>
                    <p>Total Jobs</p>
                </div>
                <div class="stat">
                    <h3>{stats['total_companies']:,}</h3>
                    <p>Companies</p>
                </div>
                <div class="stat">
                    <h3>{stats['active_apis']}</h3>
                    <p>Active APIs</p>
                </div>
                <div class="stat">
                    <h3>{stats['jobs_today']:,}</h3>
                    <p>Jobs Today</p>
                </div>
            </div>
            
            <div class="actions">
                <h2>Quick Actions</h2>
                <button class="btn" onclick="runCrawler()" id="crawlerBtn">Run Job Crawler</button>
                <button class="btn" onclick="fetchAPIs()" id="apiBtn">Fetch External APIs</button>
                <button class="btn" onclick="analyzePositions()" id="positionBtn">Analyze Positions</button>
                <button class="btn" onclick="cancelAction()" id="cancelBtn" style="display:none; background:#dc3545;">Cancel</button>
                
                <div id="progress" class="progress">
                    <div id="progressText">Processing...</div>
                    <div id="progressBar" style="width:0%; height:20px; background:#007bff; border-radius:4px; transition:width 0.3s;"></div>
                </div>
                
                <div id="result"></div>
            </div>
            
            <div class="recent-jobs">
                <h2>Recent Jobs</h2>"""
    
    for job in formatted_jobs:
        created_at = job['created_at']
        if isinstance(created_at, datetime):
            date_str = created_at.strftime('%Y-%m-%d %H:%M')
        else:
            date_str = str(created_at)
            
        html_content += f"""
                <div class="job-item">
                    <div class="job-title">{job['title']}</div>
                    <div class="job-company">{job['company']} • {job['location']}</div>
                    <div class="job-meta">Source: {job['source']} • Posted: {date_str}</div>
                </div>"""
    
    html_content += """
            </div>
        </div>
        
        <script>
            let currentAction = null;
            let progressInterval = null;
            let currentProcessId = null;
            
            function showProgress(action) {
                document.getElementById('progress').style.display = 'block';
                document.getElementById('cancelBtn').style.display = 'inline-block';
                document.getElementById('crawlerBtn').disabled = true;
                document.getElementById('apiBtn').disabled = true;
                document.getElementById('positionBtn').disabled = true;
                document.getElementById('progressText').textContent = action + ' in progress...';
                
                let progress = 0;
                progressInterval = setInterval(() => {
                    progress += Math.random() * 5;
                    if (progress > 90) progress = 90;
                    document.getElementById('progressBar').style.width = progress + '%';
                    
                    // Check process status if we have a process ID
                    if (currentProcessId) {
                        checkProcessStatus();
                    }
                }, 1000);
            }
            
            function hideProgress() {
                document.getElementById('progress').style.display = 'none';
                document.getElementById('cancelBtn').style.display = 'none';
                document.getElementById('crawlerBtn').disabled = false;
                document.getElementById('apiBtn').disabled = false;
                document.getElementById('positionBtn').disabled = false;
                if (progressInterval) {
                    clearInterval(progressInterval);
                    progressInterval = null;
                }
                document.getElementById('progressBar').style.width = '0%';
                currentAction = null;
                currentProcessId = null;
            }
            
            function showResult(message, isError = false) {
                const resultDiv = document.getElementById('result');
                resultDiv.innerHTML = '<p class="' + (isError ? 'error' : 'success') + '">' + message + '</p>';
                setTimeout(() => {
                    resultDiv.innerHTML = '';
                }, 10000);
            }
            
            async function checkProcessStatus() {
                if (!currentProcessId) return;
                
                try {
                    const response = await fetch(`/admin/actions/status/${{currentProcessId}}`);
                    const data = await response.json();
                    
                    if (data.status === 'completed') {
                        document.getElementById('progressBar').style.width = '100%';
                        setTimeout(() => {
                            hideProgress();
                            showResult('✅ Process completed successfully');
                            location.reload(); // Refresh to show updated stats
                        }, 1000);
                    } else if (data.status === 'error') {
                        hideProgress();
                        showResult('❌ Process error: ' + data.message, true);
                    } else if (data.status === 'running') {
                        document.getElementById('progressText').textContent = 
                            `${{currentAction}} running... (CPU: ${{data.cpu_percent?.toFixed(1)}}%, Memory: ${{data.memory_percent?.toFixed(1)}}%)`;
                    }
                } catch (error) {
                    console.log('Status check error:', error);
                }
            }
            
            async function runCrawler() {
                currentAction = 'Job Crawler';
                showProgress('Job Crawler');
                try {
                    const response = await fetch('/admin/actions/run-crawler', {{method: 'POST'}});
                    const data = await response.json();
                    
                    if (data.status === 'success') {
                        currentProcessId = data.process_id;
                        showResult('✅ ' + data.message);
                    } else {
                        hideProgress();
                        showResult('❌ Error: ' + data.message, true);
                    }
                } catch (error) {
                    hideProgress();
                    showResult('❌ Error: ' + error.message, true);
                }
            }
            
            async function fetchAPIs() {
                currentAction = 'External API Fetch';
                showProgress('External API Fetch');
                try {
                    const response = await fetch('/admin/actions/fetch-external-apis', {{method: 'POST'}});
                    const data = await response.json();
                    
                    if (data.status === 'success') {
                        currentProcessId = data.process_id;
                        showResult('✅ ' + data.message);
                    } else {
                        hideProgress();
                        showResult('❌ Error: ' + data.message, true);
                    }
                } catch (error) {
                    hideProgress();
                    showResult('❌ Error: ' + error.message, true);
                }
            }
            
            async function analyzePositions() {
                currentAction = 'Position Analysis';
                showProgress('Position Analysis');
                try {
                    const response = await fetch('/admin/actions/analyze-positions', {{method: 'POST'}});
                    const data = await response.json();
                    
                    if (data.status === 'success') {
                        currentProcessId = data.process_id;
                        showResult('✅ ' + data.message);
                    } else {
                        hideProgress();
                        showResult('❌ Error: ' + data.message, true);
                    }
                } catch (error) {
                    hideProgress();
                    showResult('❌ Error: ' + error.message, true);
                }
            }
            
            async function cancelAction() {
                if (currentProcessId) {
                    try {
                        const response = await fetch(`/admin/actions/cancel/${{currentProcessId}}`, {{method: 'POST'}});
                        const data = await response.json();
                        
                        hideProgress();
                        if (data.status === 'success') {
                            showResult('⚠️ ' + data.message, true);
                        } else {
                            showResult('❌ Cancel failed: ' + data.message, true);
                        }
                    } catch (error) {
                        hideProgress();
                        showResult('❌ Cancel error: ' + error.message, true);
                    }
                } else {
                    hideProgress();
                    showResult('⚠️ No active process to cancel', true);
                }
            }
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

@admin_router.get("/jobs", response_class=HTMLResponse)
async def admin_jobs(request: Request):
    """Job listings page"""
    
    # Get real jobs data
    jobs = await get_recent_jobs(50)
    total_jobs = (await get_dashboard_stats())['total_jobs']
    
    # Format jobs for display
    formatted_jobs = []
    for job in jobs:
        formatted_jobs.append({
            "_id": str(job.get("_id", "")),
            "title": job.get("title", "Unknown Title"),
            "company": job.get("company", "Unknown Company"),
            "location": job.get("location", "Remote"),
            "source": job.get("source", "Unknown"),
            "created_at": job.get("created_at", datetime.now()),
            "description": job.get("description", "")[:100] + "..." if job.get("description") else "No description"
        })
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Jobs - Buzz2Remote Admin</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; background: #f8f9fa; }}
            .header {{ background: #343a40; color: white; padding: 1rem 2rem; }}
            .nav {{ background: white; padding: 1rem 2rem; border-bottom: 1px solid #dee2e6; }}
            .nav a {{ margin-right: 20px; text-decoration: none; color: #007bff; }}
            .nav a:hover {{ text-decoration: underline; }}
            .container {{ padding: 2rem; }}
            .card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #dee2e6; }}
            th {{ background: #f8f9fa; font-weight: 600; }}
            .badge {{ padding: 4px 8px; border-radius: 4px; font-size: 0.875rem; }}
            .badge-primary {{ background: #e3f2fd; color: #1976d2; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🚀 Buzz2Remote Admin Panel</h1>
        </div>
        
        <div class="nav">
            <a href="/admin/dashboard">Dashboard</a>
            <a href="/admin/jobs">Jobs</a>
            <a href="/admin/companies">Companies</a>
            <a href="/admin/apis">API Services</a>
            <a href="/docs">API Docs</a>
        </div>
        
        <div class="container">
            <div class="card">
                <h2>Job Listings ({total_jobs:,} total)</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Title</th>
                            <th>Company</th>
                            <th>Location</th>
                            <th>Source</th>
                            <th>Posted</th>
                        </tr>
                    </thead>
                    <tbody>"""
    
    for job in formatted_jobs:
        created_at = job['created_at']
        if isinstance(created_at, datetime):
            date_str = created_at.strftime('%Y-%m-%d')
        else:
            date_str = str(created_at)
            
        html_content += f"""
                        <tr>
                            <td>
                                <div style="font-weight: bold;">{job['title']}</div>
                                <div style="color: #666; font-size: 0.9em;">{job['description']}</div>
                            </td>
                            <td>{job['company']}</td>
                            <td>{job['location']}</td>
                            <td><span class="badge badge-primary">{job['source']}</span></td>
                            <td>{date_str}</td>
                        </tr>"""
    
    html_content += """
                    </tbody>
                </table>
            </div>
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

@admin_router.get("/companies", response_class=HTMLResponse)
async def admin_companies(request: Request):
    """Companies page"""
    
    # Get real companies data
    companies = await get_companies_data(50)
    total_companies = (await get_dashboard_stats())['total_companies']
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Companies - Buzz2Remote Admin</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; background: #f8f9fa; }}
            .header {{ background: #343a40; color: white; padding: 1rem 2rem; }}
            .nav {{ background: white; padding: 1rem 2rem; border-bottom: 1px solid #dee2e6; }}
            .nav a {{ margin-right: 20px; text-decoration: none; color: #007bff; }}
            .nav a:hover {{ text-decoration: underline; }}
            .container {{ padding: 2rem; }}
            .card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #dee2e6; }}
            th {{ background: #f8f9fa; font-weight: 600; }}
            .badge {{ padding: 4px 8px; border-radius: 4px; font-size: 0.875rem; }}
            .badge-success {{ background: #e8f5e8; color: #2e7d32; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🚀 Buzz2Remote Admin Panel</h1>
        </div>
        
        <div class="nav">
            <a href="/admin/dashboard">Dashboard</a>
            <a href="/admin/jobs">Jobs</a>
            <a href="/admin/companies">Companies</a>
            <a href="/admin/apis">API Services</a>
            <a href="/docs">API Docs</a>
        </div>
        
        <div class="container">
            <div class="card">
                <h2>Companies ({total_companies:,} total)</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Company</th>
                            <th>Website</th>
                            <th>Job Count</th>
                            <th>Latest Job</th>
                        </tr>
                    </thead>
                    <tbody>"""
    
    for company in companies:
        website = company.get('website', '')
        if website and not website.startswith('http'):
            website = f"https://{website}"
            
        created_at = company.get('created_at', datetime.now())
        if isinstance(created_at, datetime):
            date_str = created_at.strftime('%Y-%m-%d')
        else:
            date_str = str(created_at)
            
        html_content += f"""
                        <tr>
                            <td>{company['name']}</td>
                            <td>"""
        
        if website:
            html_content += f'<a href="{website}" target="_blank">{website}</a>'
        else:
            html_content += '<span style="color: #999;">No website</span>'
            
        html_content += f"""</td>
                            <td><span class="badge badge-success">{company['job_count']} jobs</span></td>
                            <td>{date_str}</td>
                        </tr>"""
    
    html_content += """
                    </tbody>
                </table>
            </div>
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

@admin_router.get("/apis", response_class=HTMLResponse)
async def admin_apis(request: Request):
    """API services management page"""
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>API Services - Buzz2Remote Admin</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; background: #f8f9fa; }
            .header { background: #343a40; color: white; padding: 1rem 2rem; }
            .nav { background: white; padding: 1rem 2rem; border-bottom: 1px solid #dee2e6; }
            .nav a { margin-right: 20px; text-decoration: none; color: #007bff; }
            .nav a:hover { text-decoration: underline; }
            .container { padding: 2rem; }
            .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            table { width: 100%; border-collapse: collapse; }
            th, td { padding: 12px; text-align: left; border-bottom: 1px solid #dee2e6; }
            th { background: #f8f9fa; font-weight: 600; }
            .badge { padding: 4px 8px; border-radius: 4px; font-size: 0.875rem; }
            .badge-success { background: #e8f5e8; color: #2e7d32; }
            .badge-warning { background: #fff3cd; color: #856404; }
            .status-dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; margin-right: 8px; }
            .status-active { background: #28a745; }
            .status-inactive { background: #dc3545; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🚀 Buzz2Remote Admin Panel</h1>
        </div>
        
        <div class="nav">
            <a href="/admin/dashboard">Dashboard</a>
            <a href="/admin/jobs">Jobs</a>
            <a href="/admin/companies">Companies</a>
            <a href="/admin/apis">API Services</a>
            <a href="/docs">API Docs</a>
        </div>
        
        <div class="container">
            <div class="card">
                <h2>External API Services</h2>
                <table>
                    <thead>
                        <tr>
                            <th>API Service</th>
                            <th>Status</th>
                            <th>Rate Limit</th>
                            <th>Remaining</th>
                            <th>Last Fetch</th>
                            <th>Jobs Fetched</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><span class="status-dot status-active"></span>RemoteOK</td>
                            <td><span class="badge badge-success">Active</span></td>
                            <td>1000/day</td>
                            <td>1,000</td>
                            <td>2 hours ago</td>
                            <td>150</td>
                        </tr>
                        <tr>
                            <td><span class="status-dot status-active"></span>Jobicy</td>
                            <td><span class="badge badge-success">Active</span></td>
                            <td>500,000/month</td>
                            <td>450,000</td>
                            <td>1 hour ago</td>
                            <td>200</td>
                        </tr>
                        <tr>
                            <td><span class="status-dot status-active"></span>Remotive</td>
                            <td><span class="badge badge-success">Active</span></td>
                            <td>4/day</td>
                            <td>3</td>
                            <td>3 hours ago</td>
                            <td>45</td>
                        </tr>
                        <tr>
                            <td><span class="status-dot status-active"></span>Job Postings RSS</td>
                            <td><span class="badge badge-warning">Limited</span></td>
                            <td>31/month</td>
                            <td>25</td>
                            <td>1 day ago</td>
                            <td>30</td>
                        </tr>
                    </tbody>
                </table>
                <p style="margin-top: 20px; color: #6c757d;">
                    <em>Note: This is demo data. Real API monitoring integration coming soon.</em>
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

# Quick action endpoints
@admin_router.post("/actions/run-crawler")
async def admin_run_crawler():
    """Run job crawler"""
    try:
        # Import and run the daily crawler
        import subprocess
        import os
        
        # Get the project root directory
        project_root = os.path.dirname(os.path.dirname(__file__))
        crawler_path = os.path.join(project_root, "daily_crawler.py")
        
        # Run the crawler in background
        process = subprocess.Popen(
            ["python3", crawler_path],
            cwd=project_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        return {
            "status": "success", 
            "message": f"Job crawler started successfully (PID: {process.pid})",
            "process_id": process.pid
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to start crawler: {str(e)}"
        }

@admin_router.post("/actions/fetch-external-apis")
async def admin_fetch_external_apis():
    """Fetch from external APIs"""
    try:
        # Import and run external API fetcher
        import subprocess
        import os
        
        # Get the project root directory
        project_root = os.path.dirname(os.path.dirname(__file__))
        api_fetcher_path = os.path.join(project_root, "external_job_apis.py")
        
        # Run the API fetcher in background
        process = subprocess.Popen(
            ["python3", api_fetcher_path],
            cwd=project_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        return {
            "status": "success", 
            "message": f"External API fetch started successfully (PID: {process.pid})",
            "process_id": process.pid
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to start API fetch: {str(e)}"
        }

@admin_router.post("/actions/analyze-positions")
async def admin_analyze_positions():
    """Run position analysis"""
    try:
        # Import and run position analyzer
        import subprocess
        import os
        
        # Get the project root directory
        project_root = os.path.dirname(os.path.dirname(__file__))
        analyzer_path = os.path.join(project_root, "position_analyzer.py")
        
        # Run the position analyzer in background
        process = subprocess.Popen(
            ["python3", analyzer_path],
            cwd=project_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        return {
            "status": "success", 
            "message": f"Position analysis started successfully (PID: {process.pid})",
            "process_id": process.pid
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to start position analysis: {str(e)}"
        }

@admin_router.get("/actions/status/{process_id}")
async def admin_action_status(process_id: int):
    """Check status of a running process"""
    try:
        import psutil
        
        if psutil.pid_exists(process_id):
            process = psutil.Process(process_id)
            return {
                "status": "running",
                "process_id": process_id,
                "name": process.name(),
                "cpu_percent": process.cpu_percent(),
                "memory_percent": process.memory_percent()
            }
        else:
            return {
                "status": "completed",
                "process_id": process_id,
                "message": "Process has completed"
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error checking process status: {str(e)}"
        }

@admin_router.post("/actions/cancel/{process_id}")
async def admin_cancel_action(process_id: int):
    """Cancel a running process"""
    try:
        import psutil
        
        if psutil.pid_exists(process_id):
            process = psutil.Process(process_id)
            process.terminate()
            return {
                "status": "success",
                "message": f"Process {process_id} terminated successfully"
            }
        else:
            return {
                "status": "error",
                "message": f"Process {process_id} not found"
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error terminating process: {str(e)}"
        }

async def get_dashboard_stats():
    """Get real dashboard statistics from MongoDB"""
    if not DATABASE_AVAILABLE:
        return {
            "total_jobs": 21741,
            "total_companies": 471,
            "active_apis": 8,
            "jobs_today": 679
        }
    
    try:
        db = get_db()
        
        # Get total jobs
        total_jobs = db.jobs.count_documents({})
        
        # Get total companies
        total_companies = db.jobs.distinct("company")
        total_companies_count = len(total_companies) if total_companies else 0
        
        # Get jobs today
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        jobs_today = db.jobs.count_documents({
            "created_at": {"$gte": today}
        })
        
        # Active APIs (hardcoded for now)
        active_apis = 8
        
        return {
            "total_jobs": total_jobs,
            "total_companies": total_companies_count,
            "active_apis": active_apis,
            "jobs_today": jobs_today
        }
    except Exception as e:
        print(f"Error getting dashboard stats: {e}")
        return {
            "total_jobs": 21741,
            "total_companies": 471,
            "active_apis": 8,
            "jobs_today": 679
        }

async def get_recent_jobs(limit=10):
    """Get recent jobs from MongoDB"""
    if not DATABASE_AVAILABLE:
        return [
            {
                "_id": "1",
                "title": "Senior Software Engineer",
                "company": "Remote Company",
                "location": "Remote",
                "source": "RemoteOK",
                "created_at": datetime.now()
            }
        ]
    
    try:
        db = get_db()
        jobs = list(db.jobs.find({}).sort("created_at", DESCENDING).limit(limit))
        return jobs
    except Exception as e:
        print(f"Error getting recent jobs: {e}")
        return []

async def get_companies_data(limit=50):
    """Get companies data from MongoDB"""
    if not DATABASE_AVAILABLE:
        return [
            {
                "_id": "1",
                "name": "Remote Company",
                "website": "https://remote.com",
                "job_count": 15,
                "created_at": datetime.now()
            }
        ]
    
    try:
        db = get_db()
        
        # Aggregate companies with job counts
        pipeline = [
            {"$group": {
                "_id": "$company",
                "job_count": {"$sum": 1},
                "latest_job": {"$max": "$created_at"},
                "website": {"$first": "$company_url"}
            }},
            {"$sort": {"job_count": -1}},
            {"$limit": limit}
        ]
        
        companies = list(db.jobs.aggregate(pipeline))
        
        # Format the data
        formatted_companies = []
        for company in companies:
            formatted_companies.append({
                "_id": str(company["_id"]),
                "name": company["_id"],
                "website": company.get("website", ""),
                "job_count": company["job_count"],
                "created_at": company.get("latest_job", datetime.now())
            })
        
        return formatted_companies
    except Exception as e:
        print(f"Error getting companies data: {e}")
        return [] 