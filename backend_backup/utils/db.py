import logging
import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import sqlite3
import asyncio
from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

from utils.config import get_db_url
from models.models import (
    Job, Monitor, Website, Notification, 
    ChangeLog, WebsiteType, NotificationType,
    SelectorBase
)

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# SQLite veritabanı dosya yolu
DB_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "remotejobs.db")

# MongoDB connection string
MONGODB_URL = "mongodb+srv://remotejobs:taBQw9bkYRAtFUOS@remotejobs.tn0gxu0.mongodb.net/"

# Create MongoDB client
client = MongoClient(MONGODB_URL)
async_client = AsyncIOMotorClient(MONGODB_URL)

# Get database
db = client.remote_jobs
async_db = async_client.remote_jobs

# SQLite veritabanı bağlantısı için connection pool
# İleride SQLAlchemy veya başka bir ORM ile değiştirilebilir
class Database:
    """
    SQLite veritabanı işlemleri için yardımcı sınıf
    """
    
    def __init__(self, db_file=DB_FILE):
        self.db_file = db_file
        self.conn = None
        
        # Veritabanı klasörünün var olduğundan emin ol
        os.makedirs(os.path.dirname(db_file), exist_ok=True)
        
        # Veritabanını başlat
        self._init_db()
    
    def _init_db(self):
        """
        Veritabanını ve tabloları oluşturur
        """
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Website tablosu
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS websites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            url TEXT NOT NULL,
            website_type TEXT NOT NULL,
            is_active INTEGER NOT NULL DEFAULT 1,
            selectors TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Monitor tablosu
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS monitors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            website_id INTEGER NOT NULL,
            check_interval INTEGER NOT NULL DEFAULT 60,
            keywords TEXT,
            exclude_keywords TEXT,
            is_active INTEGER NOT NULL DEFAULT 1,
            last_check TIMESTAMP,
            notify_on_change INTEGER NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (website_id) REFERENCES websites(id)
        )
        ''')
        
        # Notification tablosu
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            notification_type TEXT NOT NULL,
            config TEXT NOT NULL,
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Monitor-Notification ilişki tablosu
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS monitor_notifications (
            monitor_id INTEGER NOT NULL,
            notification_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (monitor_id, notification_id),
            FOREIGN KEY (monitor_id) REFERENCES monitors(id),
            FOREIGN KEY (notification_id) REFERENCES notifications(id)
        )
        ''')
        
        # Job tablosu
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            url TEXT NOT NULL UNIQUE,
            description TEXT,
            location TEXT,
            salary TEXT,
            tags TEXT,
            posted_date TIMESTAMP,
            is_remote INTEGER NOT NULL DEFAULT 1,
            website_id INTEGER NOT NULL,
            raw_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (website_id) REFERENCES websites(id)
        )
        ''')
        
        # ChangeLog tablosu
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS change_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            monitor_id INTEGER NOT NULL,
            job_id INTEGER NOT NULL,
            change_type TEXT NOT NULL,
            old_data TEXT,
            new_data TEXT,
            is_notified INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (monitor_id) REFERENCES monitors(id),
            FOREIGN KEY (job_id) REFERENCES jobs(id)
        )
        ''')
        
        conn.commit()
        conn.close()
        
        logger.info(f"Database initialized at {self.db_file}")
    
    def connect(self):
        """
        Veritabanına bağlanır
        """
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_file)
            self.conn.row_factory = sqlite3.Row
        return self.conn
    
    def close(self):
        """
        Veritabanı bağlantısını kapatır
        """
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def execute(self, query, params=None):
        """
        SQL sorgusu çalıştırır
        """
        conn = self.connect()
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        conn.commit()
        return cursor
    
    def fetch_all(self, query, params=None):
        """
        SQL sorgusu çalıştırır ve tüm sonuçları döndürür
        """
        cursor = self.execute(query, params)
        return cursor.fetchall()
    
    def fetch_one(self, query, params=None):
        """
        SQL sorgusu çalıştırır ve ilk sonucu döndürür
        """
        cursor = self.execute(query, params)
        return cursor.fetchone()
    
    def insert(self, table, data):
        """
        Tabloya veri ekler
        """
        keys = ", ".join(data.keys())
        placeholders = ", ".join(["?" for _ in data])
        query = f"INSERT INTO {table} ({keys}) VALUES ({placeholders})"
        cursor = self.execute(query, list(data.values()))
        return cursor.lastrowid
    
    def update(self, table, data, condition, condition_params):
        """
        Tablodaki veriyi günceller
        """
        set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {condition}"
        params = list(data.values()) + condition_params
        cursor = self.execute(query, params)
        return cursor.rowcount
    
    def delete(self, table, condition, params=None):
        """
        Tablodaki veriyi siler
        """
        query = f"DELETE FROM {table} WHERE {condition}"
        cursor = self.execute(query, params)
        return cursor.rowcount


# Uygulama boyunca kullanılacak veritabanı nesnesi
db = Database()


# Website işlemleri
async def get_websites(include_inactive=False) -> List[Website]:
    """
    Tüm web sitelerini döndürür
    """
    condition = "" if include_inactive else "WHERE is_active = 1"
    rows = db.fetch_all(f"SELECT * FROM websites {condition}")
    
    websites = []
    for row in rows:
        website = dict(row)
        if website["selectors"]:
            website["selectors"] = json.loads(website["selectors"])
        else:
            website["selectors"] = []
        
        websites.append(Website(**website))
    
    return websites

async def get_website(website_id: int) -> Optional[Website]:
    """
    Belirli bir web sitesini ID'sine göre döndürür
    """
    row = db.fetch_one("SELECT * FROM websites WHERE id = ?", [website_id])
    if not row:
        return None
    
    website = dict(row)
    if website["selectors"]:
        website["selectors"] = json.loads(website["selectors"])
    else:
        website["selectors"] = []
    
    return Website(**website)

async def create_website(website_data: Dict[str, Any]) -> int:
    """
    Yeni bir web sitesi oluşturur
    """
    # Selektörleri JSON olarak dönüştür
    if "selectors" in website_data and website_data["selectors"]:
        website_data["selectors"] = json.dumps([s.dict() for s in website_data["selectors"]])
    else:
        website_data["selectors"] = None
    
    # created_at ve updated_at alanlarını ayarla
    website_data["created_at"] = datetime.now().isoformat()
    website_data["updated_at"] = datetime.now().isoformat()
    
    # Boolean değerleri 0/1 olarak dönüştür
    if "is_active" in website_data:
        website_data["is_active"] = 1 if website_data["is_active"] else 0
    
    return db.insert("websites", website_data)

async def update_website(website_id: int, website_data: Dict[str, Any]) -> bool:
    """
    Bir web sitesini günceller
    """
    # Selektörleri JSON olarak dönüştür
    if "selectors" in website_data and website_data["selectors"]:
        website_data["selectors"] = json.dumps([s.dict() for s in website_data["selectors"]])
    
    # updated_at alanını güncelle
    website_data["updated_at"] = datetime.now().isoformat()
    
    # Boolean değerleri 0/1 olarak dönüştür
    if "is_active" in website_data:
        website_data["is_active"] = 1 if website_data["is_active"] else 0
    
    rows_affected = db.update("websites", website_data, "id = ?", [website_id])
    return rows_affected > 0

async def delete_website(website_id: int) -> bool:
    """
    Bir web sitesini siler
    """
    rows_affected = db.delete("websites", "id = ?", [website_id])
    return rows_affected > 0


# Monitor işlemleri
async def get_monitors(include_inactive=False) -> List[Monitor]:
    """
    Tüm monitörleri döndürür
    """
    condition = "" if include_inactive else "WHERE is_active = 1"
    rows = db.fetch_all(f"SELECT * FROM monitors {condition}")
    
    monitors = []
    for row in rows:
        monitor = dict(row)
        
        # JSON formatındaki alanları dönüştür
        if monitor["keywords"]:
            monitor["keywords"] = json.loads(monitor["keywords"])
        else:
            monitor["keywords"] = []
        
        if monitor["exclude_keywords"]:
            monitor["exclude_keywords"] = json.loads(monitor["exclude_keywords"])
        else:
            monitor["exclude_keywords"] = []
        
        # Boolean değerleri dönüştür
        monitor["is_active"] = bool(monitor["is_active"])
        monitor["notify_on_change"] = bool(monitor["notify_on_change"])
        
        monitors.append(Monitor(**monitor))
    
    return monitors

async def get_monitor(monitor_id: int) -> Optional[Monitor]:
    """
    Belirli bir monitörü ID'sine göre döndürür
    """
    row = db.fetch_one("SELECT * FROM monitors WHERE id = ?", [monitor_id])
    if not row:
        return None
    
    monitor = dict(row)
    
    # JSON formatındaki alanları dönüştür
    if monitor["keywords"]:
        monitor["keywords"] = json.loads(monitor["keywords"])
    else:
        monitor["keywords"] = []
    
    if monitor["exclude_keywords"]:
        monitor["exclude_keywords"] = json.loads(monitor["exclude_keywords"])
    else:
        monitor["exclude_keywords"] = []
    
    # Boolean değerleri dönüştür
    monitor["is_active"] = bool(monitor["is_active"])
    monitor["notify_on_change"] = bool(monitor["notify_on_change"])
    
    return Monitor(**monitor)

async def create_monitor(monitor_data: Dict[str, Any]) -> int:
    """
    Yeni bir monitör oluşturur
    """
    # Liste alanlarını JSON olarak dönüştür
    if "keywords" in monitor_data and monitor_data["keywords"]:
        monitor_data["keywords"] = json.dumps(monitor_data["keywords"])
    else:
        monitor_data["keywords"] = None
    
    if "exclude_keywords" in monitor_data and monitor_data["exclude_keywords"]:
        monitor_data["exclude_keywords"] = json.dumps(monitor_data["exclude_keywords"])
    else:
        monitor_data["exclude_keywords"] = None
    
    # created_at ve updated_at alanlarını ayarla
    monitor_data["created_at"] = datetime.now().isoformat()
    monitor_data["updated_at"] = datetime.now().isoformat()
    
    # Boolean değerleri 0/1 olarak dönüştür
    if "is_active" in monitor_data:
        monitor_data["is_active"] = 1 if monitor_data["is_active"] else 0
    
    if "notify_on_change" in monitor_data:
        monitor_data["notify_on_change"] = 1 if monitor_data["notify_on_change"] else 0
    
    return db.insert("monitors", monitor_data)

async def update_monitor(monitor_id: int, monitor_data: Dict[str, Any]) -> bool:
    """
    Bir monitörü günceller
    """
    # Liste alanlarını JSON olarak dönüştür
    if "keywords" in monitor_data and monitor_data["keywords"]:
        monitor_data["keywords"] = json.dumps(monitor_data["keywords"])
    
    if "exclude_keywords" in monitor_data and monitor_data["exclude_keywords"]:
        monitor_data["exclude_keywords"] = json.dumps(monitor_data["exclude_keywords"])
    
    # updated_at alanını güncelle
    monitor_data["updated_at"] = datetime.now().isoformat()
    
    # Boolean değerleri 0/1 olarak dönüştür
    if "is_active" in monitor_data:
        monitor_data["is_active"] = 1 if monitor_data["is_active"] else 0
    
    if "notify_on_change" in monitor_data:
        monitor_data["notify_on_change"] = 1 if monitor_data["notify_on_change"] else 0
    
    rows_affected = db.update("monitors", monitor_data, "id = ?", [monitor_id])
    return rows_affected > 0

async def delete_monitor(monitor_id: int) -> bool:
    """
    Bir monitörü siler
    """
    rows_affected = db.delete("monitors", "id = ?", [monitor_id])
    return rows_affected > 0


# Notification işlemleri
async def get_notifications(include_inactive=False) -> List[Notification]:
    """
    Tüm bildirimleri döndürür
    """
    condition = "" if include_inactive else "WHERE is_active = 1"
    rows = db.fetch_all(f"SELECT * FROM notifications {condition}")
    
    notifications = []
    for row in rows:
        notification = dict(row)
        
        # JSON formatındaki config alanını dönüştür
        if notification["config"]:
            notification["config"] = json.loads(notification["config"])
        else:
            notification["config"] = {}
        
        # Boolean değerleri dönüştür
        notification["is_active"] = bool(notification["is_active"])
        
        notifications.append(Notification(**notification))
    
    return notifications

async def get_notification(notification_id: int) -> Optional[Notification]:
    """
    Belirli bir bildirimi ID'sine göre döndürür
    """
    row = db.fetch_one("SELECT * FROM notifications WHERE id = ?", [notification_id])
    if not row:
        return None
    
    notification = dict(row)
    
    # JSON formatındaki config alanını dönüştür
    if notification["config"]:
        notification["config"] = json.loads(notification["config"])
    else:
        notification["config"] = {}
    
    # Boolean değerleri dönüştür
    notification["is_active"] = bool(notification["is_active"])
    
    return Notification(**notification)

async def create_notification(notification_data: Dict[str, Any]) -> int:
    """
    Yeni bir bildirim oluşturur
    """
    # Config alanını JSON olarak dönüştür
    if "config" in notification_data and notification_data["config"]:
        notification_data["config"] = json.dumps(notification_data["config"])
    else:
        notification_data["config"] = "{}"
    
    # created_at ve updated_at alanlarını ayarla
    notification_data["created_at"] = datetime.now().isoformat()
    notification_data["updated_at"] = datetime.now().isoformat()
    
    # Boolean değerleri 0/1 olarak dönüştür
    if "is_active" in notification_data:
        notification_data["is_active"] = 1 if notification_data["is_active"] else 0
    
    return db.insert("notifications", notification_data)

async def update_notification(notification_id: int, notification_data: Dict[str, Any]) -> bool:
    """
    Bir bildirimi günceller
    """
    # Config alanını JSON olarak dönüştür
    if "config" in notification_data and notification_data["config"]:
        notification_data["config"] = json.dumps(notification_data["config"])
    
    # updated_at alanını güncelle
    notification_data["updated_at"] = datetime.now().isoformat()
    
    # Boolean değerleri 0/1 olarak dönüştür
    if "is_active" in notification_data:
        notification_data["is_active"] = 1 if notification_data["is_active"] else 0
    
    rows_affected = db.update("notifications", notification_data, "id = ?", [notification_id])
    return rows_affected > 0

async def delete_notification(notification_id: int) -> bool:
    """
    Bir bildirimi siler
    """
    rows_affected = db.delete("notifications", "id = ?", [notification_id])
    return rows_affected > 0


# Monitor-Notification ilişki işlemleri
async def link_monitor_notification(monitor_id: int, notification_id: int) -> bool:
    """
    Bir monitör ile bir bildirimi ilişkilendirir
    """
    try:
        db.insert("monitor_notifications", {
            "monitor_id": monitor_id,
            "notification_id": notification_id,
            "created_at": datetime.now().isoformat()
        })
        return True
    except Exception as e:
        logger.error(f"Error linking monitor and notification: {e}")
        return False

async def unlink_monitor_notification(monitor_id: int, notification_id: int) -> bool:
    """
    Bir monitör ile bir bildirim arasındaki ilişkiyi kaldırır
    """
    rows_affected = db.delete(
        "monitor_notifications",
        "monitor_id = ? AND notification_id = ?",
        [monitor_id, notification_id]
    )
    return rows_affected > 0

async def get_monitor_notifications(monitor_id: int) -> List[Notification]:
    """
    Bir monitöre bağlı tüm bildirimleri döndürür
    """
    rows = db.fetch_all("""
        SELECT n.* FROM notifications n
        JOIN monitor_notifications mn ON n.id = mn.notification_id
        WHERE mn.monitor_id = ? AND n.is_active = 1
    """, [monitor_id])
    
    notifications = []
    for row in rows:
        notification = dict(row)
        
        # JSON formatındaki config alanını dönüştür
        if notification["config"]:
            notification["config"] = json.loads(notification["config"])
        else:
            notification["config"] = {}
        
        # Boolean değerleri dönüştür
        notification["is_active"] = bool(notification["is_active"])
        
        notifications.append(Notification(**notification))
    
    return notifications


# Job işlemleri
async def get_jobs(filters: Dict[str, Any] = None, limit: int = 100, offset: int = 0) -> List[Job]:
    """
    İş ilanlarını döndürür
    """
    query = "SELECT * FROM jobs"
    params = []
    
    # Filtreleri ekle
    if filters:
        conditions = []
        for key, value in filters.items():
            if value is not None:
                if key == "company":
                    conditions.append("company LIKE ?")
                    params.append(f"%{value}%")
                elif key == "location":
                    conditions.append("location LIKE ?")
                    params.append(f"%{value}%")
                elif key == "is_remote":
                    conditions.append("is_remote = ?")
                    params.append(1 if value else 0)
                elif key == "website_id":
                    conditions.append("website_id = ?")
                    params.append(value)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
    
    # Sıralama ve limit ekle
    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    rows = db.fetch_all(query, params)
    
    jobs = []
    for row in rows:
        job = dict(row)
        
        # JSON formatındaki alanları dönüştür
        if job["tags"]:
            job["tags"] = json.loads(job["tags"])
        else:
            job["tags"] = []
        
        if job["raw_data"]:
            job["raw_data"] = json.loads(job["raw_data"])
        else:
            job["raw_data"] = None
        
        # Boolean değerleri dönüştür
        job["is_remote"] = bool(job["is_remote"])
        
        jobs.append(Job(**job))
    
    return jobs

async def get_job(job_id: int) -> Optional[Job]:
    """
    Belirli bir iş ilanını ID'sine göre döndürür
    """
    row = db.fetch_one("SELECT * FROM jobs WHERE id = ?", [job_id])
    if not row:
        return None
    
    job = dict(row)
    
    # JSON formatındaki alanları dönüştür
    if job["tags"]:
        job["tags"] = json.loads(job["tags"])
    else:
        job["tags"] = []
    
    if job["raw_data"]:
        job["raw_data"] = json.loads(job["raw_data"])
    else:
        job["raw_data"] = None
    
    # Boolean değerleri dönüştür
    job["is_remote"] = bool(job["is_remote"])
    
    return Job(**job)

async def create_job(job_data: Dict[str, Any]) -> int:
    """
    Yeni bir iş ilanı oluşturur
    """
    # Liste ve JSON alanlarını dönüştür
    if "tags" in job_data and job_data["tags"]:
        job_data["tags"] = json.dumps(job_data["tags"])
    else:
        job_data["tags"] = None
    
    if "raw_data" in job_data and job_data["raw_data"]:
        job_data["raw_data"] = json.dumps(job_data["raw_data"])
    else:
        job_data["raw_data"] = None
    
    # created_at ve updated_at alanlarını ayarla
    job_data["created_at"] = datetime.now().isoformat()
    job_data["updated_at"] = datetime.now().isoformat()
    
    # Boolean değerleri 0/1 olarak dönüştür
    if "is_remote" in job_data:
        job_data["is_remote"] = 1 if job_data["is_remote"] else 0
    
    try:
        return db.insert("jobs", job_data)
    except sqlite3.IntegrityError:
        # URL benzersiz olmadığında hata oluşabilir
        logger.warning(f"Job with URL {job_data.get('url')} already exists")
        return 0

async def delete_job(job_id: int) -> bool:
    """
    Bir iş ilanını siler
    """
    rows_affected = db.delete("jobs", "id = ?", [job_id])
    return rows_affected > 0


# ChangeLog işlemleri
async def create_change_log(change_log_data: Dict[str, Any]) -> int:
    """
    Yeni bir değişiklik kaydı oluşturur
    """
    # JSON alanlarını dönüştür
    if "old_data" in change_log_data and change_log_data["old_data"]:
        change_log_data["old_data"] = json.dumps(change_log_data["old_data"])
    else:
        change_log_data["old_data"] = None
    
    if "new_data" in change_log_data and change_log_data["new_data"]:
        change_log_data["new_data"] = json.dumps(change_log_data["new_data"])
    else:
        change_log_data["new_data"] = None
    
    # created_at ve updated_at alanlarını ayarla
    change_log_data["created_at"] = datetime.now().isoformat()
    change_log_data["updated_at"] = datetime.now().isoformat()
    
    # Boolean değerleri 0/1 olarak dönüştür
    if "is_notified" in change_log_data:
        change_log_data["is_notified"] = 1 if change_log_data["is_notified"] else 0
    
    return db.insert("change_logs", change_log_data)

async def get_change_logs(monitor_id: Optional[int] = None, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    """
    Değişiklik kayıtlarını döndürür
    """
    query = "SELECT cl.*, j.title, j.company, j.url FROM change_logs cl JOIN jobs j ON cl.job_id = j.id"
    params = []
    
    if monitor_id:
        query += " WHERE cl.monitor_id = ?"
        params.append(monitor_id)
    
    query += " ORDER BY cl.created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    rows = db.fetch_all(query, params)
    
    change_logs = []
    for row in rows:
        change_log = dict(row)
        
        # JSON formatındaki alanları dönüştür
        if change_log["old_data"]:
            change_log["old_data"] = json.loads(change_log["old_data"])
        else:
            change_log["old_data"] = None
        
        if change_log["new_data"]:
            change_log["new_data"] = json.loads(change_log["new_data"])
        else:
            change_log["new_data"] = None
        
        # Boolean değerleri dönüştür
        change_log["is_notified"] = bool(change_log["is_notified"])
        
        change_logs.append(change_log)
    
    return change_logs

def test_connection():
    """
    MongoDB bağlantısını test eder.
    """
    try:
        client = MongoClient(MONGODB_URL)
        client.admin.command('ping')
        logger.info("MongoDB connection successful!")
        return True
    except Exception as e:
        logger.error(f"MongoDB connection failed: {str(e)}")
        return False

# Collections
users = db.users
jobs = db.jobs
profiles = db.profiles
notifications = db.notifications
ads = db.ads
support_tickets = db.support_tickets

# Async collections
async_users = async_db.users
async_jobs = async_db.jobs
async_profiles = async_db.profiles
async_notifications = async_db.notifications
async_ads = async_db.ads
async_support_tickets = async_db.support_tickets 