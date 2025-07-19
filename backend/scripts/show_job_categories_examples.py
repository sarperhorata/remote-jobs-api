import sys, os; sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/buzz2remote")
DB_NAME = os.getenv("DB_NAME", "buzz2remote")
COLLECTION_NAME = "jobs"

async def show_job_categories_examples():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DB_NAME]
    jobs_col = db[COLLECTION_NAME]

    print("📋 Her İş Kategorisinden Örnekler:")
    print("=" * 80)

    # Kategorileri tanımlayalım
    categories = [
        "Technology", "Management", "Marketing", "Sales", 
        "HR", "Finance", "Legal", "Operations", "Design", 
        "Customer Service", "Education", "Healthcare", "Other"
    ]

    for category in categories:
        # Her kategoriden bir örnek bul
        job = await jobs_col.find_one({"job_title_category": category})
        
        if job:
            print(f"🔹 {category}:")
            print(f"   ID: {job['_id']}")
            print(f"   Orijinal: {job.get('title', 'N/A')}")
            print(f"   Parsed:   {job.get('parsed_job_title', 'N/A')}")
            print(f"   Seviye:   {job.get('job_title_level', 'N/A')}")
            print(f"   Skills:   {job.get('job_title_skills', [])}")
            print(f"   Lokasyon: {job.get('job_title_location', 'N/A')}")
            print(f"   Çalışma:  {job.get('job_title_work_type', 'N/A')}")
            print(f"   Departman: {job.get('job_title_department', 'N/A')}")
            print("-" * 80)
        else:
            print(f"🔹 {category}: Örnek bulunamadı")
            print("-" * 80)

    # Kategori istatistikleri
    print("\n📊 Kategori İstatistikleri:")
    print("=" * 80)
    
    pipeline = [
        {"$group": {"_id": "$job_title_category", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    
    category_stats = await jobs_col.aggregate(pipeline).to_list(None)
    
    total_jobs = sum(stat["count"] for stat in category_stats)
    
    for stat in category_stats:
        category = stat["_id"] or "Kategorisiz"
        count = stat["count"]
        percentage = (count / total_jobs) * 100
        print(f"   {category}: {count:,} ilan (%{percentage:.1f})")
    
    print(f"\n📈 Toplam: {total_jobs:,} iş ilanı")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(show_job_categories_examples()) 