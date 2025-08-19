from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List, Optional
import time
import psutil
import os
from datetime import datetime, timedelta

# from middleware.performance_middleware import db_performance, cache_performance
try:
    from backend.config.sentry_config import capture_message, set_tag
except ImportError:
    # Mock functions if sentry config is not available
    def capture_message(message, level="info", context=None):
        pass
    def set_tag(key, value):
        pass
from backend.core.security import get_current_user
from backend.models.user import UserResponse as User

router = APIRouter(prefix="/api/performance", tags=["performance"])

# Performans metriklerini saklamak için basit cache
performance_cache = {
    "api_metrics": [],
    "db_metrics": [],
    "system_metrics": [],
    "last_update": None
}

@router.get("/metrics")
async def get_performance_metrics(
    current_user: Optional[User] = Depends(get_current_user)
):
    """Performans metriklerini döndür"""
    
    try:
        # Sistem metriklerini al
        system_metrics = get_system_metrics()
        
        # API metriklerini hesapla
        api_metrics = calculate_api_metrics()
        
        # Database metriklerini hesapla
        db_metrics = calculate_db_metrics()
        
        # Uptime hesapla
        uptime = calculate_uptime()
        
        # Hata oranını hesapla
        error_rate = calculate_error_rate()
        
        # Server durumunu belirle
        server_status = determine_server_status(system_metrics, api_metrics, db_metrics)
        
        metrics = {
            "pageLoadTime": api_metrics.get("avg_response_time", 0) * 1000,  # ms'ye çevir
            "apiResponseTime": api_metrics.get("avg_response_time", 0) * 1000,
            "uptime": uptime,
            "errorRate": error_rate,
            "activeUsers": estimate_active_users(),
            "serverStatus": server_status,
            "lastUpdated": datetime.now().isoformat(),
            "system": system_metrics,
            "api": api_metrics,
            "database": db_metrics
        }
        
        # Sentry'ye gönder
        capture_message("Performance metrics retrieved", level="info", context={
            "metrics": metrics,
            "user_id": current_user.id if current_user else None
        })
        
        return metrics
        
    except Exception as e:
        capture_message(f"Error getting performance metrics: {str(e)}", level="error")
        raise HTTPException(status_code=500, detail="Failed to get performance metrics")

@router.get("/health")
async def health_check():
    """Sistem sağlık kontrolü"""
    
    try:
        system_metrics = get_system_metrics()
        
        # Kritik eşikler
        critical_thresholds = {
            "cpu_usage": 90,
            "memory_usage": 90,
            "disk_usage": 95,
        }
        
        health_status = "healthy"
        issues = []
        
        # CPU kontrolü
        if system_metrics["cpu_usage"] > critical_thresholds["cpu_usage"]:
            health_status = "warning"
            issues.append(f"High CPU usage: {system_metrics['cpu_usage']:.1f}%")
        
        # Memory kontrolü
        if system_metrics["memory_usage"] > critical_thresholds["memory_usage"]:
            health_status = "warning"
            issues.append(f"High memory usage: {system_metrics['memory_usage']:.1f}%")
        
        # Disk kontrolü
        if system_metrics["disk_usage"] > critical_thresholds["disk_usage"]:
            health_status = "critical"
            issues.append(f"Critical disk usage: {system_metrics['disk_usage']:.1f}%")
        
        return {
            "status": health_status,
            "timestamp": datetime.now().isoformat(),
            "metrics": system_metrics,
            "issues": issues
        }
        
    except Exception as e:
        capture_message(f"Health check failed: {str(e)}", level="error")
        return {
            "status": "error",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

def get_system_metrics() -> Dict:
    """Sistem metriklerini al"""
    
    try:
        # CPU kullanımı
        cpu_usage = psutil.cpu_percent(interval=1)
        
        # Memory kullanımı
        memory = psutil.virtual_memory()
        memory_usage = memory.percent
        
        # Disk kullanımı
        disk = psutil.disk_usage('/')
        disk_usage = (disk.used / disk.total) * 100
        
        # Network I/O
        network = psutil.net_io_counters()
        
        # Process sayısı
        process_count = len(psutil.pids())
        
        return {
            "cpu_usage": cpu_usage,
            "memory_usage": memory_usage,
            "memory_available": memory.available / (1024**3),  # GB
            "disk_usage": disk_usage,
            "disk_free": disk.free / (1024**3),  # GB
            "network_bytes_sent": network.bytes_sent,
            "network_bytes_recv": network.bytes_recv,
            "process_count": process_count,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        capture_message(f"Error getting system metrics: {str(e)}", level="error")
        return {
            "cpu_usage": 0,
            "memory_usage": 0,
            "memory_available": 0,
            "disk_usage": 0,
            "disk_free": 0,
            "network_bytes_sent": 0,
            "network_bytes_recv": 0,
            "process_count": 0,
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

def calculate_api_metrics() -> Dict:
    """API metriklerini hesapla"""
    
    # Gerçek implementasyonda bu veriler monitoring sisteminden gelecek
    # Şimdilik mock data döndürüyoruz
    
    return {
        "avg_response_time": 0.15,  # 150ms
        "total_requests": 1250,
        "successful_requests": 1230,
        "failed_requests": 20,
        "requests_per_minute": 45,
        "slow_requests": 5,  # >1s
        "critical_requests": 1,  # >5s
        "timestamp": datetime.now().isoformat()
    }

def calculate_db_metrics() -> Dict:
    """Database metriklerini hesapla"""
    
    # Gerçek implementasyonda bu veriler database monitoring'den gelecek
    
    return {
        "avg_query_time": 0.05,  # 50ms
        "total_queries": 850,
        "slow_queries": 12,  # >500ms
        "critical_queries": 2,  # >2s
        "connection_pool_size": 20,
        "active_connections": 8,
        "cache_hit_rate": 0.85,  # %85
        "timestamp": datetime.now().isoformat()
    }

def calculate_uptime() -> float:
    """Uptime hesapla"""
    
    try:
        # Sistem başlangıç zamanından itibaren geçen süre
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime_seconds = (datetime.now() - boot_time).total_seconds()
        
        # Uptime yüzdesi (basit hesaplama)
        # Gerçek implementasyonda monitoring sisteminden gelecek
        return 99.95  # %99.95
        
    except Exception as e:
        capture_message(f"Error calculating uptime: {str(e)}", level="error")
        return 99.0

def calculate_error_rate() -> float:
    """Hata oranını hesapla"""
    
    # API metriklerinden hata oranını hesapla
    api_metrics = calculate_api_metrics()
    
    if api_metrics["total_requests"] == 0:
        return 0.0
    
    error_rate = (api_metrics["failed_requests"] / api_metrics["total_requests"]) * 100
    return round(error_rate, 3)

def determine_server_status(
    system_metrics: Dict,
    api_metrics: Dict,
    db_metrics: Dict
) -> str:
    """Server durumunu belirle"""
    
    # Kritik eşikler
    if (system_metrics["cpu_usage"] > 90 or 
        system_metrics["memory_usage"] > 90 or
        system_metrics["disk_usage"] > 95 or
        api_metrics["critical_requests"] > 0 or
        db_metrics["critical_queries"] > 0):
        return "error"
    
    # Warning eşikleri
    if (system_metrics["cpu_usage"] > 70 or
        system_metrics["memory_usage"] > 70 or
        system_metrics["disk_usage"] > 80 or
        api_metrics["slow_requests"] > 10 or
        db_metrics["slow_queries"] > 20):
        return "warning"
    
    return "healthy"

def estimate_active_users() -> int:
    """Aktif kullanıcı sayısını tahmin et"""
    
    # Gerçek implementasyonda analytics sisteminden gelecek
    # Şimdilik basit bir tahmin
    
    base_users = 500
    time_factor = datetime.now().hour / 24.0  # Günün saati
    activity_multiplier = 0.5 + (time_factor * 0.5)  # 0.5-1.0 arası
    
    return int(base_users * activity_multiplier)

@router.post("/track")
async def track_performance_event(
    event_type: str,
    event_data: Dict,
    current_user: Optional[User] = Depends(get_current_user)
):
    """Performans event'ini kaydet"""
    
    try:
        # Event'i Sentry'ye gönder
        capture_message(
            f"Performance event: {event_type}",
            level="info",
            context={
                "event_type": event_type,
                "event_data": event_data,
                "user_id": current_user.id if current_user else None
            }
        )
        
        # Event'i cache'e kaydet
        performance_cache["api_metrics"].append({
            "type": event_type,
            "data": event_data,
            "timestamp": datetime.now().isoformat(),
            "user_id": current_user.id if current_user else None
        })
        
        # Cache boyutunu sınırla
        if len(performance_cache["api_metrics"]) > 1000:
            performance_cache["api_metrics"] = performance_cache["api_metrics"][-500:]
        
        return {"status": "success", "message": "Event tracked successfully"}
        
    except Exception as e:
        capture_message(f"Error tracking performance event: {str(e)}", level="error")
        raise HTTPException(status_code=500, detail="Failed to track event") 