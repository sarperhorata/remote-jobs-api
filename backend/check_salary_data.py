import asyncio

from database.db import get_database


async def check_salary_data():
    """Veritabanındaki maaş verilerini kontrol et"""
    db = await get_database()

    # Toplam iş sayısı
    total_jobs = await db.jobs.count_documents({})
    print(f"Toplam iş sayısı: {total_jobs}")

    # Maaş bilgisi olan işler
    jobs_with_salary = await db.jobs.count_documents(
        {
            "salary_min": {"$exists": True, "$ne": None},
            "salary_max": {"$exists": True, "$ne": None},
        }
    )
    print(f"Maaş bilgisi olan işler: {jobs_with_salary}")

    # Maaş bilgisi olan işlerin örnekleri
    sample_jobs = (
        await db.jobs.find(
            {
                "salary_min": {"$exists": True, "$ne": None},
                "salary_max": {"$exists": True, "$ne": None},
            }
        )
        .limit(5)
        .to_list(5)
    )

    print("\nÖrnek işler:")
    for job in sample_jobs:
        print(
            f"- {job.get('title', 'N/A')}: ${job.get('salary_min')} - ${job.get('salary_max')} {job.get('salary_currency', 'USD')}"
        )

    # Job title'ları kontrol et
    job_titles = await db.jobs.distinct("title")
    print(f"\nToplam farklı job title sayısı: {len(job_titles)}")

    # İlk 10 job title'ı göster
    print("\nİlk 10 job title:")
    for title in job_titles[:10]:
        print(f"- {title}")


if __name__ == "__main__":
    asyncio.run(check_salary_data())
