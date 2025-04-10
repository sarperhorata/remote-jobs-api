import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Any, Optional

# Chatbot yanıtları
CHATBOT_RESPONSES = {
    "greeting": [
        "Merhaba! Size nasıl yardımcı olabilirim?",
        "Hoş geldiniz! Nasıl yardımcı olabilirim?",
        "Merhaba, size nasıl yardımcı olabilirim?"
    ],
    "farewell": [
        "Görüşmek üzere!",
        "İyi günler!",
        "Başka bir sorunuz olursa yardımcı olmaktan memnuniyet duyarım."
    ],
    "thanks": [
        "Rica ederim!",
        "Ne demek, her zaman!",
        "Yardımcı olabildiysem ne mutlu bana!"
    ],
    "default": [
        "Üzgünüm, bu konuda size yardımcı olamadım. Sorunuzu destek ekibimize ileteceğim.",
        "Bu konuda daha fazla bilgi için destek ekibimizle iletişime geçebilirsiniz.",
        "Bu sorunuzu destek ekibimize ileteceğim, en kısa sürede size dönüş yapacaklardır."
    ]
}

# Sık sorulan sorular ve yanıtları
FAQ = {
    "premium": [
        "Premium üyelik nedir?",
        "Premium üyelik avantajları nelerdir?",
        "Premium üyeliğe nasıl geçebilirim?"
    ],
    "account": [
        "Hesabımı nasıl silebilirim?",
        "Şifremi nasıl değiştirebilirim?",
        "E-posta adresimi nasıl güncelleyebilirim?"
    ],
    "jobs": [
        "İş ilanlarını nasıl filtreleyebilirim?",
        "İş başvurusu nasıl yapabilirim?",
        "Favori ilanları nasıl kaydedebilirim?"
    ],
    "linkedin": [
        "LinkedIn hesabımı nasıl bağlayabilirim?",
        "LinkedIn verilerimi nasıl güncelleyebilirim?",
        "LinkedIn bağlantısını nasıl kaldırabilirim?"
    ],
    "cv": [
        "CV'mi nasıl yükleyebilirim?",
        "CV'mi nasıl güncelleyebilirim?",
        "CV'mi nasıl silebilirim?"
    ]
}

# FAQ yanıtları
FAQ_ANSWERS = {
    "premium": "Premium üyelik, sınırsız iş ilanı görüntüleme, günlük bildirimler, otomatik başvuru hazırlama ve kişiselleştirilmiş iş eşleştirme gibi özelliklere sahiptir. Premium üyeliğe geçmek için profil sayfanızdan 'Premium'a Yükselt' butonuna tıklayabilirsiniz.",
    "account": "Hesap ayarlarınızı profil sayfanızdan güncelleyebilirsiniz. Şifrenizi değiştirmek için 'Şifre Değiştir' seçeneğini, e-posta adresinizi güncellemek için 'E-posta Güncelle' seçeneğini kullanabilirsiniz.",
    "jobs": "İş ilanlarını filtrelemek için arama çubuğunu ve filtreleme seçeneklerini kullanabilirsiniz. İş başvurusu yapmak için ilan detay sayfasındaki 'Başvur' butonuna tıklayabilirsiniz. Favori ilanları kaydetmek için ilan kartındaki kalp ikonuna tıklayabilirsiniz.",
    "linkedin": "LinkedIn hesabınızı bağlamak için profil sayfanızdan 'LinkedIn Bağla' seçeneğini kullanabilirsiniz. Verilerinizi güncellemek için 'Verileri Güncelle' butonuna tıklayabilirsiniz. Bağlantıyı kaldırmak için 'LinkedIn Bağlantısını Kaldır' seçeneğini kullanabilirsiniz.",
    "cv": "CV'nizi yüklemek için profil sayfanızdan 'CV Yükle' seçeneğini kullanabilirsiniz. CV'nizi güncellemek için aynı seçeneği tekrar kullanabilirsiniz. CV'nizi silmek için 'CV Sil' seçeneğini kullanabilirsiniz."
}

def get_chatbot_response(message: str, chat_history: List[Dict[str, str]]) -> str:
    """
    Kullanıcı mesajına chatbot yanıtı verir.
    
    Args:
        message: Kullanıcı mesajı
        chat_history: Sohbet geçmişi
        
    Returns:
        str: Chatbot yanıtı
    """
    message = message.lower()
    
    # Selamlama kontrolü
    if any(word in message for word in ["merhaba", "selam", "hey", "hi", "hello"]):
        return get_random_response("greeting")
    
    # Teşekkür kontrolü
    if any(word in message for word in ["teşekkür", "sağol", "thanks", "thank you"]):
        return get_random_response("thanks")
    
    # Vedalaşma kontrolü
    if any(word in message for word in ["görüşürüz", "hoşçakal", "bye", "goodbye"]):
        return get_random_response("farewell")
    
    # FAQ kontrolü
    for category, questions in FAQ.items():
        for question in questions:
            if question.lower() in message:
                return FAQ_ANSWERS[category]
    
    # Eğer yanıt bulunamazsa, manuel review için e-posta gönder
    send_manual_review_email(message, chat_history)
    return get_random_response("default")

def get_random_response(response_type: str) -> str:
    """
    Belirli bir türde rastgele yanıt döndürür.
    
    Args:
        response_type: Yanıt türü
        
    Returns:
        str: Rastgele yanıt
    """
    import random
    return random.choice(CHATBOT_RESPONSES[response_type])

def send_manual_review_email(message: str, chat_history: List[Dict[str, str]]) -> None:
    """
    Manuel review için e-posta gönderir.
    
    Args:
        message: Kullanıcı mesajı
        chat_history: Sohbet geçmişi
    """
    # E-posta ayarları
    sender_email = os.getenv("SUPPORT_EMAIL", "support@remotejobs.com")
    receiver_email = os.getenv("MANUAL_REVIEW_EMAIL", "review@remotejobs.com")
    password = os.getenv("EMAIL_PASSWORD", "")
    
    # E-posta içeriği
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = "Manuel Review Gerekli - Chatbot"
    
    # Sohbet geçmişini formatla
    chat_history_text = "\n".join([f"{item['role']}: {item['content']}" for item in chat_history])
    
    body = f"""
    Kullanıcı Mesajı: {message}
    
    Sohbet Geçmişi:
    {chat_history_text}
    """
    
    msg.attach(MIMEText(body, "plain"))
    
    # E-posta gönder
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, password)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print(f"E-posta gönderme hatası: {e}") 