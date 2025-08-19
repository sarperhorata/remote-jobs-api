"""
Rate Limiting Utilities
API rate limiting için yardımcı fonksiyonlar
"""

import asyncio
import time
import logging
from typing import Dict, Tuple, Optional
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)

# Rate limit storage
_rate_limit_storage: Dict[str, Dict[str, list]] = defaultdict(lambda: defaultdict(list))

class RateLimitExceeded(Exception):
    """Rate limit aşıldığında fırlatılan exception"""
    pass

async def check_rate_limit(
    user_id: str,
    action: str,
    max_requests: int,
    window_seconds: int
) -> bool:
    """
    Rate limit kontrolü yapar
    
    Args:
        user_id: Kullanıcı ID'si
        action: Eylem türü (örn: 'form_analysis', 'bulk_apply')
        max_requests: Maksimum istek sayısı
        window_seconds: Zaman penceresi (saniye)
    
    Returns:
        bool: Rate limit aşılmadıysa True
    
    Raises:
        RateLimitExceeded: Rate limit aşıldığında
    """
    try:
        current_time = time.time()
        key = f"{user_id}:{action}"
        
        # Eski kayıtları temizle
        _rate_limit_storage[user_id][action] = [
            timestamp for timestamp in _rate_limit_storage[user_id][action]
            if current_time - timestamp < window_seconds
        ]
        
        # Mevcut istek sayısını kontrol et
        current_requests = len(_rate_limit_storage[user_id][action])
        
        if current_requests >= max_requests:
            # En eski isteğin ne zaman yapıldığını hesapla
            oldest_request = min(_rate_limit_storage[user_id][action])
            wait_time = window_seconds - (current_time - oldest_request)
            
            logger.warning(
                f"Rate limit exceeded for user {user_id}, action {action}: "
                f"{current_requests}/{max_requests} requests in {window_seconds}s window. "
                f"Wait {wait_time:.1f}s"
            )
            
            raise RateLimitExceeded(
                f"Rate limit exceeded. Maximum {max_requests} requests per {window_seconds} seconds. "
                f"Try again in {wait_time:.1f} seconds."
            )
        
        # Yeni isteği kaydet
        _rate_limit_storage[user_id][action].append(current_time)
        
        logger.debug(
            f"Rate limit check passed for user {user_id}, action {action}: "
            f"{current_requests + 1}/{max_requests} requests"
        )
        
        return True
        
    except Exception as e:
        logger.error(f"Rate limit check error: {str(e)}")
        raise

def get_rate_limit_status(
    user_id: str,
    action: str
) -> Dict[str, any]:
    """
    Rate limit durumunu döner
    
    Args:
        user_id: Kullanıcı ID'si
        action: Eylem türü
    
    Returns:
        Dict: Rate limit durumu
    """
    try:
        current_time = time.time()
        requests = _rate_limit_storage[user_id][action]
        
        # Son 1 dakikadaki istekleri filtrele
        recent_requests = [
            timestamp for timestamp in requests
            if current_time - timestamp < 60
        ]
        
        return {
            "user_id": user_id,
            "action": action,
            "current_requests": len(recent_requests),
            "total_requests": len(requests),
            "last_request": max(requests) if requests else None,
            "first_request": min(requests) if requests else None
        }
        
    except Exception as e:
        logger.error(f"Rate limit status error: {str(e)}")
        return {
            "user_id": user_id,
            "action": action,
            "error": str(e)
        }

def reset_rate_limit(
    user_id: str,
    action: Optional[str] = None
) -> bool:
    """
    Rate limit kayıtlarını sıfırlar
    
    Args:
        user_id: Kullanıcı ID'si
        action: Eylem türü (None ise tüm eylemler)
    
    Returns:
        bool: Başarılı ise True
    """
    try:
        if action:
            _rate_limit_storage[user_id][action].clear()
            logger.info(f"Rate limit reset for user {user_id}, action {action}")
        else:
            _rate_limit_storage[user_id].clear()
            logger.info(f"Rate limit reset for user {user_id}, all actions")
        
        return True
        
    except Exception as e:
        logger.error(f"Rate limit reset error: {str(e)}")
        return False

def cleanup_old_rate_limits(
    max_age_hours: int = 24
) -> int:
    """
    Eski rate limit kayıtlarını temizler
    
    Args:
        max_age_hours: Maksimum yaş (saat)
    
    Returns:
        int: Temizlenen kayıt sayısı
    """
    try:
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        cleaned_count = 0
        
        for user_id in list(_rate_limit_storage.keys()):
            for action in list(_rate_limit_storage[user_id].keys()):
                # Eski kayıtları filtrele
                old_count = len(_rate_limit_storage[user_id][action])
                _rate_limit_storage[user_id][action] = [
                    timestamp for timestamp in _rate_limit_storage[user_id][action]
                    if current_time - timestamp < max_age_seconds
                ]
                new_count = len(_rate_limit_storage[user_id][action])
                cleaned_count += old_count - new_count
                
                # Boş action'ları sil
                if not _rate_limit_storage[user_id][action]:
                    del _rate_limit_storage[user_id][action]
            
            # Boş user'ları sil
            if not _rate_limit_storage[user_id]:
                del _rate_limit_storage[user_id]
        
        logger.info(f"Cleaned up {cleaned_count} old rate limit records")
        return cleaned_count
        
    except Exception as e:
        logger.error(f"Rate limit cleanup error: {str(e)}")
        return 0

def get_rate_limit_stats() -> Dict[str, any]:
    """
    Rate limit istatistiklerini döner
    
    Returns:
        Dict: İstatistikler
    """
    try:
        total_users = len(_rate_limit_storage)
        total_actions = sum(len(actions) for actions in _rate_limit_storage.values())
        total_requests = sum(
            len(requests) for user_actions in _rate_limit_storage.values()
            for requests in user_actions.values()
        )
        
        return {
            "total_users": total_users,
            "total_actions": total_actions,
            "total_requests": total_requests,
            "average_requests_per_user": total_requests / total_users if total_users > 0 else 0,
            "average_actions_per_user": total_actions / total_users if total_users > 0 else 0
        }
        
    except Exception as e:
        logger.error(f"Rate limit stats error: {str(e)}")
        return {"error": str(e)}

# Rate limit konfigürasyonları
RATE_LIMIT_CONFIGS = {
    "form_analysis": {
        "max_requests": 5,
        "window_seconds": 60,
        "description": "Form analysis requests per minute"
    },
    "form_fill": {
        "max_requests": 10,
        "window_seconds": 60,
        "description": "Form filling requests per minute"
    },
    "form_submit": {
        "max_requests": 5,
        "window_seconds": 60,
        "description": "Form submission requests per minute"
    },
    "bulk_apply": {
        "max_requests": 1,
        "window_seconds": 300,  # 5 dakika
        "description": "Bulk apply requests per 5 minutes"
    },
    "job_search": {
        "max_requests": 20,
        "window_seconds": 60,
        "description": "Job search requests per minute"
    },
    "profile_update": {
        "max_requests": 10,
        "window_seconds": 60,
        "description": "Profile update requests per minute"
    }
}

async def check_rate_limit_with_config(
    user_id: str,
    action: str
) -> bool:
    """
    Konfigürasyondan rate limit kontrolü yapar
    
    Args:
        user_id: Kullanıcı ID'si
        action: Eylem türü
    
    Returns:
        bool: Rate limit aşılmadıysa True
    
    Raises:
        RateLimitExceeded: Rate limit aşıldığında
    """
    if action not in RATE_LIMIT_CONFIGS:
        logger.warning(f"Unknown rate limit action: {action}")
        return True
    
    config = RATE_LIMIT_CONFIGS[action]
    return await check_rate_limit(
        user_id=user_id,
        action=action,
        max_requests=config["max_requests"],
        window_seconds=config["window_seconds"]
    )

def get_rate_limit_config(action: str) -> Optional[Dict[str, any]]:
    """
    Rate limit konfigürasyonunu döner
    
    Args:
        action: Eylem türü
    
    Returns:
        Optional[Dict]: Konfigürasyon
    """
    return RATE_LIMIT_CONFIGS.get(action)

def get_all_rate_limit_configs() -> Dict[str, Dict[str, any]]:
    """
    Tüm rate limit konfigürasyonlarını döner
    
    Returns:
        Dict: Tüm konfigürasyonlar
    """
    return RATE_LIMIT_CONFIGS.copy() 