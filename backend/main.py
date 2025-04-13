from fastapi import FastAPI, HTTPException, Request, Depends, Security
from bs4 import BeautifulSoup
import requests
import json
from typing import List, Dict
from models import Company, JobPosting, UserCreate, Token
import logging
from datetime import datetime
from selector_validator import SelectorValidator
from rate_limiter import RateLimiter
from urllib.parse import urlparse
from cache_manager import CacheManager
from fastapi.security.api_key import APIKeyHeader
from auth_manager import AuthManager
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from user_manager import UserManager
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pathlib import Path

# Configure logging
logging.basicConfig(
    filename=f'scraper_{datetime.now().strftime("%Y%m%d")}.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

app = FastAPI(
    title="Job Postings Scraper API",
    description="API for scraping job postings from multiple company career pages",
    version="1.0.0"
)

cache_manager = CacheManager()

# API key header tanımı
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)
auth_manager = AuthManager()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
user_manager = UserManager()

async def get_api_key(api_key: str = Depends(api_key_header)):
    if not auth_manager.validate_api_key(api_key):
        raise HTTPException(
            status_code=403,
            detail="Invalid or missing API key"
        )
    return api_key

def load_companies() -> List[Company]:
    try:
        with open('companies.json', 'r') as f:
            data = json.load(f)
            return [Company(**company) for company in data['companies']]
    except Exception as e:
        logging.error(f"Error loading companies: {str(e)}")
        raise HTTPException(status_code=500, detail="Error loading company data")

def scrape_jobs(company: Company) -> List[Dict]:
    jobs = []
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(company.url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        job_elements = soup.select(company.selector)
        
        for element in job_elements:
            job = {
                'company': company.name,
                'job_title': element.text.strip(),
                'link': element.get('href') if element.name == 'a' else element.find('a')['href']
            }
            
            # Handle relative URLs
            if job['link'].startswith('/'):
                job['link'] = f"{company.url.rstrip('/')}{job['link']}"
                
            jobs.append(job)
            
        logging.info(f"Successfully scraped {len(jobs)} jobs from {company.name}")
        return jobs
        
    except Exception as e:
        logging.error(f"Error scraping {company.name}: {str(e)}")
        return []

@app.get("/jobs",
    response_model=List[JobPosting],
    summary="Get all job postings",
    description="""
    Scrapes job postings from configured company career pages.
    
    Authentication:
    - Requires valid API key in X-API-Key header
    
    Features:
    - Returns cached results if available (24 hour cache)
    - Rate limited to 3 requests per IP per day
    - Supports multiple job board platforms (Lever, Greenhouse, Breezy, etc.)
    """,
    responses={
        200: {
            "description": "List of job postings",
            "content": {
                "application/json": {
                    "example": [{
                        "company": "Example Corp",
                        "job_title": "Senior Developer",
                        "link": "https://example.com/jobs/123"
                    }]
                }
            }
        },
        401: {
            "description": "Missing API key"
        },
        403: {
            "description": "Invalid API key"
        },
        429: {
            "description": "Rate limit exceeded"
        },
        500: {
            "description": "Server error or failed to scrape jobs"
        }
    },
    dependencies=[Depends(get_api_key)]
)
async def get_jobs(request: Request):
    """
    Scrape job postings from all configured company career pages
    """
    # Rate limit kontrolü
    if not await cache_manager.check_rate_limit(request):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again later."
        )
    
    # Cache kontrolü
    cache_key = cache_manager.get_cache_key("jobs")
    cached_data = cache_manager.get_cached_data(cache_key)
    if cached_data:
        return cached_data
    
    # Cache'de yoksa yeni veri çek
    all_jobs = []
    failed_sites = []
    
    companies = load_companies()
    
    for company in companies:
        jobs = scrape_jobs(company)
        if jobs:
            all_jobs.extend(jobs)
        else:
            failed_sites.append(company.name)
    
    if failed_sites:
        logging.warning(f"Failed to scrape: {', '.join(failed_sites)}")
    
    if not all_jobs and failed_sites:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to scrape any jobs. Failed sites: {', '.join(failed_sites)}"
        )
    
    # Sonuçları cache'e kaydet
    cache_manager.set_cached_data(cache_key, all_jobs)
    
    return all_jobs

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy"}

@app.post("/users",
    summary="Create new user",
    response_model=dict,
    description="""
    Create a new user account with email and password.
    
    Required fields:
    - email: Valid email address
    - username: Unique username
    - password: User password
    """,
    responses={
        200: {
            "description": "User created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": "User created successfully",
                        "username": "testuser"
                    }
                }
            }
        },
        400: {
            "description": "Username already exists"
        }
    }
)
async def create_user(user: UserCreate):
    """Create a new user account"""
    if new_user := user_manager.create_user(user):
        return {
            "message": "User created successfully",
            "username": new_user.username
        }
    raise HTTPException(
        status_code=400,
        detail="Username already exists"
    )

@app.post("/token",
    summary="Login for access token",
    response_model=Token,
    description="""
    Login with username and password to get access token.
    This token is required for creating API keys.
    
    Token expires in 24 hours.
    """,
    responses={
        200: {
            "description": "Successfully authenticated",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIs...",
                        "token_type": "bearer"
                    }
                }
            }
        },
        401: {
            "description": "Incorrect username or password"
        }
    }
)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login to get access token"""
    user = user_manager.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = user_manager.create_access_token(user)
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api-keys",
    summary="Create new API key",
    response_model=dict,
    dependencies=[Depends(oauth2_scheme)],
    description="""
    Create a new API key for accessing the jobs endpoint.
    Requires authentication with a valid access token.
    
    Store the API key safely as it won't be shown again.
    """,
    responses={
        200: {
            "description": "API key created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "api_key": "generated_api_key_here",
                        "owner": "username",
                        "message": "Store this API key safely, it won't be shown again"
                    }
                }
            }
        },
        401: {
            "description": "Invalid authentication credentials"
        }
    }
)
async def create_api_key(
    token: str = Depends(oauth2_scheme)
):
    """Create a new API key (requires authentication)"""
    user = user_manager.verify_token(token)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials"
        )
    
    api_key = auth_manager.create_api_key(user.username)
    return {
        "api_key": api_key,
        "owner": user.username,
        "message": "Store this API key safely, it won't be shown again"
    }

@app.delete("/api-keys/{api_key}",
    summary="Revoke API key",
    response_model=dict
)
async def revoke_api_key(api_key: str):
    """Revoke an existing API key"""
    if auth_manager.revoke_api_key(api_key):
        return {"message": "API key revoked successfully"}
    raise HTTPException(status_code=404, detail="API key not found")

class JobScraper:
    def __init__(self):
        self.validator = SelectorValidator()
        self.rate_limiter = RateLimiter(interval_hours=12)
        self.logger = logging.getLogger(__name__)
        
    def update_companies_file(self):
        try:
            # companies.json dosyasını oku
            with open('companies.json', 'r') as f:
                data = json.load(f)
            
            updated_companies = []
            for company in data['companies']:
                domain = urlparse(company['url']).netloc
                
                # Rate limit kontrolü
                if not self.rate_limiter.can_make_request(domain):
                    self.logger.info(f"Skipping {company['name']} due to rate limit")
                    updated_companies.append(company)
                    continue
                
                # Seçiciyi doğrula
                new_selector = self.validator.validate_selector(
                    company['url'], 
                    company['selector']
                )
                
                if new_selector and new_selector != company['selector']:
                    self.logger.info(f"Updated selector for {company['name']}: {new_selector}")
                    company['selector'] = new_selector
                    company['last_updated'] = datetime.now().isoformat()
                elif not new_selector:
                    self.logger.warning(f"Could not validate selector for {company['name']}")
                    company['status'] = 'needs_review'
                
                self.rate_limiter.record_request(domain)
                updated_companies.append(company)
            
            # Güncellenmiş verileri kaydet
            data['companies'] = updated_companies
            with open('companies.json', 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Error updating companies file: {str(e)}")

# Static dosyaları ve template'leri ayarla
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    logging.basicConfig(
        filename=f'scraper_updates_{datetime.now().strftime("%Y%m%d")}.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    scraper = JobScraper()
    scraper.update_companies_file() 