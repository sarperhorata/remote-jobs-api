"""
🗄️ DATABASE BACKUP API ENDPOINTS
FastAPI routes for backup management and monitoring
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List, Optional, Dict, Any
import asyncio
import datetime
from ..scripts.database_backup import DatabaseBackupManager
from ..core.security import require_api_key

router = APIRouter(prefix="/api/v1/backup", tags=["backup"])

# Global backup manager instance
backup_manager = DatabaseBackupManager()

@router.post("/create/full")
async def create_full_backup(
    background_tasks: BackgroundTasks,
    api_key: str = Depends(require_api_key)
) -> Dict[str, Any]:
    """
    🔄 Create a full database backup
    
    This endpoint creates a complete backup of all collections.
    The operation runs in the background to prevent timeout.
    """
    try:
        # Run backup in background
        result = await backup_manager.create_full_backup()
        
        if result['success']:
            return {
                "status": "success",
                "message": "Full backup completed successfully",
                "backup_id": result['backup_id'],
                "backup_info": result['backup_info']
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Backup failed: {result.get('error', 'Unknown error')}"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Backup operation failed: {str(e)}"
        )

@router.post("/create/incremental")
async def create_incremental_backup(
    since_days: int = 1,
    api_key: str = Depends(require_api_key)
) -> Dict[str, Any]:
    """
    🔄 Create an incremental backup
    
    Creates a backup of documents modified since specified number of days.
    """
    try:
        since_date = datetime.datetime.now() - datetime.timedelta(days=since_days)
        result = await backup_manager.create_incremental_backup(since_date)
        
        if result['success']:
            return {
                "status": "success",
                "message": f"Incremental backup completed (since {since_days} days)",
                "backup_id": result['backup_id'],
                "backup_info": result['backup_info']
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Incremental backup failed: {result.get('error', 'Unknown error')}"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Incremental backup operation failed: {str(e)}"
        )

@router.get("/list")
async def list_backups(
    api_key: str = Depends(require_api_key)
) -> Dict[str, Any]:
    """
    📋 List all available backups
    
    Returns a list of all backups with metadata and statistics.
    """
    try:
        backups = await backup_manager.list_backups()
        status = await backup_manager.get_backup_schedule_status()
        
        return {
            "status": "success",
            "total_backups": len(backups),
            "backups": backups,
            "schedule_status": status
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list backups: {str(e)}"
        )

@router.post("/restore/{backup_id}")
async def restore_backup(
    backup_id: str,
    collections: Optional[List[str]] = None,
    api_key: str = Depends(require_api_key)
) -> Dict[str, Any]:
    """
    📥 Restore database from backup
    
    ⚠️ WARNING: This operation will overwrite existing data!
    
    Parameters:
    - backup_id: ID of the backup to restore
    - collections: Optional list of specific collections to restore
    """
    try:
        result = await backup_manager.restore_backup(backup_id, collections)
        
        if result['success']:
            return {
                "status": "success",
                "message": "Database restored successfully",
                "backup_id": backup_id,
                "restored_collections": result['restored_collections'],
                "total_documents": result.get('total_documents', 0)
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Restore failed: {result.get('error', 'Unknown error')}"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Restore operation failed: {str(e)}"
        )

@router.delete("/cleanup")
async def cleanup_old_backups(
    api_key: str = Depends(require_api_key)
) -> Dict[str, Any]:
    """
    🗑️ Cleanup old backups
    
    Removes old backups based on retention policy.
    """
    try:
        await backup_manager.cleanup_old_backups()
        
        # Get updated backup list
        backups = await backup_manager.list_backups()
        
        return {
            "status": "success",
            "message": "Old backups cleaned up successfully",
            "remaining_backups": len(backups)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Cleanup operation failed: {str(e)}"
        )

@router.get("/status")
async def get_backup_status(
    api_key: str = Depends(require_api_key)
) -> Dict[str, Any]:
    """
    📊 Get backup system status
    
    Returns comprehensive backup system health and statistics.
    """
    try:
        status = await backup_manager.get_backup_schedule_status()
        backups = await backup_manager.list_backups()
        
        # Calculate health metrics
        now = datetime.datetime.now()
        last_backup_age = None
        health_status = "UNKNOWN"
        
        if backups:
            last_backup_time = datetime.datetime.fromisoformat(
                backups[0]['timestamp'].replace('Z', '+00:00').replace('+00:00', '')
            )
            last_backup_age = (now - last_backup_time).total_seconds() / 3600  # hours
            
            if last_backup_age <= 24:
                health_status = "HEALTHY"
            elif last_backup_age <= 48:
                health_status = "WARNING"
            else:
                health_status = "CRITICAL"
        
        return {
            "status": "success",
            "backup_system": {
                "health_status": health_status,
                "last_backup_age_hours": round(last_backup_age, 2) if last_backup_age else None,
                "total_backups": len(backups),
                "total_backup_size_mb": status.get('total_backup_size_mb', 0),
                "retention_policy": status.get('retention_policy'),
                "backup_directory": status.get('backup_directory')
            },
            "recent_backups": backups[:5],  # Last 5 backups
            "schedule_status": status
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get backup status: {str(e)}"
        )

@router.post("/test")
async def test_backup_system(
    api_key: str = Depends(require_api_key)
) -> Dict[str, Any]:
    """
    🧪 Test backup system
    
    Performs a small test backup to verify system functionality.
    """
    try:
        # Create a test backup with limited data
        result = await backup_manager.create_full_backup()
        
        # Clean up test backup immediately
        if result['success']:
            await backup_manager.cleanup_old_backups()
        
        return {
            "status": "success" if result['success'] else "failed",
            "message": "Backup system test completed",
            "test_result": result,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Backup system test failed: {str(e)}"
        ) 