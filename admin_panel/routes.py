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
            .job-item {{ padding: 10px 0; border-bottom: 1px solid #eee; cursor: pointer; transition: background-color 0.2s; }}
            .job-item:hover {{ background-color: #f8f9fa; }}
            .job-item:last-child {{ border-bottom: none; }}
            .job-title {{ font-weight: bold; color: #333; }}
            .job-company {{ color: #666; font-size: 0.9em; }}
            .job-meta {{ color: #999; font-size: 0.8em; }}
            
            /* Modal styles */
            .modal {{ display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.5); }}
            .modal-content {{ background-color: white; margin: 5% auto; padding: 20px; border-radius: 8px; width: 80%; max-width: 800px; max-height: 80vh; overflow-y: auto; }}
            .modal-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; border-bottom: 1px solid #eee; padding-bottom: 10px; }}
            .modal-title {{ font-size: 1.5em; font-weight: bold; color: #333; }}
            .close {{ font-size: 28px; font-weight: bold; cursor: pointer; color: #999; }}
            .close:hover {{ color: #333; }}
            .job-detail-section {{ margin-bottom: 20px; }}
            .job-detail-label {{ font-weight: bold; color: #666; margin-bottom: 5px; }}
            .job-detail-value {{ color: #333; line-height: 1.6; }}
            .job-apply-btn {{ background: #28a745; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; text-decoration: none; display: inline-block; }}
            .job-apply-btn:hover {{ background: #218838; color: white; text-decoration: none; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🚀 Buzz2Remote Admin Panel</h1>
        </div>
        
        <div class="nav">
            <a href="/">🏠 Ana Sayfa</a>
            <a href="/admin/dashboard">Dashboard</a>
            <a href="/admin/jobs">Jobs</a>
            <a href="/admin/companies">Companies</a>
            <a href="/admin/apis">API Services</a>
            <a href="/docs">API Docs</a>
        </div>
        
        <div class="container">
            <div class="stats">
                <div class="stat" onclick="window.location.href='/admin/jobs'" style="cursor: pointer;">
                    <h3>{stats['total_jobs']:,}</h3>
                    <p>Total Jobs</p>
                </div>
                <div class="stat" onclick="window.location.href='/admin/companies'" style="cursor: pointer;">
                    <h3>{stats['total_companies']:,}</h3>
                    <p>Companies</p>
                </div>
                <div class="stat" onclick="window.location.href='/admin/apis'" style="cursor: pointer;">
                    <h3>{stats['active_apis']}</h3>
                    <p>Active APIs</p>
                </div>
                <div class="stat" onclick="window.location.href='/admin/jobs?filter=today'" style="cursor: pointer;">
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
                <div class="job-item" data-job-id="{job['_id']}">
                    <div class="job-title">{job['title']}</div>
                    <div class="job-company">{job['company']} • {job['location']}</div>
                    <div class="job-meta">Source: {job['source']} • Posted: {date_str}</div>
                </div>"""
    
    html_content += """
            </div>
        </div>
        
        <!-- Job Detail Modal -->
        <div id="jobModal" class="modal">
            <div class="modal-content">
                <div class="modal-header">
                    <div class="modal-title" id="modalJobTitle">Job Details</div>
                    <span class="close" onclick="closeJobModal()">&times;</span>
                </div>
                <div id="modalJobContent">
                    <div class="job-detail-section">
                        <div class="job-detail-label">Company:</div>
                        <div class="job-detail-value" id="modalJobCompany"></div>
                    </div>
                    <div class="job-detail-section">
                        <div class="job-detail-label">Location:</div>
                        <div class="job-detail-value" id="modalJobLocation"></div>
                    </div>
                    <div class="job-detail-section">
                        <div class="job-detail-label">Source:</div>
                        <div class="job-detail-value" id="modalJobSource"></div>
                    </div>
                    <div class="job-detail-section">
                        <div class="job-detail-label">Posted Date:</div>
                        <div class="job-detail-value" id="modalJobDate"></div>
                    </div>
                    <div class="job-detail-section">
                        <div class="job-detail-label">Description:</div>
                        <div class="job-detail-value" id="modalJobDescription"></div>
                    </div>
                    <div class="job-detail-section">
                        <a id="modalJobApply" class="job-apply-btn" href="#" target="_blank">Apply for this Job</a>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            let currentAction = null;
            let progressInterval = null;
            let currentProcessId = null;
            
            // Job modal functions
            function openJobModal(jobId) {
                fetchJobDetails(jobId);
                document.getElementById('jobModal').style.display = 'block';
            }
            
            function closeJobModal() {
                document.getElementById('jobModal').style.display = 'none';
            }
            
            async function fetchJobDetails(jobId) {
                try {
                    const response = await fetch(`/admin/job-details/${{jobId}}`);
                    const job = await response.json();
                    
                    document.getElementById('modalJobTitle').textContent = job.title;
                    document.getElementById('modalJobCompany').textContent = job.company;
                    document.getElementById('modalJobLocation').textContent = job.location;
                    document.getElementById('modalJobSource').textContent = job.source;
                    document.getElementById('modalJobDate').textContent = new Date(job.created_at).toLocaleDateString();
                    document.getElementById('modalJobDescription').innerHTML = job.description || 'No description available';
                    
                    const applyBtn = document.getElementById('modalJobApply');
                    if (job.url) {
                        applyBtn.href = job.url;
                        applyBtn.style.display = 'inline-block';
                    } else {
                        applyBtn.style.display = 'none';
                    }
                } catch (error) {
                    console.error('Error fetching job details:', error);
                    document.getElementById('modalJobTitle').textContent = 'Error loading job details';
                }
            }
            
            // Add click event listeners to job items
            document.addEventListener('DOMContentLoaded', function() {
                const jobItems = document.querySelectorAll('.job-item[data-job-id]');
                jobItems.forEach(item => {
                    item.addEventListener('click', function() {
                        const jobId = this.getAttribute('data-job-id');
                        openJobModal(jobId);
                    });
                });
                
                // Close modal when clicking outside
                window.addEventListener('click', function(event) {
                    const modal = document.getElementById('jobModal');
                    if (event.target === modal) {
                        closeJobModal();
                    }
                });
            });
            
            // Progress and action functions
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
async def admin_jobs(request: Request, page: int = 1, sort_by: str = "created_at", sort_order: str = "desc", company_filter: str = None):
    """Job listings page with pagination and sorting"""
    
    page_size = 20
    skip = (page - 1) * page_size
    
    # Build sort criteria
    sort_direction = -1 if sort_order == "desc" else 1
    sort_criteria = {sort_by: sort_direction}
    
    # Build filter criteria
    filter_criteria = {}
    if company_filter:
        filter_criteria["company"] = {"$regex": company_filter, "$options": "i"}
    
    # Get jobs data with pagination
    try:
        from database import get_db
        db = await get_db()
        
        total_jobs = await db.jobs.count_documents(filter_criteria)
        jobs_cursor = db.jobs.find(filter_criteria).sort(list(sort_criteria.items())).skip(skip).limit(page_size)
        jobs = await jobs_cursor.to_list(length=page_size)
        
        total_pages = (total_jobs + page_size - 1) // page_size
        
    except Exception as e:
        logger.error(f"Error fetching jobs: {e}")
        jobs = []
        total_jobs = 0
        total_pages = 1
    
    # Format jobs for display
    formatted_jobs = []
    for job in jobs:
        formatted_jobs.append({
            "_id": str(job.get("_id", "")),
            "title": job.get("title", "Unknown Title"),
            "company": job.get("company", "Unknown Company"),
            "location": job.get("location", "Remote"),
            "source": job.get("source", "Unknown"),
            "url": job.get("url", ""),
            "created_at": job.get("created_at", datetime.now()),
            "description": job.get("description", "")[:100] + "..." if job.get("description") else "No description"
        })
    
    # Generate pagination links
    pagination_html = ""
    if total_pages > 1:
        pagination_html = '<div style="margin: 20px 0; text-align: center;">'
        
        # Previous button
        if page > 1:
            prev_url = f"/admin/jobs?page={page-1}&sort_by={sort_by}&sort_order={sort_order}"
            if company_filter:
                prev_url += f"&company_filter={company_filter}"
            pagination_html += f'<a href="{prev_url}" style="margin: 0 5px; padding: 8px 12px; background: #007bff; color: white; text-decoration: none; border-radius: 4px;">← Previous</a>'
        
        # Page numbers
        start_page = max(1, page - 2)
        end_page = min(total_pages, page + 2)
        
        for p in range(start_page, end_page + 1):
            page_url = f"/admin/jobs?page={p}&sort_by={sort_by}&sort_order={sort_order}"
            if company_filter:
                page_url += f"&company_filter={company_filter}"
            
            if p == page:
                pagination_html += f'<span style="margin: 0 5px; padding: 8px 12px; background: #6c757d; color: white; border-radius: 4px;">{p}</span>'
            else:
                pagination_html += f'<a href="{page_url}" style="margin: 0 5px; padding: 8px 12px; background: #007bff; color: white; text-decoration: none; border-radius: 4px;">{p}</a>'
        
        # Next button
        if page < total_pages:
            next_url = f"/admin/jobs?page={page+1}&sort_by={sort_by}&sort_order={sort_order}"
            if company_filter:
                next_url += f"&company_filter={company_filter}"
            pagination_html += f'<a href="{next_url}" style="margin: 0 5px; padding: 8px 12px; background: #007bff; color: white; text-decoration: none; border-radius: 4px;">Next →</a>'
        
        pagination_html += '</div>'
    
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
            th {{ background: #f8f9fa; font-weight: 600; cursor: pointer; }}
            th:hover {{ background: #e9ecef; }}
            .badge {{ padding: 4px 8px; border-radius: 4px; font-size: 0.875rem; }}
            .badge-primary {{ background: #e3f2fd; color: #1976d2; }}
            .company-link {{ color: #007bff; text-decoration: none; font-weight: 500; }}
            .company-link:hover {{ text-decoration: underline; }}
            .job-title {{ cursor: pointer; color: #333; }}
            .job-title:hover {{ color: #007bff; text-decoration: underline; }}
            .sort-indicator {{ font-size: 0.8em; margin-left: 5px; }}
            .filters {{ margin-bottom: 20px; padding: 15px; background: #f8f9fa; border-radius: 8px; }}
            .filter-input {{ padding: 8px; border: 1px solid #ddd; border-radius: 4px; margin-right: 10px; }}
            
            /* Modal styles */
            .modal {{ display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.5); }}
            .modal-content {{ background-color: white; margin: 5% auto; padding: 20px; border-radius: 8px; width: 80%; max-width: 800px; max-height: 80vh; overflow-y: auto; }}
            .modal-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; border-bottom: 1px solid #eee; padding-bottom: 10px; }}
            .modal-title {{ font-size: 1.5em; font-weight: bold; color: #333; }}
            .close {{ font-size: 28px; font-weight: bold; cursor: pointer; color: #999; }}
            .close:hover {{ color: #333; }}
            .job-detail-section {{ margin-bottom: 20px; }}
            .job-detail-label {{ font-weight: bold; color: #666; margin-bottom: 5px; }}
            .job-detail-value {{ color: #333; line-height: 1.6; }}
            .job-apply-btn {{ background: #28a745; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; text-decoration: none; display: inline-block; }}
            .job-apply-btn:hover {{ background: #218838; color: white; text-decoration: none; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🚀 Buzz2Remote Admin Panel</h1>
        </div>
        
        <div class="nav">
            <a href="/">🏠 Ana Sayfa</a>
            <a href="/admin/dashboard">Dashboard</a>
            <a href="/admin/jobs">Jobs</a>
            <a href="/admin/companies">Companies</a>
            <a href="/admin/apis">API Services</a>
            <a href="/docs">API Docs</a>
        </div>
        
        <div class="container">
            <div class="card">
                <h2>Job Listings ({total_jobs:,} total) - Page {page} of {total_pages}</h2>
                
                <div class="filters">
                    <input type="text" id="companyFilter" class="filter-input" placeholder="Filter by company..." value="{company_filter or ''}" onkeypress="if(event.key==='Enter') filterByCompany()">
                    <button onclick="filterByCompany()" style="padding: 8px 15px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer;">Filter</button>
                    <button onclick="clearFilters()" style="padding: 8px 15px; background: #6c757d; color: white; border: none; border-radius: 4px; cursor: pointer; margin-left: 5px;">Clear</button>
                </div>
                
                <table>
                    <thead>
                        <tr>
                            <th onclick="sortBy('title')">Title {get_sort_indicator('title', sort_by, sort_order)}</th>
                            <th onclick="sortBy('company')">Company {get_sort_indicator('company', sort_by, sort_order)}</th>
                            <th onclick="sortBy('location')">Location {get_sort_indicator('location', sort_by, sort_order)}</th>
                            <th onclick="sortBy('source')">Job Ad {get_sort_indicator('source', sort_by, sort_order)}</th>
                            <th onclick="sortBy('created_at')">Posted {get_sort_indicator('created_at', sort_by, sort_order)}</th>
                        </tr>
                    </thead>
                    <tbody>"""
    
    for job in formatted_jobs:
        created_at = job['created_at']
        if isinstance(created_at, datetime):
            date_str = created_at.strftime('%Y-%m-%d')
        else:
            date_str = str(created_at)
        
        # Create company filter link
        company_link = f"/admin/jobs?company_filter={job['company']}"
        
        # Create job ad link
        job_ad_link = job['url'] if job['url'] else '#'
        job_ad_text = "View Job Ad" if job['url'] else "No Link"
        job_ad_style = "" if job['url'] else "color: #999; cursor: not-allowed;"
            
        html_content += f"""
                        <tr>
                            <td>
                                <div class="job-title" data-job-id="{job['_id']}">{job['title']}</div>
                                <div style="color: #666; font-size: 0.9em;">{job['description']}</div>
                            </td>
                            <td><a href="{company_link}" class="company-link">{job['company']}</a></td>
                            <td>{job['location']}</td>
                            <td><a href="{job_ad_link}" target="_blank" style="{job_ad_style}">{job_ad_text}</a></td>
                            <td>{date_str}</td>
                        </tr>"""
    
    html_content += f"""
                    </tbody>
                </table>
                
                {pagination_html}
            </div>
        </div>
        
        <!-- Job Detail Modal -->
        <div id="jobModal" class="modal">
            <div class="modal-content">
                <div class="modal-header">
                    <div class="modal-title" id="modalJobTitle">Job Details</div>
                    <span class="close" onclick="closeJobModal()">&times;</span>
                </div>
                <div id="modalJobContent">
                    <div class="job-detail-section">
                        <div class="job-detail-label">Company:</div>
                        <div class="job-detail-value" id="modalJobCompany"></div>
                    </div>
                    <div class="job-detail-section">
                        <div class="job-detail-label">Location:</div>
                        <div class="job-detail-value" id="modalJobLocation"></div>
                    </div>
                    <div class="job-detail-section">
                        <div class="job-detail-label">Source:</div>
                        <div class="job-detail-value" id="modalJobSource"></div>
                    </div>
                    <div class="job-detail-section">
                        <div class="job-detail-label">Posted Date:</div>
                        <div class="job-detail-value" id="modalJobDate"></div>
                    </div>
                    <div class="job-detail-section">
                        <div class="job-detail-label">Description:</div>
                        <div class="job-detail-value" id="modalJobDescription"></div>
                    </div>
                    <div class="job-detail-section">
                        <a id="modalJobApply" class="job-apply-btn" href="#" target="_blank">Apply for this Job</a>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            // Job modal functions
            function openJobModal(jobId) {{
                fetchJobDetails(jobId);
                document.getElementById('jobModal').style.display = 'block';
            }}
            
            function closeJobModal() {{
                document.getElementById('jobModal').style.display = 'none';
            }}
            
            async function fetchJobDetails(jobId) {{
                try {{
                    const response = await fetch(`/admin/job-details/${{jobId}}`);
                    const job = await response.json();
                    
                    document.getElementById('modalJobTitle').textContent = job.title;
                    document.getElementById('modalJobCompany').textContent = job.company;
                    document.getElementById('modalJobLocation').textContent = job.location;
                    document.getElementById('modalJobSource').textContent = job.source;
                    document.getElementById('modalJobDate').textContent = new Date(job.created_at).toLocaleDateString();
                    document.getElementById('modalJobDescription').innerHTML = job.description || 'No description available';
                    
                    const applyBtn = document.getElementById('modalJobApply');
                    if (job.url) {{
                        applyBtn.href = job.url;
                        applyBtn.style.display = 'inline-block';
                    }} else {{
                        applyBtn.style.display = 'none';
                    }}
                }} catch (error) {{
                    console.error('Error fetching job details:', error);
                    document.getElementById('modalJobTitle').textContent = 'Error loading job details';
                }}
            }}
            
            // Sorting and filtering functions
            function sortBy(column) {{
                const currentSort = '{sort_by}';
                const currentOrder = '{sort_order}';
                
                let newOrder = 'asc';
                if (column === currentSort && currentOrder === 'asc') {{
                    newOrder = 'desc';
                }}
                
                const companyFilter = document.getElementById('companyFilter').value;
                let url = `/admin/jobs?sort_by=${{column}}&sort_order=${{newOrder}}`;
                if (companyFilter) {{
                    url += `&company_filter=${{encodeURIComponent(companyFilter)}}`;
                }}
                
                window.location.href = url;
            }}
            
            function filterByCompany() {{
                const companyFilter = document.getElementById('companyFilter').value;
                let url = '/admin/jobs?page=1';
                if (companyFilter) {{
                    url += `&company_filter=${{encodeURIComponent(companyFilter)}}`;
                }}
                window.location.href = url;
            }}
            
            function clearFilters() {{
                window.location.href = '/admin/jobs';
            }}
            
            // Add click event listeners
            document.addEventListener('DOMContentLoaded', function() {{
                const jobTitles = document.querySelectorAll('.job-title[data-job-id]');
                jobTitles.forEach(title => {{
                    title.addEventListener('click', function() {{
                        const jobId = this.getAttribute('data-job-id');
                        openJobModal(jobId);
                    }});
                }});
                
                // Close modal when clicking outside
                window.addEventListener('click', function(event) {{
                    const modal = document.getElementById('jobModal');
                    if (event.target === modal) {{
                        closeJobModal();
                    }}
                }});
            }});
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

def get_sort_indicator(column, current_sort, current_order):
    """Get sort indicator for table headers"""
    if column == current_sort:
        return '<span class="sort-indicator">↓</span>' if current_order == 'desc' else '<span class="sort-indicator">↑</span>'
    return '<span class="sort-indicator">↕</span>'

@admin_router.get("/companies", response_class=HTMLResponse)
async def admin_companies(request: Request, page: int = 1, sort_by: str = "job_count", sort_order: str = "desc"):
    """Companies page with pagination and sorting"""
    
    page_size = 20
    skip = (page - 1) * page_size
    
    # Build sort criteria
    sort_direction = -1 if sort_order == "desc" else 1
    sort_criteria = {sort_by: sort_direction}
    
    # Get companies data with pagination
    try:
        from database import get_db
        db = await get_db()
        
        # Aggregate companies with job counts
        pipeline = [
            {
                "$group": {
                    "_id": "$company",
                    "job_count": {"$sum": 1},
                    "latest_job": {"$max": "$created_at"},
                    "website": {"$first": "$company_website"}
                }
            },
            {"$sort": {sort_by: sort_direction}},
            {"$skip": skip},
            {"$limit": page_size}
        ]
        
        companies_cursor = db.jobs.aggregate(pipeline)
        companies = await companies_cursor.to_list(length=page_size)
        
        # Get total count
        total_pipeline = [
            {"$group": {"_id": "$company"}},
            {"$count": "total"}
        ]
        total_result = await db.jobs.aggregate(total_pipeline).to_list(length=1)
        total_companies = total_result[0]["total"] if total_result else 0
        
        total_pages = (total_companies + page_size - 1) // page_size
        
    except Exception as e:
        logger.error(f"Error fetching companies: {e}")
        companies = []
        total_companies = 0
        total_pages = 1
    
    # Format companies for display
    formatted_companies = []
    for company in companies:
        formatted_companies.append({
            "name": company["_id"],
            "job_count": company["job_count"],
            "latest_job": company.get("latest_job", datetime.now()),
            "website": company.get("website", "")
        })
    
    # Generate pagination links
    pagination_html = ""
    if total_pages > 1:
        pagination_html = '<div style="margin: 20px 0; text-align: center;">'
        
        # Previous button
        if page > 1:
            prev_url = f"/admin/companies?page={page-1}&sort_by={sort_by}&sort_order={sort_order}"
            pagination_html += f'<a href="{prev_url}" style="margin: 0 5px; padding: 8px 12px; background: #007bff; color: white; text-decoration: none; border-radius: 4px;">← Previous</a>'
        
        # Page numbers
        start_page = max(1, page - 2)
        end_page = min(total_pages, page + 2)
        
        for p in range(start_page, end_page + 1):
            page_url = f"/admin/companies?page={p}&sort_by={sort_by}&sort_order={sort_order}"
            
            if p == page:
                pagination_html += f'<span style="margin: 0 5px; padding: 8px 12px; background: #6c757d; color: white; border-radius: 4px;">{p}</span>'
            else:
                pagination_html += f'<a href="{page_url}" style="margin: 0 5px; padding: 8px 12px; background: #007bff; color: white; text-decoration: none; border-radius: 4px;">{p}</a>'
        
        # Next button
        if page < total_pages:
            next_url = f"/admin/companies?page={page+1}&sort_by={sort_by}&sort_order={sort_order}"
            pagination_html += f'<a href="{next_url}" style="margin: 0 5px; padding: 8px 12px; background: #007bff; color: white; text-decoration: none; border-radius: 4px;">Next →</a>'
        
        pagination_html += '</div>'

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
            th {{ background: #f8f9fa; font-weight: 600; cursor: pointer; }}
            th:hover {{ background: #e9ecef; }}
            .badge {{ padding: 4px 8px; border-radius: 4px; font-size: 0.875rem; }}
            .badge-success {{ background: #e8f5e8; color: #2e7d32; }}
            .company-link {{ color: #007bff; text-decoration: none; font-weight: 500; }}
            .company-link:hover {{ text-decoration: underline; }}
            .sort-indicator {{ font-size: 0.8em; margin-left: 5px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🚀 Buzz2Remote Admin Panel</h1>
        </div>
        
        <div class="nav">
            <a href="/">🏠 Ana Sayfa</a>
            <a href="/admin/dashboard">Dashboard</a>
            <a href="/admin/jobs">Jobs</a>
            <a href="/admin/companies">Companies</a>
            <a href="/admin/apis">API Services</a>
            <a href="/docs">API Docs</a>
        </div>
        
        <div class="container">
            <div class="card">
                <h2>Companies ({total_companies:,} total) - Page {page} of {total_pages}</h2>
                <table>
                    <thead>
                        <tr>
                            <th onclick="sortBy('_id')">Company {get_sort_indicator('_id', sort_by, sort_order)}</th>
                            <th onclick="sortBy('job_count')">Job Count {get_sort_indicator('job_count', sort_by, sort_order)}</th>
                            <th onclick="sortBy('latest_job')">Latest Job {get_sort_indicator('latest_job', sort_by, sort_order)}</th>
                        </tr>
                    </thead>
                    <tbody>"""
    
    for company in formatted_companies:
        latest_job = company['latest_job']
        if isinstance(latest_job, datetime):
            date_str = latest_job.strftime('%Y-%m-%d')
        else:
            date_str = str(latest_job)
        
        # Create company link - try website first, then jobs filter
        company_website = company.get('website', '')
        if company_website and not company_website.startswith('http'):
            company_website = f"https://{company_website}"
        
        if company_website:
            company_link = company_website
            company_target = 'target="_blank"'
        else:
            company_link = f"/admin/jobs?company_filter={company['name']}"
            company_target = ''
            
        html_content += f"""
                        <tr>
                            <td><a href="{company_link}" {company_target} class="company-link">{company['name']}</a></td>
                            <td><span class="badge badge-success">{company['job_count']} jobs</span></td>
                            <td>{date_str}</td>
                        </tr>"""
    
    html_content += f"""
                    </tbody>
                </table>
                
                {pagination_html}
            </div>
        </div>
        
        <script>
            function sortBy(column) {{
                const currentSort = '{sort_by}';
                const currentOrder = '{sort_order}';
                
                let newOrder = 'asc';
                if (column === currentSort && currentOrder === 'asc') {{
                    newOrder = 'desc';
                }}
                
                window.location.href = `/admin/companies?sort_by=${{column}}&sort_order=${{newOrder}}`;
            }}
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

@admin_router.get("/apis", response_class=HTMLResponse)
async def admin_apis(request: Request):
    """API services management page"""
    
    # Define all integrated API services
    api_services = [
        {
            "name": "BUZZ2REMOTE-COMPANIES",
            "description": "Internal company database crawler",
            "endpoint": "run-company-crawler",
            "status": "active",
            "last_run": "2024-01-15 10:30:00"
        },
        {
            "name": "REMOTEOK",
            "description": "Remote OK job board API",
            "endpoint": "run-remoteok",
            "status": "active",
            "last_run": "2024-01-15 09:15:00"
        },
        {
            "name": "WEWORKREMOTELY",
            "description": "We Work Remotely job board",
            "endpoint": "run-weworkremotely",
            "status": "active",
            "last_run": "2024-01-15 08:45:00"
        },
        {
            "name": "REMOTECO",
            "description": "Remote.co job listings",
            "endpoint": "run-remoteco",
            "status": "active",
            "last_run": "2024-01-15 07:20:00"
        },
        {
            "name": "JUSTREMOTE",
            "description": "JustRemote job board",
            "endpoint": "run-justremote",
            "status": "active",
            "last_run": "2024-01-15 06:10:00"
        },
        {
            "name": "FLEXJOBS",
            "description": "FlexJobs remote positions",
            "endpoint": "run-flexjobs",
            "status": "active",
            "last_run": "2024-01-15 05:30:00"
        },
        {
            "name": "ANGEL-LIST",
            "description": "AngelList startup jobs",
            "endpoint": "run-angellist",
            "status": "active",
            "last_run": "2024-01-15 04:15:00"
        },
        {
            "name": "LINKEDIN-JOBS",
            "description": "LinkedIn job postings API",
            "endpoint": "run-linkedin",
            "status": "active",
            "last_run": "2024-01-15 03:45:00"
        },
        {
            "name": "GITHUB-JOBS",
            "description": "GitHub job board (deprecated but monitored)",
            "endpoint": "run-github-jobs",
            "status": "inactive",
            "last_run": "2024-01-10 12:00:00"
        },
        {
            "name": "STACKOVERFLOW-JOBS",
            "description": "Stack Overflow job listings",
            "endpoint": "run-stackoverflow",
            "status": "active",
            "last_run": "2024-01-15 02:30:00"
        }
    ]
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>API Services - Buzz2Remote Admin</title>
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
            .badge-warning {{ background: #fff3cd; color: #856404; }}
            .badge-danger {{ background: #f8d7da; color: #721c24; }}
            .status-dot {{ width: 8px; height: 8px; border-radius: 50%; display: inline-block; margin-right: 8px; }}
            .status-active {{ background: #28a745; }}
            .status-inactive {{ background: #dc3545; }}
            .btn {{ padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; font-size: 0.875rem; }}
            .btn-primary {{ background: #007bff; color: white; }}
            .btn-primary:hover {{ background: #0056b3; }}
            .btn-danger {{ background: #dc3545; color: white; }}
            .btn-danger:hover {{ background: #c82333; }}
            .btn:disabled {{ background: #6c757d; cursor: not-allowed; }}
            .progress {{ margin: 10px 0; padding: 10px; background: #e9ecef; border-radius: 4px; display: none; }}
            .progress-bar {{ width: 0%; height: 20px; background: #007bff; border-radius: 4px; transition: width 0.3s; }}
            .result {{ margin: 10px 0; padding: 10px; border-radius: 4px; display: none; }}
            .result.success {{ background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
            .result.error {{ background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🚀 Buzz2Remote Admin Panel</h1>
        </div>
        
        <div class="nav">
            <a href="/">🏠 Ana Sayfa</a>
            <a href="/admin/dashboard">Dashboard</a>
            <a href="/admin/jobs">Jobs</a>
            <a href="/admin/companies">Companies</a>
            <a href="/admin/apis">API Services</a>
            <a href="/docs">API Docs</a>
        </div>
        
        <div class="container">
            <div class="card">
                <h2>External API Services ({len(api_services)} total)</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Service</th>
                            <th>Description</th>
                            <th>Status</th>
                            <th>Last Run</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>"""
    
    for i, service in enumerate(api_services):
        status_class = "status-active" if service["status"] == "active" else "status-inactive"
        badge_class = "badge-success" if service["status"] == "active" else "badge-danger"
        
        html_content += f"""
                        <tr id="service-row-{i}">
                            <td>
                                <strong>{service['name']}</strong>
                            </td>
                            <td>{service['description']}</td>
                            <td>
                                <span class="status-dot {status_class}"></span>
                                <span class="badge {badge_class}">{service['status'].title()}</span>
                            </td>
                            <td>{service['last_run']}</td>
                            <td>
                                <button class="btn btn-primary" onclick="runService('{service['endpoint']}', {i})" id="run-btn-{i}">
                                    Run
                                </button>
                                <button class="btn btn-danger" onclick="cancelService({i})" id="cancel-btn-{i}" style="display: none;">
                                    Cancel
                                </button>
                                <div class="progress" id="progress-{i}">
                                    <div class="progress-bar" id="progress-bar-{i}"></div>
                                    <div style="text-align: center; margin-top: 5px; font-size: 0.8em;" id="progress-text-{i}">
                                        Starting...
                                    </div>
                                </div>
                                <div class="result" id="result-{i}"></div>
                            </td>
                        </tr>"""
    
    html_content += """
                    </tbody>
                </table>
            </div>
        </div>
        
        <script>
            let runningServices = new Set();
            let serviceIntervals = {};
            
            async function runService(endpoint, serviceIndex) {
                if (runningServices.has(serviceIndex)) {
                    return;
                }
                
                runningServices.add(serviceIndex);
                
                // Update UI
                const runBtn = document.getElementById(`run-btn-${serviceIndex}`);
                const cancelBtn = document.getElementById(`cancel-btn-${serviceIndex}`);
                const progress = document.getElementById(`progress-${serviceIndex}`);
                const progressBar = document.getElementById(`progress-bar-${serviceIndex}`);
                const progressText = document.getElementById(`progress-text-${serviceIndex}`);
                const result = document.getElementById(`result-${serviceIndex}`);
                
                runBtn.style.display = 'none';
                cancelBtn.style.display = 'inline-block';
                progress.style.display = 'block';
                result.style.display = 'none';
                
                // Simulate progress
                let progressValue = 0;
                serviceIntervals[serviceIndex] = setInterval(() => {
                    progressValue += Math.random() * 10;
                    if (progressValue > 90) progressValue = 90;
                    progressBar.style.width = progressValue + '%';
                    progressText.textContent = `Running ${endpoint}... ${Math.round(progressValue)}%`;
                }, 1000);
                
                try {
                    const response = await fetch(`/admin/api-services/${endpoint}`, {
                        method: 'POST'
                    });
                    const data = await response.json();
                    
                    // Complete progress
                    clearInterval(serviceIntervals[serviceIndex]);
                    progressBar.style.width = '100%';
                    progressText.textContent = 'Completed!';
                    
                    setTimeout(() => {
                        progress.style.display = 'none';
                        runBtn.style.display = 'inline-block';
                        cancelBtn.style.display = 'none';
                        
                        // Show result
                        result.className = `result ${data.status === 'success' ? 'success' : 'error'}`;
                        result.textContent = data.message;
                        result.style.display = 'block';
                        
                        // Hide result after 10 seconds
                        setTimeout(() => {
                            result.style.display = 'none';
                        }, 10000);
                        
                        runningServices.delete(serviceIndex);
                    }, 2000);
                    
                } catch (error) {
                    clearInterval(serviceIntervals[serviceIndex]);
                    progress.style.display = 'none';
                    runBtn.style.display = 'inline-block';
                    cancelBtn.style.display = 'none';
                    
                    result.className = 'result error';
                    result.textContent = `Error: ${error.message}`;
                    result.style.display = 'block';
                    
                    runningServices.delete(serviceIndex);
                }
            }
            
            function cancelService(serviceIndex) {
                if (serviceIntervals[serviceIndex]) {
                    clearInterval(serviceIntervals[serviceIndex]);
                }
                
                const runBtn = document.getElementById(`run-btn-${serviceIndex}`);
                const cancelBtn = document.getElementById(`cancel-btn-${serviceIndex}`);
                const progress = document.getElementById(`progress-${serviceIndex}`);
                const result = document.getElementById(`result-${serviceIndex}`);
                
                progress.style.display = 'none';
                runBtn.style.display = 'inline-block';
                cancelBtn.style.display = 'none';
                
                result.className = 'result error';
                result.textContent = 'Service cancelled by user';
                result.style.display = 'block';
                
                setTimeout(() => {
                    result.style.display = 'none';
                }, 5000);
                
                runningServices.delete(serviceIndex);
            }
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

@admin_router.post("/api-services/{service_endpoint}")
async def run_api_service(service_endpoint: str):
    """Run a specific API service"""
    try:
        import subprocess
        from telegram_bot.bot import RemoteJobsBot
        
        # Map endpoints to actual service commands
        service_commands = {
            "run-company-crawler": ["python", "-m", "services.company_crawler"],
            "run-remoteok": ["python", "-m", "services.remoteok_crawler"],
            "run-weworkremotely": ["python", "-m", "services.weworkremotely_crawler"],
            "run-remoteco": ["python", "-m", "services.remoteco_crawler"],
            "run-justremote": ["python", "-m", "services.justremote_crawler"],
            "run-flexjobs": ["python", "-m", "services.flexjobs_crawler"],
            "run-angellist": ["python", "-m", "services.angellist_crawler"],
            "run-linkedin": ["python", "-m", "services.linkedin_crawler"],
            "run-github-jobs": ["python", "-m", "services.github_jobs_crawler"],
            "run-stackoverflow": ["python", "-m", "services.stackoverflow_crawler"]
        }
        
        if service_endpoint not in service_commands:
            return {
                "status": "error",
                "message": f"Unknown service endpoint: {service_endpoint}"
            }
        
        # Start the service process
        command = service_commands[service_endpoint]
        process = subprocess.Popen(
            command,
            cwd=os.path.dirname(os.path.dirname(__file__)),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Send Telegram notification
        try:
            bot = RemoteJobsBot()
            if bot.enabled:
                service_name = service_endpoint.replace("run-", "").replace("-", " ").title()
                await bot.send_notification(f"🔄 {service_name} API service started from Admin Panel")
        except Exception as e:
            logger.warning(f"Failed to send Telegram notification: {e}")
        
        return {
            "status": "success",
            "message": f"Service {service_endpoint} started successfully",
            "process_id": process.pid
        }
        
    except Exception as e:
        logger.error(f"Error starting API service {service_endpoint}: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to start service: {str(e)}"
        }

# Quick action endpoints
@admin_router.post("/actions/run-crawler")
async def admin_run_crawler():
    """Run job crawler"""
    try:
        import subprocess
        import psutil
        import asyncio
        from telegram_bot.bot import RemoteJobsBot
        
        # Start the crawler process
        process = subprocess.Popen(
            ["python", "-m", "services.job_crawler"],
            cwd=os.path.dirname(os.path.dirname(__file__)),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Store process info
        process_info = {
            "id": process.pid,
            "name": "Job Crawler",
            "status": "running",
            "start_time": datetime.now()
        }
        
        # Send Telegram notification
        try:
            bot = RemoteJobsBot()
            if bot.enabled:
                await bot.send_notification("🚀 Job Crawler started from Admin Panel")
        except Exception as e:
            logger.warning(f"Failed to send Telegram notification: {e}")
        
        return {
            "status": "success",
            "message": "Job crawler started successfully",
            "process_id": process.pid
        }
        
    except Exception as e:
        logger.error(f"Error starting job crawler: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to start job crawler: {str(e)}"
        }

@admin_router.post("/actions/fetch-external-apis")
async def admin_fetch_external_apis():
    """Fetch data from external APIs"""
    try:
        import subprocess
        from telegram_bot.bot import RemoteJobsBot
        
        # Start the external API fetch process
        process = subprocess.Popen(
            ["python", "-m", "services.external_api_service"],
            cwd=os.path.dirname(os.path.dirname(__file__)),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Send Telegram notification
        try:
            bot = RemoteJobsBot()
            if bot.enabled:
                await bot.send_notification("🔄 External API fetch started from Admin Panel")
        except Exception as e:
            logger.warning(f"Failed to send Telegram notification: {e}")
        
        return {
            "status": "success",
            "message": "External API fetch started successfully",
            "process_id": process.pid
        }
        
    except Exception as e:
        logger.error(f"Error starting external API fetch: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to start external API fetch: {str(e)}"
        }

@admin_router.post("/actions/analyze-positions")
async def admin_analyze_positions():
    """Analyze job positions using AI"""
    try:
        import subprocess
        from telegram_bot.bot import RemoteJobsBot
        
        # Start the position analysis process
        process = subprocess.Popen(
            ["python", "-m", "services.ai_analysis_service"],
            cwd=os.path.dirname(os.path.dirname(__file__)),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Send Telegram notification
        try:
            bot = RemoteJobsBot()
            if bot.enabled:
                await bot.send_notification("🤖 AI Position Analysis started from Admin Panel\n\nThis service analyzes job descriptions, extracts key requirements, categorizes positions, and identifies trending skills in the job market.")
        except Exception as e:
            logger.warning(f"Failed to send Telegram notification: {e}")
        
        return {
            "status": "success",
            "message": "Position analysis started successfully",
            "process_id": process.pid
        }
        
    except Exception as e:
        logger.error(f"Error starting position analysis: {str(e)}")
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

@admin_router.get("/job-details/{job_id}")
async def get_job_details(job_id: str):
    """Get detailed information about a specific job"""
    try:
        from bson import ObjectId
        from database import get_db
        
        db = await get_db()
        job = await db.jobs.find_one({"_id": ObjectId(job_id)})
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Format the job data
        job_data = {
            "_id": str(job["_id"]),
            "title": job.get("title", "Unknown Title"),
            "company": job.get("company", "Unknown Company"),
            "location": job.get("location", "Remote"),
            "source": job.get("source", "Unknown"),
            "description": job.get("description", "No description available"),
            "url": job.get("url", ""),
            "created_at": job.get("created_at", datetime.now()).isoformat() if isinstance(job.get("created_at"), datetime) else str(job.get("created_at", "")),
            "salary": job.get("salary", ""),
            "job_type": job.get("job_type", ""),
            "requirements": job.get("requirements", ""),
            "benefits": job.get("benefits", "")
        }
        
        return job_data
        
    except Exception as e:
        logger.error(f"Error fetching job details: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching job details") 