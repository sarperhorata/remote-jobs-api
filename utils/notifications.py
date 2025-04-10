from ..models.user import User
from ..models.job import Job
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List

def send_daily_notifications(db: Session):
    """
    Premium kullanıcılara günlük bildirimler gönderir.
    """
    premium_users = db.query(User).filter(User.subscription_type == "premium").all()
    new_jobs = db.query(Job).filter(Job.created_at >= datetime.now() - timedelta(days=1)).all()
    
    for user in premium_users:
        # Kullanıcıya bildirim gönder
        send_notification(user, new_jobs)

def send_notification(user: User, jobs: List[Job]):
    """
    Kullanıcıya bildirim gönderir.
    """
    # Bildirim gönderme işlemi burada yapılacak
    pass 