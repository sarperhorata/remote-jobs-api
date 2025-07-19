import sys, os; sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from services.job_title_parser import job_title_parser
import os
import pprint

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/buzz2remote")
DB_NAME = os.getenv("DB_NAME", "buzz2remote")
COLLECTION_NAME = "jobs"

async def migrate_job_titles():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DB_NAME]
    jobs_col = db[COLLECTION_NAME]

    print("🚀 Job Title Parsing Migration Başlıyor...")
    print(f"📊 Veritabanı: {DB_NAME}")
    print(f"📋 Koleksiyon: {COLLECTION_NAME}")
    print("-" * 80)

    # İstatistikler
    total_jobs = 0
    updated_jobs = 0
    examples_shown = 0

    cursor = jobs_col.find({})
    async for job in cursor:
        total_jobs += 1
        original_title = job.get("title", "")
        
        if not original_title:
            continue

        # Parse job title
        parsed = job_title_parser.parse_job_title(original_title)
        
        # Check if we need to update
        needs_update = False
        update_fields = {}
        
        # Check each field
        if job.get("parsed_job_title") != parsed.parsed_title:
            needs_update = True
            update_fields["parsed_job_title"] = parsed.parsed_title
            
        if job.get("job_title_category") != parsed.category:
            needs_update = True
            update_fields["job_title_category"] = parsed.category
            
        if job.get("job_title_level") != parsed.level:
            needs_update = True
            update_fields["job_title_level"] = parsed.level
            
        if job.get("job_title_skills") != parsed.skills:
            needs_update = True
            update_fields["job_title_skills"] = parsed.skills
            
        if job.get("job_title_location") != parsed.location:
            needs_update = True
            update_fields["job_title_location"] = parsed.location
            
        if job.get("job_title_work_type") != parsed.work_type:
            needs_update = True
            update_fields["job_title_work_type"] = parsed.work_type
            
        if job.get("job_title_department") != parsed.department:
            needs_update = True
            update_fields["job_title_department"] = parsed.department
            
        # Preserve original title
        if job.get("original_job_title") != original_title:
            needs_update = True
            update_fields["original_job_title"] = original_title

        if needs_update:
            # Update the document
            await jobs_col.update_one(
                {"_id": job["_id"]},
                {"$set": update_fields}
            )
            updated_jobs += 1
            
            # Show first 5 examples
            if examples_shown < 5:
                print(f"✅ Güncellendi - ID: {job['_id']}")
                print(f"   Orijinal: {original_title}")
                print(f"   Parsed:   {parsed.parsed_title}")
                print(f"   Kategori: {parsed.category}")
                print(f"   Seviye:   {parsed.level}")
                print(f"   Skills:   {parsed.skills}")
                print(f"   Lokasyon: {parsed.location}")
                print(f"   Çalışma:  {parsed.work_type}")
                print(f"   Departman: {parsed.department}")
                print("-" * 80)
                examples_shown += 1

    print(f"📈 Migration Tamamlandı!")
    print(f"   Toplam İş İlanı: {total_jobs}")
    print(f"   Güncellenen: {updated_jobs}")
    print(f"   Güncelleme Oranı: {(updated_jobs/total_jobs*100):.1f}%")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(migrate_job_titles()) 