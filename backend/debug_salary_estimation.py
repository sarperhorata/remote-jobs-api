import asyncio
from services.salary_estimation_service import salary_estimation_service
from database.db import get_database

async def debug_salary_estimation():
    """Maaş tahmin servisini debug et"""
    db = await get_database()
    
    # Veritabanındaki işleri kontrol et
    print("=== Veritabanı Kontrolü ===")
    total_jobs = await db.jobs.count_documents({})
    print(f"Toplam iş sayısı: {total_jobs}")
    
    jobs_with_salary = await db.jobs.count_documents({
        'salary_min': {'$exists': True, '$ne': None},
        'salary_max': {'$exists': True, '$ne': None}
    })
    print(f"Maaş bilgisi olan işler: {jobs_with_salary}")
    
    # Maaş bilgisi olan işlerin detaylarını göster
    salary_jobs = await db.jobs.find({
        'salary_min': {'$exists': True, '$ne': None},
        'salary_max': {'$exists': True, '$ne': None}
    }).to_list(10)
    
    print("\n=== Maaş Bilgisi Olan İşler ===")
    for job in salary_jobs:
        print(f"- {job.get('title', 'N/A')}: ${job.get('salary_min')} - ${job.get('salary_max')} {job.get('salary_currency', 'USD')}")
    
    # Servisi test et
    print("\n=== Maaş Tahmin Testi ===")
    await salary_estimation_service.initialize()
    
    # Benzer işleri bul
    similar_jobs = await salary_estimation_service.find_similar_jobs("Software Engineer", "Remote")
    print(f"Benzer iş sayısı: {len(similar_jobs)}")
    
    for job in similar_jobs:
        print(f"- {job.get('title', 'N/A')}: ${job.get('salary_min')} - ${job.get('salary_max')} {job.get('salary_currency', 'USD')}")
    
    # Maaş tahmini yap
    estimation = await salary_estimation_service.estimate_salary("Software Engineer", "Remote")
    print(f"\nMaaş tahmini: {estimation}")

if __name__ == "__main__":
    asyncio.run(debug_salary_estimation()) 