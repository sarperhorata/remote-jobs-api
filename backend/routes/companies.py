from fastapi import APIRouter

router = APIRouter(prefix="/companies", tags=["companies"])

@router.get("")
async def get_companies():
    """Get all companies"""
    return {
        "companies": [
            {
                "_id": "1",
                "name": "Remote Tech Co",
                "description": "Leading remote-first technology company",
                "website": "https://remotetech.com",
                "location": "Remote",
                "employees": "50-100",
                "industry": "Technology",
                "is_active": True
            },
            {
                "_id": "2", 
                "name": "Global Solutions",
                "description": "Worldwide consulting and development services",
                "website": "https://globalsolutions.com",
                "location": "Remote",
                "employees": "100-500",
                "industry": "Consulting",
                "is_active": True
            },
            {
                "_id": "3",
                "name": "Cloud Innovations",
                "description": "Cloud infrastructure and DevOps specialists",
                "website": "https://cloudinnovations.com",
                "location": "Remote",
                "employees": "10-50",
                "industry": "Cloud Services",
                "is_active": True
            }
        ],
        "total": 3
    }

@router.get("/{company_id}")
async def get_company(company_id: str):
    """Get company by ID"""
    companies = {
        "1": {
            "_id": "1",
            "name": "Remote Tech Co",
            "description": "Leading remote-first technology company specializing in modern web applications.",
            "website": "https://remotetech.com",
            "location": "Remote",
            "employees": "50-100",
            "industry": "Technology",
            "is_active": True,
            "jobs_count": 5,
            "benefits": ["Remote work", "Health insurance", "Flexible hours"]
        },
        "2": {
            "_id": "2",
            "name": "Global Solutions", 
            "description": "Worldwide consulting and development services for enterprise clients.",
            "website": "https://globalsolutions.com",
            "location": "Remote",
            "employees": "100-500",
            "industry": "Consulting",
            "is_active": True,
            "jobs_count": 3,
            "benefits": ["Remote work", "401k", "Training budget"]
        }
    }
    
    if company_id not in companies:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Company not found")
    
    return companies[company_id] 