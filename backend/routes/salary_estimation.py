from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, Dict, List
from pydantic import BaseModel
from services.salary_estimation_service import salary_estimation_service
from database.db import get_database
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/salary", tags=["salary-estimation"])

class SalaryEstimationRequest(BaseModel):
    job_title: str
    location: Optional[str] = None
    company_size: Optional[str] = None
    experience_level: Optional[str] = None

class SalaryEstimationResponse(BaseModel):
    min_salary: int
    max_salary: int
    currency: str
    period: str
    is_estimated: bool
    confidence_score: Optional[float] = None
    data_points: Optional[int] = None
    similar_jobs_count: Optional[int] = None
    mean_salary: Optional[int] = None
    median_salary: Optional[int] = None

@router.post("/estimate", response_model=SalaryEstimationResponse)
async def estimate_salary(request: SalaryEstimationRequest):
    """Maaş tahmini yap"""
    try:
        # Servisi başlat
        await salary_estimation_service.initialize()
        
        # Maaş tahmini yap
        estimation = await salary_estimation_service.estimate_salary(
            job_title=request.job_title,
            location=request.location,
            company_size=request.company_size,
            experience_level=request.experience_level
        )
        
        if not estimation:
            raise HTTPException(
                status_code=404,
                detail="Yeterli veri bulunamadı. Benzer pozisyonlar için maaş bilgisi mevcut değil."
            )
        
        return SalaryEstimationResponse(**estimation)
        
    except Exception as e:
        logger.error(f"Error estimating salary: {e}")
        raise HTTPException(
            status_code=500,
            detail="Maaş tahmini sırasında bir hata oluştu."
        )

@router.post("/extract-from-text")
async def extract_salary_from_text(text: str):
    """Metinden maaş bilgisini çıkar"""
    try:
        # Servisi başlat
        await salary_estimation_service.initialize()
        
        # Maaş bilgisini çıkar
        salary_info = salary_estimation_service.extract_salary_from_text(text)
        
        if not salary_info:
            return {"message": "Metinde maaş bilgisi bulunamadı."}
        
        return salary_info
        
    except Exception as e:
        logger.error(f"Error extracting salary from text: {e}")
        raise HTTPException(
            status_code=500,
            detail="Maaş bilgisi çıkarılırken bir hata oluştu."
        )

@router.get("/similar-jobs/{job_title}")
async def get_similar_jobs(
    job_title: str,
    location: Optional[str] = None,
    company_size: Optional[str] = None,
    experience_level: Optional[str] = None
):
    """Benzer işleri getir"""
    try:
        # Servisi başlat
        await salary_estimation_service.initialize()
        
        # Benzer işleri bul
        similar_jobs = await salary_estimation_service.find_similar_jobs(
            job_title=job_title,
            location=location,
            company_size=company_size,
            experience_level=experience_level
        )
        
        return {
            "job_title": job_title,
            "similar_jobs_count": len(similar_jobs),
            "similar_jobs": similar_jobs[:10]  # İlk 10'u döndür
        }
        
    except Exception as e:
        logger.error(f"Error finding similar jobs: {e}")
        raise HTTPException(
            status_code=500,
            detail="Benzer işler aranırken bir hata oluştu."
        )

@router.post("/process-job")
async def process_job_salary(job_data: Dict):
    """İş verisini işle ve maaş bilgisini ekle"""
    try:
        # Servisi başlat
        await salary_estimation_service.initialize()
        
        # İş verisini işle
        processed_job = await salary_estimation_service.process_job_salary(job_data)
        
        return processed_job
        
    except Exception as e:
        logger.error(f"Error processing job salary: {e}")
        raise HTTPException(
            status_code=500,
            detail="İş verisi işlenirken bir hata oluştu."
        )

@router.get("/statistics")
async def get_salary_statistics():
    """Maaş istatistiklerini getir"""
    try:
        db = await get_database()
        
        # Toplam iş sayısı
        total_jobs = await db.jobs.count_documents({})
        
        # Maaş bilgisi olan iş sayısı
        jobs_with_salary = await db.jobs.count_documents({
            'salary_min': {'$exists': True, '$ne': None},
            'salary_max': {'$exists': True, '$ne': None}
        })
        
        # Tahmin edilen maaş bilgisi olan iş sayısı
        estimated_salary_jobs = await db.jobs.count_documents({
            'is_estimated': True
        })
        
        # Para birimi dağılımı
        currency_pipeline = [
            {'$match': {'salary_currency': {'$exists': True, '$ne': None}}},
            {'$group': {'_id': '$salary_currency', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}}
        ]
        currency_stats = await db.jobs.aggregate(currency_pipeline).to_list(10)
        
        return {
            "total_jobs": total_jobs,
            "jobs_with_salary": jobs_with_salary,
            "estimated_salary_jobs": estimated_salary_jobs,
            "salary_coverage_percentage": round((jobs_with_salary / total_jobs * 100), 2) if total_jobs > 0 else 0,
            "currency_distribution": currency_stats
        }
        
    except Exception as e:
        logger.error(f"Error getting salary statistics: {e}")
        raise HTTPException(
            status_code=500,
            detail="İstatistikler alınırken bir hata oluştu."
        ) 