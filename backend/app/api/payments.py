from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
import stripe
from app.core.config import settings
from app.core.auth import get_current_user
from app.models.user import User

router = APIRouter()

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

class PaymentIntentRequest(BaseModel):
    payment_method_id: str
    amount: int
    user_id: Optional[str] = None

@router.post("/create-payment-intent")
async def create_payment_intent(
    request: PaymentIntentRequest,
    current_user: User = Depends(get_current_user)
):
    try:
        # Create a PaymentIntent with the order amount and currency
        intent = stripe.PaymentIntent.create(
            amount=request.amount,
            currency="usd",
            payment_method=request.payment_method_id,
            confirm=True,
            return_url=f"{settings.FRONTEND_URL}/payment/success",
            metadata={
                "user_id": str(current_user.id),
            }
        )

        return {
            "clientSecret": intent.client_secret,
            "status": intent.status
        }
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/payment-intent/{payment_intent_id}")
async def get_payment_intent(
    payment_intent_id: str,
    current_user: User = Depends(get_current_user)
):
    try:
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        
        # Verify that the payment belongs to the current user
        if intent.metadata.get("user_id") != str(current_user.id):
            raise HTTPException(status_code=403, detail="Not authorized to view this payment")
        
        return {
            "status": intent.status,
            "amount": intent.amount,
            "currency": intent.currency
        }
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 