from ..models.user import User
from ..models.job import Job
from datetime import datetime, timedelta
from typing import List

def send_daily_notifications(db):
    """
    Premium kullanıcılara günlük bildirimler gönderir.
    """
    premium_users = db.find({"subscription_type": "premium"})
    new_jobs = db.find({"created_at": {"$gte": datetime.now() - timedelta(days=1)}})
    
    for user in premium_users:
        # Kullanıcıya bildirim gönder
        send_notification(user, new_jobs)

def send_notification(user: dict, jobs: List[dict]):
    """
    Kullanıcıya bildirim gönderir.
    """
    # Bildirim gönderme işlemi burada yapılacak
    pass 