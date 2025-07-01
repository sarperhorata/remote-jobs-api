from fastapi import APIRouter, Depends
from typing import List, Dict, Any

router = APIRouter()

@router.post("/chat")
async def chat_with_bot(
    message: str,
    chat_history: List[Dict[str, str]]
):
    """
    Chatbot ile sohbet etmek için endpoint.
    
    Args:
        message: Kullanıcı mesajı
        chat_history: Sohbet geçmişi
        
    Returns:
        Dict[str, str]: Chatbot yanıtı
    """
    # Basit chatbot response
    response = f"Mesajınızı aldık: {message}. Size yardımcı olmaya çalışacağız."
    return {"response": response}

@router.post("/contact")
async def contact_support(
    subject: str,
    message: str
):
    """
    Destek ekibiyle iletişime geçmek için endpoint.
    
    Args:
        subject: Konu
        message: Mesaj
        
    Returns:
        Dict[str, str]: Başarı mesajı
    """
    # Destek talebini kaydet (basit versiyon)
    return {"message": "Destek talebiniz alındı. En kısa sürede size dönüş yapacağız."} 