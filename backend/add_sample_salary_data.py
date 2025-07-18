import asyncio
from database.db import get_database
from datetime import datetime

async def add_sample_salary_data():
    """Test için örnek maaş verileri ekle"""
    db = await get_database()
    
    # Örnek maaş verileri
    sample_jobs = [
        {
            "title": "Software Engineer",
            "company": "Tech Corp",
            "location": "Remote",
            "salary_min": 80000,
            "salary_max": 120000,
            "salary_currency": "USD",
            "salary_period": "yearly",
            "is_estimated": False,
            "created_at": datetime.now().isoformat(),
            "job_type": "Full-time",
            "work_type": "remote"
        },
        {
            "title": "Senior Software Engineer",
            "company": "Tech Corp",
            "location": "Remote",
            "salary_min": 120000,
            "salary_max": 180000,
            "salary_currency": "USD",
            "salary_period": "yearly",
            "is_estimated": False,
            "created_at": datetime.now().isoformat(),
            "job_type": "Full-time",
            "work_type": "remote"
        },
        {
            "title": "Frontend Developer",
            "company": "Web Solutions",
            "location": "Remote",
            "salary_min": 70000,
            "salary_max": 110000,
            "salary_currency": "USD",
            "salary_period": "yearly",
            "is_estimated": False,
            "created_at": datetime.now().isoformat(),
            "job_type": "Full-time",
            "work_type": "remote"
        },
        {
            "title": "Backend Developer",
            "company": "API Masters",
            "location": "Remote",
            "salary_min": 75000,
            "salary_max": 130000,
            "salary_currency": "USD",
            "salary_period": "yearly",
            "is_estimated": False,
            "created_at": datetime.now().isoformat(),
            "job_type": "Full-time",
            "work_type": "remote"
        },
        {
            "title": "Full Stack Developer",
            "company": "Full Stack Inc",
            "location": "Remote",
            "salary_min": 85000,
            "salary_max": 140000,
            "salary_currency": "USD",
            "salary_period": "yearly",
            "is_estimated": False,
            "created_at": datetime.now().isoformat(),
            "job_type": "Full-time",
            "work_type": "remote"
        },
        {
            "title": "Product Manager",
            "company": "Product Co",
            "location": "Remote",
            "salary_min": 90000,
            "salary_max": 150000,
            "salary_currency": "USD",
            "salary_period": "yearly",
            "is_estimated": False,
            "created_at": datetime.now().isoformat(),
            "job_type": "Full-time",
            "work_type": "remote"
        },
        {
            "title": "Data Scientist",
            "company": "Data Corp",
            "location": "Remote",
            "salary_min": 95000,
            "salary_max": 160000,
            "salary_currency": "USD",
            "salary_period": "yearly",
            "is_estimated": False,
            "created_at": datetime.now().isoformat(),
            "job_type": "Full-time",
            "work_type": "remote"
        },
        {
            "title": "DevOps Engineer",
            "company": "Cloud Solutions",
            "location": "Remote",
            "salary_min": 80000,
            "salary_max": 130000,
            "salary_currency": "USD",
            "salary_period": "yearly",
            "is_estimated": False,
            "created_at": datetime.now().isoformat(),
            "job_type": "Full-time",
            "work_type": "remote"
        },
        {
            "title": "UX Designer",
            "company": "Design Studio",
            "location": "Remote",
            "salary_min": 70000,
            "salary_max": 120000,
            "salary_currency": "USD",
            "salary_period": "yearly",
            "is_estimated": False,
            "created_at": datetime.now().isoformat(),
            "job_type": "Full-time",
            "work_type": "remote"
        },
        {
            "title": "QA Engineer",
            "company": "Quality Corp",
            "location": "Remote",
            "salary_min": 65000,
            "salary_max": 110000,
            "salary_currency": "USD",
            "salary_period": "yearly",
            "is_estimated": False,
            "created_at": datetime.now().isoformat(),
            "job_type": "Full-time",
            "work_type": "remote"
        }
    ]
    
    # Verileri ekle
    result = await db.jobs.insert_many(sample_jobs)
    print(f"{len(result.inserted_ids)} adet örnek iş eklendi")
    
    # Kontrol et
    jobs_with_salary = await db.jobs.count_documents({
        'salary_min': {'$exists': True, '$ne': None},
        'salary_max': {'$exists': True, '$ne': None}
    })
    print(f"Toplam maaş bilgisi olan iş sayısı: {jobs_with_salary}")

if __name__ == "__main__":
    asyncio.run(add_sample_salary_data()) 