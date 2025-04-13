from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from ..database import get_db
from ..models.user import User
from ..utils.auth import get_current_active_user
from ..utils.chatbot import get_chatbot_response

router = APIRouter()

@router.post("/chat")
async def chat_with_bot(
    message: str,
    chat_history: List[Dict[str, str]],
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Chatbot ile sohbet etmek için endpoint.
    
    Args:
        message: Kullanıcı mesajı
        chat_history: Sohbet geçmişi
        current_user: Mevcut kullanıcı
        db: Veritabanı oturumu
        
    Returns:
        Dict[str, str]: Chatbot yanıtı
    """
    response = get_chatbot_response(message, chat_history)
    return {"response": response}

@router.post("/contact")
async def contact_support(
    subject: str,
    message: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Destek ekibiyle iletişime geçmek için endpoint.
    
    Args:
        subject: Konu
        message: Mesaj
        current_user: Mevcut kullanıcı
        db: Veritabanı oturumu
        
    Returns:
        Dict[str, str]: Başarı mesajı
    """
    # Destek talebini veritabanına kaydet
    # TODO: Destek talebi modeli oluştur ve kaydet
    
    return {"message": "Destek talebiniz alındı. En kısa sürede size dönüş yapacağız."} 