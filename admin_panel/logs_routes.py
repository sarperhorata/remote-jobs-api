from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from datetime import datetime
from typing import Optional
import os
import sys
import logging
import subprocess

# Setup logging
logger = logging.getLogger(__name__)

# Add backend to path for database access
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend"))

try:
    from database import get_db
    db = get_db()
    DATABASE_AVAILABLE = True
    logger.info("Database connection successful for logs")
except ImportError as e:
    DATABASE_AVAILABLE = False
    db = None
    logger.warning(f"Database not available: {e}")

# Router
logs_router = APIRouter(prefix="/admin", tags=["admin-logs"])

@logs_router.get("/logs", response_class=HTMLResponse)
async def admin_logs(request: Request, page: int = 1, log_type: str = "all"):
    """Processing logs page"""
    
    # Get logs data
    logs_data = await get_processing_logs(page, log_type)
    error_summary = await get_error_summary()
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Processing Logs - Buzz2Remote Admin</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; background: #f8f9fa; }}
            .header {{ background: #343a40; color: white; padding: 1rem 2rem; }}
            .nav {{ background: white; padding: 1rem 2rem; border-bottom: 1px solid #dee2e6; }}
            .nav a {{ margin-right: 20px; text-decoration: none; color: #007bff; }}
            .nav a:hover {{ text-decoration: underline; }}
            .container {{ padding: 2rem; }}
            .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }}
            .summary-card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .summary-card h3 {{ margin: 0 0 10px 0; color: #333; }}
            .summary-card .number {{ font-size: 2rem; font-weight: bold; margin: 10px 0; }}
            .success {{ color: #28a745; }}
            .warning {{ color: #ffc107; }}
            .error {{ color: #dc3545; }}
            .info {{ color: #17a2b8; }}
            .filters {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; }}
            .filters select, .filters button {{ padding: 8px 15px; margin: 5px; border: 1px solid #ddd; border-radius: 4px; }}
            .logs-table {{ background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); overflow: hidden; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #eee; }}
            th {{ background: #f8f9fa; font-weight: 600; color: #333; }}
            tr:hover {{ background-color: #f8f9fa; }}
            .log-timestamp {{ color: #666; font-size: 0.9em; }}
            .log-type {{ padding: 4px 8px; border-radius: 4px; font-size: 0.8em; font-weight: bold; }}
            .log-type.enrichment {{ background: #e7f3ff; color: #0066cc; }}
            .log-type.crawler {{ background: #fff3e0; color: #e65100; }}
            .success-rate {{ padding: 4px 8px; border-radius: 4px; font-weight: bold; }}
            .rate-high {{ background: #d4edda; color: #155724; }}
            .rate-medium {{ background: #fff3cd; color: #856404; }}
            .rate-low {{ background: #f8d7da; color: #721c24; }}
            .view-btn {{ color: #007bff; text-decoration: none; padding: 4px 8px; border: 1px solid #007bff; border-radius: 4px; font-size: 0.8em; }}
            .view-btn:hover {{ background: #007bff; color: white; text-decoration: none; }}
            .pagination {{ text-align: center; margin: 20px 0; }}
            .pagination a {{ margin: 0 5px; padding: 8px 12px; text-decoration: none; color: #007bff; border: 1px solid #ddd; border-radius: 4px; }}
            .pagination a:hover {{ background: #f8f9fa; }}
            .pagination .current {{ background: #007bff; color: white; }}
            .btn {{ background: #007bff; color: white; padding: 8px 15px; border: none; border-radius: 4px; cursor: pointer; text-decoration: none; }}
            .btn:hover {{ background: #0056b3; }}
            .btn-danger {{ background: #dc3545; }}
            .btn-danger:hover {{ background: #c82333; }}
            .btn-success {{ background: #28a745; }}
            .btn-success:hover {{ background: #218838; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📊 Processing Logs</h1>
        </div>
        
        <div class="nav">
            <a href="http://localhost:3000">🏠 Ana Sayfa</a>
            <a href="/admin/dashboard">Dashboard</a>
            <a href="/admin/jobs">Jobs</a>
            <a href="/admin/companies">Companies</a>
            <a href="/admin/logs">Logs</a>
            <a href="/admin/apis">API Services</a>
            <a href="/docs">API Docs</a>
        </div>
        
        <div class="container">
            <div class="summary">
                <div class="summary-card">
                    <h3>Recent Runs</h3>
                    <div class="number info">{error_summary.get('total_runs', 0)}</div>
                    <p>Total processing runs</p>
                </div>
                <div class="summary-card">
                    <h3>Success Rate</h3>
                    <div class="number {'success' if error_summary.get('avg_success_rate', 0) > 80 else 'warning' if error_summary.get('avg_success_rate', 0) > 50 else 'error'}">{error_summary.get('avg_success_rate', 0):.1f}%</div>
                    <p>Average success rate</p>
                </div>
                <div class="summary-card">
                    <h3>Total Errors</h3>
                    <div class="number error">{error_summary.get('total_errors', 0)}</div>
                    <p>Across all runs</p>
                </div>
                <div class="summary-card">
                    <h3>Last Run</h3>
                    <div class="number info">{error_summary.get('last_run', 'Never')}</div>
                    <p>Most recent processing</p>
                </div>
            </div>
            
            <div class="filters">
                <select onchange="filterLogs(this.value)">
                    <option value="all" {'selected' if log_type == 'all' else ''}>All Logs</option>
                    <option value="company_website_enrichment" {'selected' if log_type == 'company_website_enrichment' else ''}>Company Enrichment</option>
                    <option value="job_crawler" {'selected' if log_type == 'job_crawler' else ''}>Job Crawler</option>
                    <option value="api_fetch" {'selected' if log_type == 'api_fetch' else ''}>API Fetch</option>
                </select>
                <button onclick="refreshLogs()" class="btn">🔄 Refresh</button>
                <button onclick="window.location.href='/admin/logs/errors'" class="btn btn-danger">❌ View Detailed Errors</button>
                <button onclick="runCompanyEnrichment()" class="btn btn-success">🚀 Run Company Enrichment</button>
            </div>
            
            <div class="logs-table">
                <table>
                    <thead>
                        <tr>
                            <th>Timestamp</th>
                            <th>Type</th>
                            <th>Success Rate</th>
                            <th>Total Processed</th>
                            <th>Errors</th>
                            <th>Duration</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>"""
    
    for log in logs_data.get('logs', []):
        timestamp = log.get('timestamp', datetime.now())
        if isinstance(timestamp, datetime):
            timestamp_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        else:
            timestamp_str = str(timestamp)
            
        log_type_display = log.get('type', 'unknown').replace('_', ' ').title()
        success_rate = log.get('success_rate', 0)
        
        rate_class = "rate-high" if success_rate > 80 else "rate-medium" if success_rate > 50 else "rate-low"
        
        stats = log.get('stats', {})
        total_processed = stats.get('total_companies', stats.get('total_jobs', 0))
        total_errors = log.get('total_errors', 0)
        
        html_content += f"""
                        <tr onclick="viewLogDetails('{log.get('_id', '')}')">
                            <td class="log-timestamp">{timestamp_str}</td>
                            <td><span class="log-type enrichment">{log_type_display}</span></td>
                            <td><span class="success-rate {rate_class}">{success_rate:.1f}%</span></td>
                            <td>{total_processed:,}</td>
                            <td class="{'error' if total_errors > 0 else 'success'}">{total_errors}</td>
                            <td>N/A</td>
                            <td><a href="/admin/logs/details/{log.get('_id', '')}" class="view-btn">View Details</a></td>
                        </tr>"""
    
    html_content += f"""
                    </tbody>
                </table>
            </div>
            
            <div class="pagination">
                {logs_data.get('pagination_html', '')}
            </div>
        </div>
        
        <script>
            function filterLogs(type) {{
                window.location.href = '/admin/logs?log_type=' + type;
            }}
            
            function refreshLogs() {{
                window.location.reload();
            }}
            
            function viewLogDetails(logId) {{
                window.location.href = '/admin/logs/details/' + logId;
            }}
            
            async function runCompanyEnrichment() {{
                if (confirm('Bu işlem şirket website verilerini yeniden işleyecek. Devam etmek istiyor musunuz?')) {{
                    try {{
                        const response = await fetch('/admin/actions/run-company-enrichment', {{method: 'POST'}});
                        const data = await response.json();
                        
                        if (data.status === 'success') {{
                            alert('✅ Company enrichment başlatıldı: ' + data.message);
                            setTimeout(() => window.location.reload(), 2000);
                        }} else {{
                            alert('❌ Hata: ' + data.message);
                        }}
                    }} catch (error) {{
                        alert('❌ Hata: ' + error.message);
                    }}
                }}
            }}
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

@logs_router.get("/logs/errors", response_class=HTMLResponse)
async def admin_error_logs(request: Request, page: int = 1, error_type: str = "all"):
    """Detailed error logs page"""
    
    errors_data = await get_error_logs(page, error_type)
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Error Logs - Buzz2Remote Admin</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; background: #f8f9fa; }}
            .header {{ background: #343a40; color: white; padding: 1rem 2rem; }}
            .nav {{ background: white; padding: 1rem 2rem; border-bottom: 1px solid #dee2e6; }}
            .nav a {{ margin-right: 20px; text-decoration: none; color: #007bff; }}
            .nav a:hover {{ text-decoration: underline; }}
            .container {{ padding: 2rem; }}
            .filters {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; }}
            .filters select, .filters button {{ padding: 8px 15px; margin: 5px; border: 1px solid #ddd; border-radius: 4px; }}
            .error-item {{ background: white; margin-bottom: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-left: 4px solid #dc3545; }}
            .error-header {{ padding: 15px 20px; border-bottom: 1px solid #eee; cursor: pointer; }}
            .error-header:hover {{ background: #f8f9fa; }}
            .error-company {{ font-weight: bold; color: #333; }}
            .error-type {{ background: #dc3545; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.8em; margin-left: 10px; }}
            .error-timestamp {{ color: #666; font-size: 0.9em; float: right; }}
            .error-details {{ padding: 20px; background: #f8f9fa; display: none; }}
            .error-message {{ background: #fff; padding: 15px; border-radius: 4px; border-left: 4px solid #dc3545; margin-bottom: 15px; }}
            .error-metadata {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }}
            .metadata-item {{ background: #fff; padding: 10px; border-radius: 4px; }}
            .metadata-label {{ font-weight: bold; color: #666; font-size: 0.9em; }}
            .metadata-value {{ color: #333; word-break: break-all; }}
            .pagination {{ text-align: center; margin: 20px 0; }}
            .pagination a {{ margin: 0 5px; padding: 8px 12px; text-decoration: none; color: #007bff; border: 1px solid #ddd; border-radius: 4px; }}
            .pagination a:hover {{ background: #f8f9fa; }}
            .pagination .current {{ background: #007bff; color: white; }}
            .back-btn {{ background: #6c757d; color: white; padding: 8px 15px; text-decoration: none; border-radius: 4px; }}
            .back-btn:hover {{ background: #5a6268; color: white; text-decoration: none; }}
            .btn {{ background: #007bff; color: white; padding: 8px 15px; border: none; border-radius: 4px; cursor: pointer; text-decoration: none; }}
            .btn:hover {{ background: #0056b3; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>❌ Detailed Error Logs</h1>
        </div>
        
        <div class="nav">
            <a href="http://localhost:3000">🏠 Ana Sayfa</a>
            <a href="/admin/dashboard">Dashboard</a>
            <a href="/admin/jobs">Jobs</a>
            <a href="/admin/companies">Companies</a>
            <a href="/admin/logs">Logs</a>
            <a href="/admin/apis">API Services</a>
            <a href="/docs">API Docs</a>
        </div>
        
        <div class="container">
            <div class="filters">
                <a href="/admin/logs" class="back-btn">← Back to Logs</a>
                <select onchange="filterErrors(this.value)">
                    <option value="all" {'selected' if error_type == 'all' else ''}>All Errors</option>
                    <option value="extraction_failed" {'selected' if error_type == 'extraction_failed' else ''}>Extraction Failed</option>
                    <option value="missing_uri" {'selected' if error_type == 'missing_uri' else ''}>Missing URI</option>
                    <option value="database_update_failed" {'selected' if error_type == 'database_update_failed' else ''}>Database Errors</option>
                    <option value="processing_exception" {'selected' if error_type == 'processing_exception' else ''}>Processing Exceptions</option>
                    <option value="no_jobs_found" {'selected' if error_type == 'no_jobs_found' else ''}>No Jobs Found</option>
                </select>
                <button onclick="refreshErrors()" class="btn">🔄 Refresh</button>
            </div>"""
    
    for error in errors_data.get('errors', []):
        timestamp = error.get('timestamp', datetime.now())
        if isinstance(timestamp, datetime):
            timestamp_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        else:
            timestamp_str = str(timestamp)
            
        error_id = str(error.get('_id', ''))
        company_name = error.get('company_name', 'Unknown Company')
        error_type = error.get('error_type', 'unknown').replace('_', ' ').title()
        error_message = error.get('error_message', 'No message available')
        uri = error.get('uri', 'N/A')
        extraction_method = error.get('extraction_method', 'N/A')
        
        html_content += f"""
            <div class="error-item">
                <div class="error-header" onclick="toggleErrorDetails('{error_id}')">
                    <span class="error-company">{company_name}</span>
                    <span class="error-type">{error_type}</span>
                    <span class="error-timestamp">{timestamp_str}</span>
                </div>
                <div class="error-details" id="details-{error_id}">
                    <div class="error-message">
                        <strong>Error Message:</strong><br>
                        {error_message}
                    </div>
                    <div class="error-metadata">
                        <div class="metadata-item">
                            <div class="metadata-label">Company Name</div>
                            <div class="metadata-value">{company_name}</div>
                        </div>
                        <div class="metadata-item">
                            <div class="metadata-label">Career Page URI</div>
                            <div class="metadata-value">{uri}</div>
                        </div>
                        <div class="metadata-item">
                            <div class="metadata-label">Extraction Method</div>
                            <div class="metadata-value">{extraction_method}</div>
                        </div>
                        <div class="metadata-item">
                            <div class="metadata-label">Log Type</div>
                            <div class="metadata-value">{error.get('log_type', 'N/A')}</div>
                        </div>
                    </div>
                </div>
            </div>"""
    
    html_content += f"""
            <div class="pagination">
                {errors_data.get('pagination_html', '')}
            </div>
        </div>
        
        <script>
            function toggleErrorDetails(errorId) {{
                const details = document.getElementById('details-' + errorId);
                if (details.style.display === 'none' || details.style.display === '') {{
                    details.style.display = 'block';
                }} else {{
                    details.style.display = 'none';
                }}
            }}
            
            function filterErrors(type) {{
                window.location.href = '/admin/logs/errors?error_type=' + type;
            }}
            
            function refreshErrors() {{
                window.location.reload();
            }}
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

@logs_router.get("/logs/details/{log_id}", response_class=HTMLResponse)
async def admin_log_details(log_id: str, request: Request):
    """Detailed view of a specific processing log"""
    
    log_details = await get_log_details(log_id)
    
    if not log_details:
        return HTMLResponse(content="<h1>Log not found</h1>", status_code=404)
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Log Details - Buzz2Remote Admin</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; background: #f8f9fa; }}
            .header {{ background: #343a40; color: white; padding: 1rem 2rem; }}
            .nav {{ background: white; padding: 1rem 2rem; border-bottom: 1px solid #dee2e6; }}
            .nav a {{ margin-right: 20px; text-decoration: none; color: #007bff; }}
            .nav a:hover {{ text-decoration: underline; }}
            .container {{ padding: 2rem; }}
            .back-btn {{ background: #6c757d; color: white; padding: 8px 15px; text-decoration: none; border-radius: 4px; margin-bottom: 20px; display: inline-block; }}
            .back-btn:hover {{ background: #5a6268; color: white; text-decoration: none; }}
            .log-summary {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; }}
            .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }}
            .stat-item {{ background: #f8f9fa; padding: 15px; border-radius: 4px; text-align: center; }}
            .stat-number {{ font-size: 1.5rem; font-weight: bold; margin-bottom: 5px; }}
            .stat-label {{ color: #666; font-size: 0.9em; }}
            .success {{ color: #28a745; }}
            .warning {{ color: #ffc107; }}
            .error {{ color: #dc3545; }}
            .errors-section {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .error-list {{ max-height: 600px; overflow-y: auto; }}
            .error-item {{ background: #f8f9fa; margin-bottom: 10px; padding: 15px; border-radius: 4px; border-left: 4px solid #dc3545; }}
            .error-company {{ font-weight: bold; color: #333; }}
            .error-message {{ color: #666; margin: 5px 0; }}
            .error-meta {{ font-size: 0.8em; color: #999; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📊 Log Details</h1>
        </div>
        
        <div class="nav">
            <a href="http://localhost:3000">🏠 Ana Sayfa</a>
            <a href="/admin/dashboard">Dashboard</a>
            <a href="/admin/jobs">Jobs</a>
            <a href="/admin/companies">Companies</a>
            <a href="/admin/logs">Logs</a>
            <a href="/admin/apis">API Services</a>
            <a href="/docs">API Docs</a>
        </div>
        
        <div class="container">
            <a href="/admin/logs" class="back-btn">← Back to Logs</a>
            
            <div class="log-summary">
                <h2>Processing Run Details</h2>
                <p><strong>Type:</strong> {log_details.get('type', 'Unknown').replace('_', ' ').title()}</p>
                <p><strong>Timestamp:</strong> {log_details.get('timestamp', 'Unknown')}</p>
                <p><strong>Success Rate:</strong> <span class="{'success' if log_details.get('success_rate', 0) > 80 else 'warning' if log_details.get('success_rate', 0) > 50 else 'error'}">{log_details.get('success_rate', 0):.1f}%</span></p>
                
                <div class="stats-grid">"""
    
    stats = log_details.get('stats', {})
    
    for stat_key, stat_value in stats.items():
        stat_label = stat_key.replace('_', ' ').title()
        if isinstance(stat_value, (int, float)):
            html_content += f"""
                    <div class="stat-item">
                        <div class="stat-number">{stat_value:,}</div>
                        <div class="stat-label">{stat_label}</div>
                    </div>"""
    
    html_content += """
                </div>
            </div>"""
    
    # Show processing errors
    processing_errors = log_details.get('processing_errors', [])
    update_errors = log_details.get('update_errors', [])
    
    if processing_errors or update_errors:
        html_content += f"""
            <div class="errors-section">
                <h3>Processing Errors ({len(processing_errors)} found)</h3>
                <div class="error-list">"""
        
        for error in processing_errors[:50]:  # Show first 50 errors
            html_content += f"""
                    <div class="error-item">
                        <div class="error-company">{error.get('company_name', 'Unknown')}</div>
                        <div class="error-message">{error.get('error_message', 'No message')}</div>
                        <div class="error-meta">Type: {error.get('error_type', 'unknown')} | URI: {error.get('uri', 'N/A')}</div>
                    </div>"""
        
        html_content += """
                </div>
            </div>"""
        
        if update_errors:
            html_content += f"""
            <div class="errors-section">
                <h3>Database Update Errors ({len(update_errors)} found)</h3>
                <div class="error-list">"""
            
            for error in update_errors[:50]:  # Show first 50 errors
                html_content += f"""
                    <div class="error-item">
                        <div class="error-company">{error.get('company_name', 'Unknown')}</div>
                        <div class="error-message">{error.get('error_message', 'No message')}</div>
                        <div class="error-meta">Type: {error.get('error_type', 'unknown')} | Website: {error.get('website', 'N/A')}</div>
                    </div>"""
            
            html_content += """
                </div>
            </div>"""
    
    html_content += """
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

@logs_router.post("/actions/run-company-enrichment")
async def admin_run_company_enrichment():
    """Run company website enrichment process"""
    try:
        # Run the company enrichment script
        script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "company_website_enricher.py")
        
        if not os.path.exists(script_path):
            return {"status": "error", "message": "Company enricher script not found"}
        
        # Run in background
        process = subprocess.Popen(
            ["python", script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        return {
            "status": "success", 
            "message": "Company enrichment process started",
            "process_id": process.pid
        }
        
    except Exception as e:
        logger.error(f"Error starting company enrichment: {str(e)}")
        return {"status": "error", "message": f"Failed to start enrichment: {str(e)}"}

# Helper functions for logs

async def get_processing_logs(page: int = 1, log_type: str = "all", limit: int = 20):
    """Get processing logs with pagination"""
    if not DATABASE_AVAILABLE:
        return {"logs": [], "pagination_html": ""}
    
    try:
        # Build filter
        filter_query = {}
        if log_type != "all":
            filter_query["type"] = log_type
        
        # Get total count
        total_logs = await db.processing_logs.count_documents(filter_query)
        
        # Calculate pagination
        total_pages = (total_logs + limit - 1) // limit
        skip = (page - 1) * limit
        
        # Get logs
        cursor = db.processing_logs.find(filter_query).sort("timestamp", -1).skip(skip).limit(limit)
        logs = await cursor.to_list(length=limit)
        
        # Generate pagination HTML
        pagination_html = ""
        if total_pages > 1:
            if page > 1:
                pagination_html += f'<a href="/admin/logs?page={page-1}&log_type={log_type}">← Previous</a>'
            
            for p in range(max(1, page-2), min(total_pages+1, page+3)):
                if p == page:
                    pagination_html += f'<a href="/admin/logs?page={p}&log_type={log_type}" class="current">{p}</a>'
                else:
                    pagination_html += f'<a href="/admin/logs?page={p}&log_type={log_type}">{p}</a>'
            
            if page < total_pages:
                pagination_html += f'<a href="/admin/logs?page={page+1}&log_type={log_type}">Next →</a>'
        
        return {
            "logs": logs,
            "pagination_html": pagination_html,
            "total_logs": total_logs,
            "current_page": page,
            "total_pages": total_pages
        }
        
    except Exception as e:
        logger.error(f"Error fetching processing logs: {str(e)}")
        return {"logs": [], "pagination_html": ""}

async def get_error_logs(page: int = 1, error_type: str = "all", limit: int = 20):
    """Get error logs with pagination"""
    if not DATABASE_AVAILABLE:
        return {"errors": [], "pagination_html": ""}
    
    try:
        # Build filter
        filter_query = {}
        if error_type != "all":
            filter_query["error_type"] = error_type
        
        # Get total count
        total_errors = await db.error_logs.count_documents(filter_query)
        
        # Calculate pagination
        total_pages = (total_errors + limit - 1) // limit
        skip = (page - 1) * limit
        
        # Get errors
        cursor = db.error_logs.find(filter_query).sort("timestamp", -1).skip(skip).limit(limit)
        errors = await cursor.to_list(length=limit)
        
        # Generate pagination HTML
        pagination_html = ""
        if total_pages > 1:
            if page > 1:
                pagination_html += f'<a href="/admin/logs/errors?page={page-1}&error_type={error_type}">← Previous</a>'
            
            for p in range(max(1, page-2), min(total_pages+1, page+3)):
                if p == page:
                    pagination_html += f'<a href="/admin/logs/errors?page={p}&error_type={error_type}" class="current">{p}</a>'
                else:
                    pagination_html += f'<a href="/admin/logs/errors?page={p}&error_type={error_type}">{p}</a>'
            
            if page < total_pages:
                pagination_html += f'<a href="/admin/logs/errors?page={page+1}&error_type={error_type}">Next →</a>'
        
        return {
            "errors": errors,
            "pagination_html": pagination_html,
            "total_errors": total_errors,
            "current_page": page,
            "total_pages": total_pages
        }
        
    except Exception as e:
        logger.error(f"Error fetching error logs: {str(e)}")
        return {"errors": [], "pagination_html": ""}

async def get_error_summary():
    """Get error summary statistics"""
    if not DATABASE_AVAILABLE:
        return {}
    
    try:
        # Get recent runs
        recent_runs = await db.processing_logs.find().sort("timestamp", -1).limit(10).to_list(length=10)
        
        total_runs = len(recent_runs)
        total_errors = sum(log.get('total_errors', 0) for log in recent_runs)
        avg_success_rate = sum(log.get('success_rate', 0) for log in recent_runs) / max(total_runs, 1)
        
        last_run = "Never"
        if recent_runs:
            last_timestamp = recent_runs[0].get('timestamp')
            if isinstance(last_timestamp, datetime):
                last_run = last_timestamp.strftime('%Y-%m-%d %H:%M')
        
        return {
            "total_runs": total_runs,
            "total_errors": total_errors,
            "avg_success_rate": avg_success_rate,
            "last_run": last_run
        }
        
    except Exception as e:
        logger.error(f"Error getting error summary: {str(e)}")
        return {}

async def get_log_details(log_id: str):
    """Get detailed information about a specific log"""
    if not DATABASE_AVAILABLE:
        return None
    
    try:
        from bson import ObjectId
        log = await db.processing_logs.find_one({"_id": ObjectId(log_id)})
        return log
        
    except Exception as e:
        logger.error(f"Error getting log details: {str(e)}")
        return None 