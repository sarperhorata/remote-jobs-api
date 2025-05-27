from fastapi import APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from database import get_db
from typing import List, Dict, Any

router = APIRouter()

# Add CORS middleware
router.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@router.get("/companies")
async def get_companies():
    try:
        db = get_db()
        companies = list(db.companies.find({"is_active": True}))
        return {"companies": companies}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/companies/{company_id}")
async def get_company(company_id: str):
    try:
        db = get_db()
        company = db.companies.find_one({"_id": company_id})
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        return company
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 