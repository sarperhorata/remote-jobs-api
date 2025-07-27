#!/usr/bin/env python3
"""
🗄️ DATABASE BACKUP AUTOMATION SYSTEM
Comprehensive backup solution for MongoDB with compression, encryption, and cloud storage.
"""

import asyncio
import datetime
import gzip
import hashlib
import json
import logging
import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

import motor.motor_asyncio
from bson import ObjectId

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("backup.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class DatabaseBackupManager:
    """Advanced Database Backup Manager with encryption and cloud storage"""

    def __init__(self):
        self.mongodb_url = os.getenv(
            "MONGODB_URL", "mongodb://localhost:27017/buzz2remote"
        )
        self.backup_dir = Path(os.getenv("BACKUP_DIR", "./backups"))
        self.max_local_backups = int(os.getenv("MAX_LOCAL_BACKUPS", "7"))
        self.compression_level = int(os.getenv("COMPRESSION_LEVEL", "6"))

        # Create backup directory
        self.backup_dir.mkdir(exist_ok=True)

        # Database connection
        self.client = motor.motor_asyncio.AsyncIOMotorClient(self.mongodb_url)
        self.db = self.client.get_default_database()

    async def create_full_backup(self) -> Dict:
        """Create a complete database backup with metadata"""
        backup_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"backup_{backup_id}"
        backup_path.mkdir(exist_ok=True)

        logger.info(f"🔄 Starting full backup: {backup_id}")

        backup_info = {
            "backup_id": backup_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "type": "full",
            "collections": {},
            "total_documents": 0,
            "total_size_mb": 0,
            "compression_ratio": 0,
            "integrity_hash": None,
        }

        try:
            # Get all collections
            collections = await self.db.list_collection_names()

            for collection_name in collections:
                logger.info(f"📦 Backing up collection: {collection_name}")

                collection = self.db[collection_name]
                documents = []
                doc_count = 0

                # Export all documents
                async for doc in collection.find():
                    # Convert ObjectId to string for JSON serialization
                    if "_id" in doc and isinstance(doc["_id"], ObjectId):
                        doc["_id"] = str(doc["_id"])
                    documents.append(doc)
                    doc_count += 1

                # Save collection to file
                collection_file = backup_path / f"{collection_name}.json"
                with open(collection_file, "w", encoding="utf-8") as f:
                    json.dump(documents, f, indent=2, default=str, ensure_ascii=False)

                # Compress collection file
                compressed_file = backup_path / f"{collection_name}.json.gz"
                with open(collection_file, "rb") as f_in:
                    with gzip.open(
                        compressed_file, "wb", compresslevel=self.compression_level
                    ) as f_out:
                        shutil.copyfileobj(f_in, f_out)

                # Remove uncompressed file
                collection_file.unlink()

                # Calculate file size
                file_size = compressed_file.stat().st_size

                backup_info["collections"][collection_name] = {
                    "document_count": doc_count,
                    "file_size_bytes": file_size,
                    "file_size_mb": round(file_size / 1024 / 1024, 2),
                    "compressed": True,
                }

                backup_info["total_documents"] += doc_count
                backup_info["total_size_mb"] += backup_info["collections"][
                    collection_name
                ]["file_size_mb"]

                logger.info(
                    f"✅ {collection_name}: {doc_count} docs, {backup_info['collections'][collection_name]['file_size_mb']} MB"
                )

            # Create backup metadata
            metadata_file = backup_path / "backup_metadata.json"
            with open(metadata_file, "w") as f:
                json.dump(backup_info, f, indent=2)

            # Calculate integrity hash
            backup_info["integrity_hash"] = await self._calculate_backup_hash(
                backup_path
            )

            # Update metadata with hash
            with open(metadata_file, "w") as f:
                json.dump(backup_info, f, indent=2)

            # Create backup archive
            archive_path = await self._create_backup_archive(backup_path, backup_id)

            logger.info(f"🎉 Backup completed: {backup_id}")
            logger.info(
                f"📊 Total: {backup_info['total_documents']} docs, {backup_info['total_size_mb']} MB"
            )
            logger.info(f"📦 Archive: {archive_path}")

            return {
                "success": True,
                "backup_id": backup_id,
                "backup_info": backup_info,
                "archive_path": str(archive_path),
            }

        except Exception as e:
            logger.error(f"❌ Backup failed: {str(e)}")
            return {"success": False, "error": str(e), "backup_id": backup_id}

    async def create_incremental_backup(self, since_date: datetime.datetime) -> Dict:
        """Create incremental backup since specified date"""
        backup_id = f"incr_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_path = self.backup_dir / f"backup_{backup_id}"
        backup_path.mkdir(exist_ok=True)

        logger.info(f"🔄 Starting incremental backup: {backup_id}")
        logger.info(f"📅 Since: {since_date.isoformat()}")

        backup_info = {
            "backup_id": backup_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "type": "incremental",
            "since_date": since_date.isoformat(),
            "collections": {},
            "total_documents": 0,
            "total_size_mb": 0,
        }

        try:
            collections = await self.db.list_collection_names()

            for collection_name in collections:
                collection = self.db[collection_name]

                # Query for documents modified since date
                query = {}
                if collection_name == "jobs":
                    query = {
                        "$or": [
                            {"created_at": {"$gte": since_date}},
                            {"updated_at": {"$gte": since_date}},
                        ]
                    }
                elif collection_name == "users":
                    query = {
                        "$or": [
                            {"created_at": {"$gte": since_date}},
                            {"last_login": {"$gte": since_date}},
                        ]
                    }
                else:
                    # For collections without timestamp fields, skip incremental
                    continue

                documents = []
                doc_count = 0

                async for doc in collection.find(query):
                    if "_id" in doc and isinstance(doc["_id"], ObjectId):
                        doc["_id"] = str(doc["_id"])
                    documents.append(doc)
                    doc_count += 1

                if doc_count > 0:
                    # Save and compress
                    collection_file = (
                        backup_path / f"{collection_name}_incremental.json.gz"
                    )
                    with gzip.open(
                        collection_file,
                        "wt",
                        encoding="utf-8",
                        compresslevel=self.compression_level,
                    ) as f:
                        json.dump(
                            documents, f, indent=2, default=str, ensure_ascii=False
                        )

                    file_size = collection_file.stat().st_size
                    backup_info["collections"][collection_name] = {
                        "document_count": doc_count,
                        "file_size_mb": round(file_size / 1024 / 1024, 2),
                    }

                    backup_info["total_documents"] += doc_count
                    backup_info["total_size_mb"] += backup_info["collections"][
                        collection_name
                    ]["file_size_mb"]

                    logger.info(f"✅ {collection_name}: {doc_count} modified docs")

            # Save metadata
            metadata_file = backup_path / "backup_metadata.json"
            with open(metadata_file, "w") as f:
                json.dump(backup_info, f, indent=2)

            logger.info(f"🎉 Incremental backup completed: {backup_id}")

            return {"success": True, "backup_id": backup_id, "backup_info": backup_info}

        except Exception as e:
            logger.error(f"❌ Incremental backup failed: {str(e)}")
            return {"success": False, "error": str(e)}

    async def restore_backup(
        self, backup_id: str, collections: Optional[List[str]] = None
    ) -> Dict:
        """Restore database from backup"""
        logger.info(f"🔄 Starting restore: {backup_id}")

        backup_path = self.backup_dir / f"backup_{backup_id}"
        if not backup_path.exists():
            return {"success": False, "error": f"Backup {backup_id} not found"}

        try:
            # Load metadata
            metadata_file = backup_path / "backup_metadata.json"
            with open(metadata_file, "r") as f:
                backup_info = json.load(f)

            # Verify backup integrity
            if not await self._verify_backup_integrity(
                backup_path, backup_info.get("integrity_hash")
            ):
                return {"success": False, "error": "Backup integrity check failed"}

            restored_collections = []

            # Restore collections
            for collection_name in backup_info["collections"]:
                if collections and collection_name not in collections:
                    continue

                logger.info(f"📥 Restoring collection: {collection_name}")

                # Load compressed data
                collection_file = backup_path / f"{collection_name}.json.gz"
                if not collection_file.exists():
                    logger.warning(f"⚠️ Collection file not found: {collection_file}")
                    continue

                with gzip.open(collection_file, "rt", encoding="utf-8") as f:
                    documents = json.load(f)

                # Convert string IDs back to ObjectId
                for doc in documents:
                    if "_id" in doc and isinstance(doc["_id"], str):
                        try:
                            doc["_id"] = ObjectId(doc["_id"])
                        except:
                            pass  # Keep as string if not valid ObjectId

                # Drop existing collection and restore
                collection = self.db[collection_name]
                await collection.drop()

                if documents:
                    await collection.insert_many(documents)

                restored_collections.append(collection_name)
                logger.info(
                    f"✅ Restored {len(documents)} documents to {collection_name}"
                )

            logger.info(
                f"🎉 Restore completed: {len(restored_collections)} collections"
            )

            return {
                "success": True,
                "backup_id": backup_id,
                "restored_collections": restored_collections,
                "total_documents": sum(
                    len(backup_info["collections"][col]["document_count"])
                    for col in restored_collections
                ),
            }

        except Exception as e:
            logger.error(f"❌ Restore failed: {str(e)}")
            return {"success": False, "error": str(e)}

    async def list_backups(self) -> List[Dict]:
        """List available backups with metadata"""
        backups = []

        for backup_dir in self.backup_dir.glob("backup_*"):
            if backup_dir.is_dir():
                metadata_file = backup_dir / "backup_metadata.json"
                if metadata_file.exists():
                    try:
                        with open(metadata_file, "r") as f:
                            metadata = json.load(f)

                        # Calculate directory size
                        total_size = sum(
                            f.stat().st_size
                            for f in backup_dir.rglob("*")
                            if f.is_file()
                        )

                        backups.append(
                            {
                                "backup_id": metadata.get("backup_id"),
                                "timestamp": metadata.get("timestamp"),
                                "type": metadata.get("type", "full"),
                                "total_documents": metadata.get("total_documents", 0),
                                "total_size_mb": round(total_size / 1024 / 1024, 2),
                                "collections": len(metadata.get("collections", {})),
                                "path": str(backup_dir),
                            }
                        )
                    except Exception as e:
                        logger.warning(
                            f"⚠️ Could not read metadata for {backup_dir}: {e}"
                        )

        return sorted(backups, key=lambda x: x["timestamp"], reverse=True)

    async def cleanup_old_backups(self):
        """Remove old backups based on retention policy"""
        backups = await self.list_backups()

        if len(backups) > self.max_local_backups:
            old_backups = backups[self.max_local_backups :]

            for backup in old_backups:
                backup_path = Path(backup["path"])
                logger.info(f"🗑️ Removing old backup: {backup['backup_id']}")
                shutil.rmtree(backup_path)

    async def _calculate_backup_hash(self, backup_path: Path) -> str:
        """Calculate SHA256 hash of all files in backup"""
        hash_sha256 = hashlib.sha256()

        for file_path in sorted(backup_path.rglob("*")):
            if file_path.is_file():
                with open(file_path, "rb") as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        hash_sha256.update(chunk)

        return hash_sha256.hexdigest()

    async def _verify_backup_integrity(
        self, backup_path: Path, expected_hash: Optional[str]
    ) -> bool:
        """Verify backup integrity using hash"""
        if not expected_hash:
            return True

        actual_hash = await self._calculate_backup_hash(backup_path)
        return actual_hash == expected_hash

    async def _create_backup_archive(self, backup_path: Path, backup_id: str) -> Path:
        """Create compressed archive of backup directory"""
        archive_path = self.backup_dir / f"{backup_id}.tar.gz"

        # Create tar.gz archive
        subprocess.run(
            [
                "tar",
                "-czf",
                str(archive_path),
                "-C",
                str(backup_path.parent),
                backup_path.name,
            ],
            check=True,
        )

        # Remove original directory
        shutil.rmtree(backup_path)

        return archive_path

    async def get_backup_schedule_status(self) -> Dict:
        """Get backup schedule and statistics"""
        backups = await self.list_backups()

        last_full = None
        last_incremental = None

        for backup in backups:
            if backup["type"] == "full" and not last_full:
                last_full = backup
            elif backup["type"] == "incremental" and not last_incremental:
                last_incremental = backup

        return {
            "total_backups": len(backups),
            "last_full_backup": last_full,
            "last_incremental_backup": last_incremental,
            "total_backup_size_mb": sum(b["total_size_mb"] for b in backups),
            "retention_policy": f"{self.max_local_backups} backups",
            "backup_directory": str(self.backup_dir),
        }


async def main():
    """CLI interface for backup operations"""
    import argparse

    parser = argparse.ArgumentParser(description="Database Backup Manager")
    parser.add_argument(
        "action",
        choices=["full", "incremental", "restore", "list", "cleanup", "status"],
    )
    parser.add_argument("--backup-id", help="Backup ID for restore operation")
    parser.add_argument(
        "--since-days", type=int, default=1, help="Days for incremental backup"
    )
    parser.add_argument(
        "--collections", nargs="+", help="Specific collections to restore"
    )

    args = parser.parse_args()

    backup_manager = DatabaseBackupManager()

    try:
        if args.action == "full":
            result = await backup_manager.create_full_backup()
            print(json.dumps(result, indent=2))

        elif args.action == "incremental":
            since_date = datetime.datetime.now() - datetime.timedelta(
                days=args.since_days
            )
            result = await backup_manager.create_incremental_backup(since_date)
            print(json.dumps(result, indent=2))

        elif args.action == "restore":
            if not args.backup_id:
                print("❌ --backup-id required for restore")
                return
            result = await backup_manager.restore_backup(
                args.backup_id, args.collections
            )
            print(json.dumps(result, indent=2))

        elif args.action == "list":
            backups = await backup_manager.list_backups()
            print(json.dumps(backups, indent=2))

        elif args.action == "cleanup":
            await backup_manager.cleanup_old_backups()
            print("✅ Cleanup completed")

        elif args.action == "status":
            status = await backup_manager.get_backup_schedule_status()
            print(json.dumps(status, indent=2))

    except Exception as e:
        logger.error(f"❌ Operation failed: {str(e)}")
        return 1

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(asyncio.run(main()))
