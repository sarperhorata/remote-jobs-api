import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    # ... existing settings ...
    
    # Stripe settings
    STRIPE_SECRET_KEY: str = os.getenv("STRIPE_SECRET_KEY", "")
    STRIPE_WEBHOOK_SECRET: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    
    # ... rest of the settings ... 