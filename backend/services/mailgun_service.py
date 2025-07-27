import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger(__name__)


class MailgunService:
    """Mailgun email service for sending emails"""

    def __init__(self):
        self.api_key = os.getenv("MAILGUN_API_KEY")
        self.domain = os.getenv(
            "MAILGUN_DOMAIN", "mg.buzz2remote.com"
        )  # Mailgun'da ayarlanmış domain
        self.from_email = os.getenv("FROM_EMAIL", "info@buzz2remote.com")
        self.base_url = f"https://api.mailgun.net/v3/{self.domain}"

        # Daily email limit for free tier
        self.daily_limit = 100
        self.sent_today = 0
        self.last_reset_date = datetime.now().date()

        # Brand colors and styling
        self.brand_colors = {
            "primary": "#667eea",
            "secondary": "#764ba2",
            "success": "#28a745",
            "warning": "#ffc107",
            "danger": "#dc3545",
            "info": "#17a2b8",
            "light": "#f8f9fa",
            "dark": "#343a40",
        }

    def _get_base_template(
        self,
        title: str,
        content: str,
        header_gradient: str = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    ) -> str:
        """Get base email template with Buzz2Remote branding"""
        return f"""
        <!DOCTYPE html>
        <html lang="tr">
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <meta http-equiv="X-UA-Compatible" content="IE=edge">
            <title>{title}</title>
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
                
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                
                body {{
                    font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    margin: 0;
                    padding: 20px;
                    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                    min-height: 100vh;
                }}
                
                .email-wrapper {{
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: white;
                    border-radius: 16px;
                    overflow: hidden;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                }}
                
                .header {{
                    background: {header_gradient};
                    color: white;
                    padding: 40px 30px;
                    text-align: center;
                    position: relative;
                }}
                
                .header::before {{
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="20" cy="20" r="2" fill="rgba(255,255,255,0.1)"/><circle cx="80" cy="40" r="1" fill="rgba(255,255,255,0.1)"/><circle cx="40" cy="80" r="1.5" fill="rgba(255,255,255,0.1)"/></svg>');
                }}
                
                .logo {{
                    font-size: 28px;
                    font-weight: 700;
                    margin-bottom: 10px;
                    position: relative;
                    z-index: 2;
                }}
                
                .header h1 {{
                    font-size: 24px;
                    font-weight: 600;
                    margin-bottom: 8px;
                    position: relative;
                    z-index: 2;
                }}
                
                .header p {{
                    font-size: 16px;
                    opacity: 0.9;
                    position: relative;
                    z-index: 2;
                }}
                
                .content {{
                    padding: 40px 30px;
                }}
                
                .content h2 {{
                    color: #2d3748;
                    font-size: 20px;
                    font-weight: 600;
                    margin-bottom: 20px;
                }}
                
                .content p {{
                    color: #4a5568;
                    font-size: 15px;
                    margin-bottom: 15px;
                }}
                
                .button {{
                    display: inline-block;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white !important;
                    padding: 15px 32px;
                    text-decoration: none;
                    border-radius: 8px;
                    font-weight: 600;
                    font-size: 15px;
                    margin: 20px 0;
                    transition: all 0.3s ease;
                    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
                }}
                
                .button:hover {{
                    transform: translateY(-2px);
                    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
                }}
                
                .feature-list {{
                    background-color: #f8fafc;
                    border-radius: 12px;
                    padding: 24px;
                    margin: 24px 0;
                }}
                
                .feature-item {{
                    display: flex;
                    align-items: flex-start;
                    margin-bottom: 16px;
                    padding: 12px;
                    background: white;
                    border-radius: 8px;
                    border-left: 4px solid #667eea;
                }}
                
                .feature-item:last-child {{
                    margin-bottom: 0;
                }}
                
                .feature-icon {{
                    font-size: 20px;
                    margin-right: 12px;
                    margin-top: 2px;
                }}
                
                .feature-content h3 {{
                    color: #2d3748;
                    font-size: 16px;
                    font-weight: 600;
                    margin-bottom: 4px;
                }}
                
                .feature-content p {{
                    color: #718096;
                    font-size: 14px;
                    margin: 0;
                }}
                
                .warning-box {{
                    background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
                    border: 1px solid #f0c14b;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 20px 0;
                }}
                
                .warning-box strong {{
                    color: #856404;
                    display: block;
                    margin-bottom: 8px;
                }}
                
                .footer {{
                    background-color: #f8fafc;
                    padding: 30px;
                    text-align: center;
                    border-top: 1px solid #e2e8f0;
                }}
                
                .footer p {{
                    color: #718096;
                    font-size: 13px;
                    margin-bottom: 8px;
                }}
                
                .footer-links {{
                    margin-top: 20px;
                }}
                
                .footer-links a {{
                    color: #667eea;
                    text-decoration: none;
                    margin: 0 10px;
                    font-size: 13px;
                }}
                
                .social-links {{
                    margin-top: 16px;
                }}
                
                .social-links a {{
                    display: inline-block;
                    margin: 0 8px;
                    color: #718096;
                    text-decoration: none;
                }}
                
                @media only screen and (max-width: 600px) {{
                    body {{
                        padding: 10px;
                    }}
                    
                    .header {{
                        padding: 30px 20px;
                    }}
                    
                    .content {{
                        padding: 30px 20px;
                    }}
                    
                    .footer {{
                        padding: 20px;
                    }}
                    
                    .button {{
                        display: block;
                        text-align: center;
                        width: 100%;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="email-wrapper">
                <div class="header">
                    <div class="logo">🚀 Buzz2Remote</div>
                    <h1>{title}</h1>
                    <p>Remote iş dünyasının lideri</p>
                </div>
                <div class="content">
                    {content}
                </div>
                <div class="footer">
                    <p>Bu email, Buzz2Remote sistemi tarafından gönderilmiştir.</p>
                    <p>© 2024 Buzz2Remote. Tüm hakları saklıdır.</p>
                    <div class="footer-links">
                        <a href="https://buzz2remote.com/privacy">Gizlilik Politikası</a>
                        <a href="https://buzz2remote.com/terms">Kullanım Koşulları</a>
                        <a href="https://buzz2remote.com/contact">İletişim</a>
                    </div>
                    <div class="social-links">
                        <a href="https://linkedin.com/company/buzz2remote">LinkedIn</a>
                        <a href="https://twitter.com/buzz2remote">Twitter</a>
                        <a href="https://github.com/buzz2remote">GitHub</a>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

    def _check_daily_limit(self) -> bool:
        """Check if we're within daily email limit"""
        current_date = datetime.now().date()

        # Reset counter if new day
        if current_date > self.last_reset_date:
            self.sent_today = 0
            self.last_reset_date = current_date

        return self.sent_today < self.daily_limit

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        from_name: Optional[str] = "Buzz2Remote",
    ) -> Dict[str, Any]:
        """
        Send email via Mailgun API

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML email content
            text_content: Plain text content (optional)
            from_name: Sender name (optional)

        Returns:
            Dict with success status and message
        """
        try:
            # Check if Mailgun API key is configured
            if not self.api_key:
                logger.warning(
                    f"Mailgun API key not configured. Logging email instead of sending: {to_email} - {subject}"
                )
                logger.info(f"Email content (HTML): {html_content[:500]}...")
                if text_content:
                    logger.info(f"Email content (Text): {text_content[:500]}...")

                # Return success for development/testing purposes
                return {
                    "success": True,
                    "message": "Email logged (Mailgun not configured)",
                    "warning": "Mailgun API key not configured - email was logged instead of sent",
                }

            # Check daily limit
            if not self._check_daily_limit():
                logger.error(f"Daily email limit ({self.daily_limit}) reached")
                return {
                    "success": False,
                    "error": "Daily email limit reached",
                    "limit_info": {
                        "sent_today": self.sent_today,
                        "daily_limit": self.daily_limit,
                    },
                }

            # Prepare email data
            from_address = (
                f"{from_name} <{self.from_email}>" if from_name else self.from_email
            )

            data = {
                "from": from_address,
                "to": to_email,
                "subject": subject,
                "html": html_content,
            }

            if text_content:
                data["text"] = text_content

            # Send email via Mailgun API
            response = requests.post(
                f"{self.base_url}/messages",
                auth=("api", self.api_key),
                data=data,
                timeout=30,
            )

            if response.status_code == 200:
                self.sent_today += 1
                logger.info(f"Email sent successfully to {to_email}")
                return {
                    "success": True,
                    "message_id": response.json().get("id"),
                    "message": "Email sent successfully",
                }
            else:
                logger.error(
                    f"Mailgun API error: {response.status_code} - {response.text}"
                )
                return {
                    "success": False,
                    "error": f"Mailgun API error: {response.status_code}",
                    "details": response.text,
                }

        except requests.exceptions.Timeout:
            logger.error("Mailgun API timeout")
            return {"success": False, "error": "Email service timeout"}
        except requests.exceptions.RequestException as e:
            logger.error(f"Mailgun request error: {str(e)}")
            return {"success": False, "error": f"Request error: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error sending email: {str(e)}")
            return {"success": False, "error": f"Unexpected error: {str(e)}"}

    def send_verification_email(self, email: str, token: str) -> bool:
        """Send email verification email with enhanced template"""
        frontend_url = os.getenv("FRONTEND_URL", "https://buzz2remote.com")
        verification_url = f"{frontend_url}/verify-email?token={token}"

        subject = "✅ Email Adresinizi Doğrulayın - Buzz2Remote"

        content = f"""
        <h2>🎉 Hoş Geldiniz!</h2>
        <p>Buzz2Remote'a kaydolduğunuz için teşekkürler! Hesabınızı aktifleştirmek için email adresinizi doğrulamanız gerekiyor.</p>
        
        <a href="{verification_url}" class="button">✅ Email Adresimi Doğrula</a>
        
        <div class="feature-list">
            <div class="feature-item">
                <div class="feature-icon">🔍</div>
                <div class="feature-content">
                    <h3>Akıllı İş Arama</h3>
                    <p>AI destekli filtreleme ile size uygun remote işleri keşfedin</p>
                </div>
            </div>
            <div class="feature-item">
                <div class="feature-icon">🤖</div>
                <div class="feature-content">
                    <h3>Otomatik Başvuru</h3>
                    <p>Tek tıkla işlere başvurun, zamanınızı değerlendirin</p>
                </div>
            </div>
            <div class="feature-item">
                <div class="feature-icon">📊</div>
                <div class="feature-content">
                    <h3>Başvuru Takibi</h3>
                    <p>Tüm başvurularınızı tek yerden yönetin ve takip edin</p>
                </div>
            </div>
            <div class="feature-item">
                <div class="feature-icon">🌍</div>
                <div class="feature-content">
                    <h3>Global Fırsatlar</h3>
                    <p>470+ şirketten 36.000+ remote iş fırsatı</p>
                </div>
            </div>
        </div>
        
        <p><strong>⏰ Bu link 24 saat geçerlidir.</strong></p>
        
        <p>Eğer bu işlemi siz yapmadıysanız, bu emaili güvenle silebilirsiniz.</p>
        
        <p style="word-break: break-all; background-color: #f8fafc; padding: 12px; border-radius: 6px; font-size: 12px; color: #718096;">
            Alternatif link: {verification_url}
        </p>
        """

        html_content = self._get_base_template("Email Doğrulama", content)

        text_content = f"""
        Buzz2Remote'a Hoş Geldiniz!
        
        Email adresinizi doğrulamak için aşağıdaki linke tıklayın:
        {verification_url}
        
        Bu link 24 saat geçerlidir.
        
        Eğer bu işlemi siz yapmadıysanız, bu emaili görmezden gelebilirsiniz.
        
        Buzz2Remote Ekibi
        """

        result = self.send_email(
            to_email=email,
            subject=subject,
            html_content=html_content,
            text_content=text_content,
        )

        return result.get("success", False)

    def send_password_reset_email(self, email: str, token: str) -> bool:
        """Send password reset email with enhanced template"""
        frontend_url = os.getenv("FRONTEND_URL", "https://buzz2remote.com")
        reset_url = f"{frontend_url}/reset-password?token={token}"

        subject = "🔐 Şifre Sıfırlama Talebi - Buzz2Remote"

        content = f"""
        <h2>Şifrenizi Sıfırlayın</h2>
        <p>Buzz2Remote hesabınız için şifre sıfırlama talebi aldık. Güvenliğiniz için hemen işlem yapmanızı öneririz.</p>
        
        <a href="{reset_url}" class="button">🔐 Şifremi Sıfırla</a>
        
        <div class="warning-box">
            <strong>⚠️ Güvenlik Uyarısı:</strong>
            <ul style="margin: 8px 0 0 20px; color: #856404;">
                <li>Bu link sadece <strong>1 saat</strong> geçerlidir</li>
                <li>Eğer bu talebi siz yapmadıysanız, derhal bizimle iletişime geçin</li>
                <li>Şifrenizi kimseyle paylaşmayın</li>
                <li>Güçlü bir şifre seçin (en az 8 karakter, büyük/küçük harf, rakam)</li>
            </ul>
        </div>
        
        <p style="word-break: break-all; background-color: #f8fafc; padding: 12px; border-radius: 6px; font-size: 12px; color: #718096;">
            Alternatif link: {reset_url}
        </p>
        
        <p>Eğer bu talebi siz yapmadıysanız, hesabınızın güvenliği için derhal şifrenizi değiştirmenizi öneririz.</p>
        
        <p><strong>Destek:</strong> Herhangi bir sorun yaşarsanız <a href="mailto:support@buzz2remote.com">support@buzz2remote.com</a> adresinden bizimle iletişime geçebilirsiniz.</p>
        """

        html_content = self._get_base_template(
            "Şifre Sıfırlama",
            content,
            "linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%)",
        )

        text_content = f"""
        Şifre Sıfırlama - Buzz2Remote
        
        Şifrenizi sıfırlamak için aşağıdaki linke tıklayın:
        {reset_url}
        
        ⚠️ Bu link 1 saat geçerlidir.
        
        Eğer bu talebi siz yapmadıysanız, derhal bizimle iletişime geçin.
        
        Buzz2Remote Güvenlik Ekibi
        """

        result = self.send_email(
            to_email=email,
            subject=subject,
            html_content=html_content,
            text_content=text_content,
        )

        return result.get("success", False)

    def send_welcome_email(self, email: str, name: str) -> bool:
        """Send welcome email after onboarding completion"""
        subject = "🎉 Hoş Geldiniz! Kariyeriniz Başlıyor - Buzz2Remote"

        content = f"""
        <h2>Merhaba {name}! 🎉</h2>
        <p>Tebrikler! Buzz2Remote ailesine katıldınız. Artık dünyanın en iyi remote iş fırsatlarına erişim sahibisiniz.</p>
        
        <a href="{os.getenv('FRONTEND_URL', 'https://buzz2remote.com')}/dashboard" class="button">🚀 Dashboard'a Git</a>
        
        <div class="feature-list">
            <div class="feature-item">
                <div class="feature-icon">🎯</div>
                <div class="feature-content">
                    <h3>İlk İş Aramanızı Yapın</h3>
                    <p>AI destekli filtreleme ile size uygun remote işleri keşfedin</p>
                </div>
            </div>
            <div class="feature-item">
                <div class="feature-icon">⚡</div>
                <div class="feature-content">
                    <h3>Otomatik Başvuru Sistemi</h3>
                    <p>Tek tıkla işlere başvurun, zamanınızı değerlendirin</p>
                </div>
            </div>
            <div class="feature-item">
                <div class="feature-icon">📈</div>
                <div class="feature-content">
                    <h3>Başvuru Takibi</h3>
                    <p>Tüm başvurularınızı tek yerden yönetin ve takip edin</p>
                </div>
            </div>
        </div>
        
        <h3>💡 Hızlı Başlangıç Rehberi:</h3>
        <ol style="color: #4a5568; margin-left: 20px;">
            <li><strong>Profilinizi tamamlayın</strong> - %100 tamamlanmış profiller %75 daha fazla görüntülenir</li>
            <li><strong>CV'nizi yükleyin</strong> - AI otomatik olarak becerilerinizi analiz edecek</li>
            <li><strong>İş tercihlerinizi belirtin</strong> - Size özel iş önerileri alın</li>
            <li><strong>Günlük job alertlerinizi aktif edin</strong> - Yeni fırsatları kaçırmayın</li>
        </ol>
        
        <p>Herhangi bir sorunuz olursa, <a href="mailto:support@buzz2remote.com">support@buzz2remote.com</a> adresinden bizimle iletişime geçmekten çekinmeyin.</p>
        
        <p><strong>Remote çalışma dünyasında başarılar!</strong></p>
        """

        html_content = self._get_base_template(
            "Hoş Geldiniz!",
            content,
            "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)",
        )

        result = self.send_email(
            to_email=email, subject=subject, html_content=html_content
        )

        return result.get("success", False)

    def send_new_jobs_email(
        self, email: str, name: str, jobs: List[Dict], user_preferences: Dict = None
    ) -> bool:
        """Send daily/weekly new jobs email"""
        job_count = len(jobs)
        subject = f"🔥 {job_count} Yeni Remote İş Fırsatı - Buzz2Remote"

        # Create search URL with user preferences
        frontend_url = os.getenv("FRONTEND_URL", "https://buzz2remote.com")
        search_params = []

        if user_preferences:
            if user_preferences.get("location"):
                search_params.append(f"location={user_preferences['location']}")
            if user_preferences.get("skills"):
                search_params.append(
                    f"skills={','.join(user_preferences['skills'][:3])}"
                )
            if user_preferences.get("salary_min"):
                search_params.append(f"salary_min={user_preferences['salary_min']}")

        search_params.append("date_range=24h")  # Son 24 saat
        search_url = f"{frontend_url}/jobs?" + "&".join(search_params)

        # Generate job cards HTML
        job_cards_html = ""
        for job in jobs[:5]:  # Sadece ilk 5 işi göster
            salary_info = ""
            if job.get("salary_min") and job.get("salary_max"):
                salary_info = f"${job['salary_min']:,} - ${job['salary_max']:,}"
            elif job.get("salary_min"):
                salary_info = f"${job['salary_min']:,}+"

            location_info = job.get("location", "Remote")
            if location_info == "Remote" or not location_info:
                location_info = "🌍 Anywhere"

            job_cards_html += f"""
            <div style="background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; margin-bottom: 16px; transition: all 0.3s ease;">
                <div style="display: flex; align-items: center; margin-bottom: 12px;">
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); width: 40px; height: 40px; border-radius: 8px; display: flex; align-items: center; justify-content: center; margin-right: 12px; color: white; font-weight: bold;">
                        {job.get("company_name", "?")[0].upper()}
                    </div>
                    <div>
                        <h3 style="color: #2d3748; margin: 0; font-size: 16px; font-weight: 600;">{job.get("title", "İş Pozisyonu")}</h3>
                        <p style="color: #718096; margin: 0; font-size: 14px;">{job.get("company_name", "Şirket")}</p>
                    </div>
                </div>
                <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 12px;">
                    <span style="background: #e6fffa; color: #234e52; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: 500;">📍 {location_info}</span>
                    {f'<span style="background: #f0fff4; color: #22543d; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: 500;">💰 {salary_info}</span>' if salary_info else ''}
                    <span style="background: #fef5e7; color: #744210; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: 500;">🕒 {job.get("work_type", "Full-time")}</span>
                </div>
                <p style="color: #4a5568; font-size: 14px; line-height: 1.5; margin-bottom: 12px;">{job.get("description", "")[:120]}...</p>
                <a href="{frontend_url}/jobs/{job.get('_id', '')}" style="color: #667eea; text-decoration: none; font-weight: 500; font-size: 14px;">Detayları Görüntüle →</a>
            </div>
            """

        content = f"""
        <h2>Merhaba {name}! 👋</h2>
        <p>Son 24 saatte sizin için <strong>{job_count} yeni remote iş fırsatı</strong> bulundu!</p>
        
        <a href="{search_url}" class="button">🔍 Tüm Yeni İşleri Görüntüle ({job_count})</a>
        
        <h3>✨ Öne Çıkan Fırsatlar:</h3>
        <div style="background: #f8fafc; border-radius: 12px; padding: 20px; margin: 20px 0;">
            {job_cards_html}
            {f'<p style="text-align: center; color: #718096; font-size: 14px; margin-top: 16px;">+{job_count - 5} daha fazla iş fırsatı</p>' if job_count > 5 else ''}
        </div>
        
        <div style="background: linear-gradient(135deg, #e6fffa 0%, #f0fff4 100%); border-radius: 12px; padding: 20px; margin: 20px 0;">
            <h3 style="color: #234e52; margin-bottom: 12px;">💡 Pro İpucu:</h3>
            <p style="color: #285e61; margin: 0;">Yeni ilan verilen işlere ilk başvuranlar arasında olmak başarı şansınızı %40 artırıyor!</p>
        </div>
        
        <h3>📊 Bu Hafta ki Özet:</h3>
        <ul style="color: #4a5568;">
            <li>Yeni işler: <strong>{job_count}</strong></li>
            <li>En popüler konum: <strong>🌍 Anywhere</strong></li>
            <li>Ortalama maaş: <strong>$75,000+</strong></li>
            <li>En çok aranan beceri: <strong>Python, React, Node.js</strong></li>
        </ul>
        
        <p>Bu email'i almayı istemiyorsanız, <a href="{frontend_url}/unsubscribe?email={email}">buradan</a> abonelikten çıkabilirsiniz.</p>
        """

        html_content = self._get_base_template(
            "Yeni İş Fırsatları",
            content,
            "linear-gradient(135deg, #ff9a56 0%, #ffad56 100%)",
        )

        result = self.send_email(
            to_email=email, subject=subject, html_content=html_content
        )

        return result.get("success", False)

    def send_application_status_email(
        self, email: str, name: str, job_title: str, company_name: str, status: str
    ) -> bool:
        """Send application status update email"""
        status_info = {
            "accepted": {
                "emoji": "🎉",
                "color": "#10b981",
                "title": "Başvurunuz Kabul Edildi!",
                "message": "Tebrikler! Başvurunuz olumlu karşılandı.",
            },
            "rejected": {
                "emoji": "😔",
                "color": "#ef4444",
                "title": "Başvuru Sonucu",
                "message": "Maalesef bu sefer olmadı, ama pes etmeyin!",
            },
            "interview": {
                "emoji": "📞",
                "color": "#3b82f6",
                "title": "Mülakat Davetiniz Var!",
                "message": "Harika haber! Mülakat için davet edildiniz.",
            },
            "viewed": {
                "emoji": "👀",
                "color": "#8b5cf6",
                "title": "Başvurunuz İnceleniyor",
                "message": "Başvurunuz HR ekibi tarafından görüntülendi.",
            },
        }

        info = status_info.get(
            status,
            {
                "emoji": "📝",
                "color": "#6b7280",
                "title": "Başvuru Güncellemesi",
                "message": "Başvuru durumunuzda güncelleme var.",
            },
        )

        subject = f"{info['emoji']} {info['title']} - {company_name}"

        content = f"""
        <h2>Merhaba {name}!</h2>
        <p>{info['message']}</p>
        
        <div style="background: {info['color']}15; border: 1px solid {info['color']}40; border-radius: 12px; padding: 20px; margin: 20px 0;">
            <h3 style="color: {info['color']}; margin-bottom: 8px;">{info['emoji']} {info['title']}</h3>
            <p style="color: #4a5568; margin-bottom: 8px;"><strong>Pozisyon:</strong> {job_title}</p>
            <p style="color: #4a5568; margin: 0;"><strong>Şirket:</strong> {company_name}</p>
        </div>
        
        <a href="{os.getenv('FRONTEND_URL', 'https://buzz2remote.com')}/applications" class="button">📊 Tüm Başvurularım</a>
        
        <p>Başarılar dileriz!</p>
        """

        html_content = self._get_base_template(
            info["title"],
            content,
            f"linear-gradient(135deg, {info['color']} 0%, {info['color']}dd 100%)",
        )

        result = self.send_email(
            to_email=email, subject=subject, html_content=html_content
        )

        return result.get("success", False)

    def create_mailgun_template(
        self, template_name: str, template_content: Dict
    ) -> Dict[str, Any]:
        """Create stored template in Mailgun"""
        try:
            data = {
                "name": template_name,
                "description": template_content.get("description", ""),
                "template": template_content.get("html", ""),
                "tag": "buzz2remote-templates",
            }

            response = requests.post(
                f"{self.base_url}/templates",
                auth=("api", self.api_key),
                data=data,
                timeout=30,
            )

            if response.status_code == 200:
                logger.info(f"Template {template_name} created successfully")
                return {
                    "success": True,
                    "template_name": template_name,
                    "response": response.json(),
                }
            else:
                logger.error(
                    f"Failed to create template: {response.status_code} - {response.text}"
                )
                return {
                    "success": False,
                    "error": f"Mailgun API error: {response.status_code}",
                    "details": response.text,
                }

        except Exception as e:
            logger.error(f"Error creating template: {str(e)}")
            return {"success": False, "error": str(e)}

    def test_email_service(self, test_email: str) -> Dict[str, Any]:
        """Test email service with enhanced template"""
        subject = "🧪 Test Email - Buzz2Remote"

        content = f"""
        <h2>Email Service Test</h2>
        <p>Bu bir test emailidir. Eğer bu emaili alıyorsanız, Mailgun entegrasyonu başarıyla çalışıyor!</p>
        
        <div class="feature-list">
            <div class="feature-item">
                <div class="feature-icon">✅</div>
                <div class="feature-content">
                    <h3>Mailgun Servisi</h3>
                    <p>Aktif ve çalışıyor</p>
                </div>
            </div>
            <div class="feature-item">
                <div class="feature-icon">📧</div>
                <div class="feature-content">
                    <h3>Email Gönderimi</h3>
                    <p>Başarıyla tamamlandı</p>
                </div>
            </div>
        </div>
        
        <p><strong>Test tarihi:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        """

        html_content = self._get_base_template(
            "Test Email", content, "linear-gradient(135deg, #10b981 0%, #059669 100%)"
        )

        return self.send_email(
            to_email=test_email, subject=subject, html_content=html_content
        )

    def get_stats(self) -> Dict[str, Any]:
        """Get email service statistics"""
        return {
            "sent_today": self.sent_today,
            "daily_limit": self.daily_limit,
            "remaining_today": self.daily_limit - self.sent_today,
            "last_reset_date": self.last_reset_date.isoformat(),
            "service_status": (
                "active" if self._check_daily_limit() else "limit_reached"
            ),
        }


# Global instance
mailgun_service = MailgunService()
