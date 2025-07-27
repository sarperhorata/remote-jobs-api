import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import asyncio
import html
import os
import re

from bs4 import BeautifulSoup
from motor.motor_asyncio import AsyncIOMotorClient

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/buzz2remote")
DB_NAME = os.getenv("DB_NAME", "buzz2remote")
COLLECTION_NAME = "jobs"


def clean_html_tags(text):
    """HTML taglerini temizle ve metni düzenle"""
    if not text:
        return text

    # HTML entities'leri decode et
    text = html.unescape(text)

    # BeautifulSoup ile HTML taglerini temizle
    soup = BeautifulSoup(text, "html.parser")
    clean_text = soup.get_text()

    # Fazla boşlukları temizle
    clean_text = re.sub(r"\s+", " ", clean_text)
    clean_text = clean_text.strip()

    return clean_text


async def clean_html_tags_migration():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DB_NAME]
    jobs_col = db[COLLECTION_NAME]

    print("🧹 HTML Tagleri Temizleme Migration Başlıyor...")
    print("=" * 80)

    # HTML tag pattern'i
    html_pattern = re.compile(r"<[^>]+>")

    # HTML tagleri olan iş ilanlarını bul ve temizle
    updated_count = 0
    total_checked = 0

    async for job in jobs_col.find({}):
        total_checked += 1
        description = job.get("description", "")

        if html_pattern.search(description):
            # HTML taglerini temizle
            cleaned_description = clean_html_tags(description)

            # Veritabanını güncelle
            await jobs_col.update_one(
                {"_id": job["_id"]}, {"$set": {"description": cleaned_description}}
            )

            updated_count += 1

            if updated_count <= 5:  # İlk 5 örneği göster
                print(f"✅ Temizlendi: {job.get('title', '')[:50]}...")
                print(f"   Önceki: {description[:100]}...")
                print(f"   Sonraki: {cleaned_description[:100]}...")
                print()

    print(f"📊 Toplam Kontrol Edilen: {total_checked}")
    print(f"🧹 Temizlenen: {updated_count}")
    print(f"📈 Oran: %{(updated_count/total_checked*100):.2f}")
    print("✅ HTML tagleri temizleme tamamlandı!")

    client.close()


if __name__ == "__main__":
    asyncio.run(clean_html_tags_migration())
