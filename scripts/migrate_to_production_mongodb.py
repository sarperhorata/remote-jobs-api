#!/usr/bin/env python3
"""
MongoDB Migration Script
Local MongoDB'den production MongoDB'ye veri taşıma
"""

import os
import sys
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import logging
from datetime import datetime

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_mongodb_connections():
    """Local ve production MongoDB bağlantılarını al"""
    
    # Local MongoDB
    local_url = "mongodb://localhost:27017/buzz2remote"
    
    # Production MongoDB (environment variable'dan)
    production_url = os.getenv("MONGODB_URL")
    
    if not production_url:
        logger.error("❌ MONGODB_URL environment variable'ı bulunamadı!")
        logger.info("GitHub Repository Variables'a MONGODB_URL ekleyin")
        return None, None
    
    try:
        # Local connection
        local_client = MongoClient(local_url, serverSelectionTimeoutMS=5000)
        local_client.admin.command('ping')
        logger.info("✅ Local MongoDB bağlantısı başarılı")
        
        # Production connection
        prod_client = MongoClient(production_url, serverSelectionTimeoutMS=10000)
        prod_client.admin.command('ping')
        logger.info("✅ Production MongoDB bağlantısı başarılı")
        
        return local_client, prod_client
        
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        logger.error(f"❌ MongoDB bağlantı hatası: {e}")
        return None, None

def migrate_collection(local_db, prod_db, collection_name):
    """Tek bir collection'ı taşı"""
    
    local_collection = local_db[collection_name]
    prod_collection = prod_db[collection_name]
    
    # Mevcut veri sayısını kontrol et
    local_count = local_collection.count_documents({})
    prod_count = prod_collection.count_documents({})
    
    logger.info(f"📊 {collection_name}:")
    logger.info(f"   Local: {local_count} döküman")
    logger.info(f"   Production: {prod_count} döküman")
    
    if local_count == 0:
        logger.warning(f"⚠️ Local {collection_name} collection'ı boş")
        return
    
    if prod_count > 0:
        logger.warning(f"⚠️ Production {collection_name} collection'ında {prod_count} döküman var")
        response = input("Devam etmek istiyor musunuz? (y/N): ")
        if response.lower() != 'y':
            logger.info("❌ Migration iptal edildi")
            return
    
    # Verileri taşı
    logger.info(f"🔄 {collection_name} verileri taşınıyor...")
    
    batch_size = 1000
    total_migrated = 0
    
    for i in range(0, local_count, batch_size):
        batch = list(local_collection.find().skip(i).limit(batch_size))
        
        if batch:
            try:
                # Duplicate key hatalarını önlemek için upsert kullan
                for doc in batch:
                    try:
                        # _id'yi koru ama duplicate key hatalarını önle
                        if '_id' in doc:
                            prod_collection.replace_one(
                                {'_id': doc['_id']}, 
                                doc, 
                                upsert=True
                            )
                        else:
                            # Email gibi unique field'lar için kontrol et
                            if collection_name == 'users' and 'email' in doc:
                                prod_collection.replace_one(
                                    {'email': doc['email']}, 
                                    doc, 
                                    upsert=True
                                )
                            else:
                                prod_collection.insert_one(doc)
                    except Exception as e:
                        # Duplicate key hatalarını logla ama devam et
                        if 'duplicate key' in str(e).lower():
                            logger.warning(f"⚠️ Duplicate key hatası (devam ediliyor): {e}")
                            continue
                        else:
                            raise e
                
                total_migrated += len(batch)
                logger.info(f"   ✅ {total_migrated}/{local_count} döküman taşındı")
                
            except Exception as e:
                logger.error(f"❌ Batch migration hatası: {e}")
                continue
    
    # Son kontrol
    final_count = prod_collection.count_documents({})
    logger.info(f"✅ {collection_name} migration tamamlandı: {final_count} döküman")

def create_indexes(prod_db):
    """Production'da gerekli index'leri oluştur"""
    
    logger.info("🔧 Production index'leri oluşturuluyor...")
    
    try:
        # Jobs collection index'leri
        jobs_collection = prod_db['jobs']
        
        # Title index
        jobs_collection.create_index("title")
        logger.info("   ✅ jobs.title index oluşturuldu")
        
        # Company index
        jobs_collection.create_index("company")
        logger.info("   ✅ jobs.company index oluşturuldu")
        
        # Posted_date index
        jobs_collection.create_index("posted_date")
        logger.info("   ✅ jobs.posted_date index oluşturuldu")
        
        # Text search index
        jobs_collection.create_index([
            ("title", "text"),
            ("description", "text"),
            ("company", "text")
        ])
        logger.info("   ✅ jobs text search index oluşturuldu")
        
        # Users collection index'leri
        users_collection = prod_db['users']
        users_collection.create_index("email", unique=True)
        logger.info("   ✅ users.email unique index oluşturuldu")
        
        logger.info("✅ Tüm index'ler oluşturuldu")
        
    except Exception as e:
        logger.error(f"❌ Index oluşturma hatası: {e}")

def main():
    """Ana migration fonksiyonu"""
    
    logger.info("🚀 MongoDB Migration Başlıyor...")
    logger.info(f"⏰ Başlangıç zamanı: {datetime.now()}")
    
    # Bağlantıları al
    local_client, prod_client = get_mongodb_connections()
    
    if not local_client or not prod_client:
        logger.error("❌ Migration iptal edildi - bağlantı hatası")
        return
    
    try:
        local_db = local_client['buzz2remote']
        prod_db = prod_client['buzz2remote']
        
        # Migration edilecek collection'lar
        collections = ['jobs', 'users', 'companies', 'applications']
        
        for collection in collections:
            try:
                migrate_collection(local_db, prod_db, collection)
            except Exception as e:
                logger.error(f"❌ {collection} migration hatası: {e}")
                continue
        
        # Index'leri oluştur
        create_indexes(prod_db)
        
        logger.info("🎉 Migration tamamlandı!")
        logger.info(f"⏰ Bitiş zamanı: {datetime.now()}")
        
    except Exception as e:
        logger.error(f"❌ Migration hatası: {e}")
    
    finally:
        # Bağlantıları kapat
        if local_client:
            local_client.close()
        if prod_client:
            prod_client.close()
        logger.info("🔒 MongoDB bağlantıları kapatıldı")

if __name__ == "__main__":
    main() 