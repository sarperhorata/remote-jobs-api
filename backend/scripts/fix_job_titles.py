import re

from pymongo import MongoClient
from tqdm import tqdm

# MongoDB bağlantısı
MONGODB_URL = "mongodb://localhost:27017"
DB_NAME = "buzz2remote"
COLLECTION_NAME = "jobs"

# Anahtar kelimeler
JOB_TYPES = [
    ("Full[- ]?time", "Full-time"),
    ("Part[- ]?time", "Part-time"),
    ("Contract", "Contract"),
    ("Freelance", "Freelance"),
    ("Internship", "Internship"),
    ("Staj", "Internship"),
]
LOCATIONS = [
    "Remote",
    "On[- ]?Site",
    "Hybrid",
    "İstanbul",
    "Istanbul",
    "Ankara",
    "Izmir",
    "London",
    "Berlin",
    "Paris",
    "New York",
    "San Francisco",
    "US",
    "USA",
    "Europe",
    "Türkiye",
    "Turkey",
    "Global",
    "Worldwide",
]

# Lokasyonları regex pattern'e çevir
LOCATION_PATTERN = "|".join([re.escape(loc) for loc in LOCATIONS])
JOB_TYPE_PATTERN = "|".join([pat for pat, _ in JOB_TYPES])

# MongoDB bağlantısı
client = MongoClient(MONGODB_URL)
db = client[DB_NAME]
jobs = db[COLLECTION_NAME]

# Tüm işleri çek
all_jobs = list(jobs.find({}))
print(f"Toplam {len(all_jobs)} iş ilanı bulundu.")

update_count = 0
for job in tqdm(all_jobs):
    original_title = job.get("title", "")
    new_title = original_title
    new_job_type = job.get("job_type", "")
    new_location = job.get("location", "")
    changed = False

    # İş tipi ayrıştır
    for pat, job_type in JOB_TYPES:
        match = re.search(pat, new_title, re.IGNORECASE)
        if match:
            new_job_type = job_type
            # Title'dan çıkar
            new_title = re.sub(pat, "", new_title, flags=re.IGNORECASE).strip()
            changed = True
            break

    # Lokasyon ayrıştır
    loc_match = re.search(LOCATION_PATTERN, new_title, re.IGNORECASE)
    if loc_match:
        loc = loc_match.group(0)
        new_location = loc.replace("-", " ").replace("İ", "I")
        new_title = re.sub(LOCATION_PATTERN, "", new_title, flags=re.IGNORECASE).strip()
        changed = True

    # Kalan gereksiz karakterleri temizle
    new_title = re.sub(r"[\-–—]+", " ", new_title).strip()
    new_title = re.sub(r"\s+", " ", new_title).strip()

    # Eğer değişiklik olduysa güncelle
    if changed and new_title:
        update_fields = {"title": new_title}
        if new_job_type:
            update_fields["job_type"] = new_job_type
        if new_location:
            update_fields["location"] = new_location
        jobs.update_one({"_id": job["_id"]}, {"$set": update_fields})
        update_count += 1

print(f"Düzeltilen iş ilanı sayısı: {update_count}")
