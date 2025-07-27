import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import asyncio
import os
import re

from motor.motor_asyncio import AsyncIOMotorClient

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/buzz2remote")
DB_NAME = os.getenv("DB_NAME", "buzz2remote")
COLLECTION_NAME = "jobs"


async def check_html_tags():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DB_NAME]
    jobs_col = db[COLLECTION_NAME]

    print("🔍 HTML Tagleri Kontrol Ediliyor...")
    print("=" * 80)

    # HTML tag pattern'i
    html_pattern = re.compile(r"<[^>]+>")

    # HTML tagleri olan iş ilanlarını bul
    jobs_with_html = []
    total_jobs = 0

    async for job in jobs_col.find({}):
        total_jobs += 1
        description = job.get("description", "")

        if html_pattern.search(description):
            jobs_with_html.append(
                {
                    "id": str(job["_id"]),
                    "title": job.get("title", ""),
                    "company": job.get("company", ""),
                    "html_tags": html_pattern.findall(description),
                }
            )

    print(f"📊 Toplam İş İlanı: {total_jobs}")
    print(f"🏷️  HTML Tagleri Olan: {len(jobs_with_html)}")
    print(f"📈 Oran: %{(len(jobs_with_html)/total_jobs*100):.2f}")
    print()

    if jobs_with_html:
        print("🔍 HTML Tagleri Bulunan İş İlanları:")
        print("-" * 80)

        for i, job in enumerate(jobs_with_html[:10], 1):  # İlk 10 tanesini göster
            print(f"{i}. {job['title']} - {job['company']}")
            print(f"   HTML Tagleri: {job['html_tags'][:5]}")  # İlk 5 tag'i göster
            print()

        if len(jobs_with_html) > 10:
            print(f"... ve {len(jobs_with_html) - 10} tane daha")
    else:
        print("✅ Hiç HTML tagi bulunamadı!")

    await client.close()


if __name__ == "__main__":
    asyncio.run(check_html_tags())
