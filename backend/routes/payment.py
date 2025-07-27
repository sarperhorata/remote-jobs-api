import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import stripe
from bson.objectid import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Request, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from backend.database import get_async_db
from backend.schemas.payment import (PaymentCreate, PaymentListResponse,
                                     PaymentResponse)
from backend.schemas.user import User
from backend.utils.auth import get_current_active_user, get_current_user

router = APIRouter(prefix="/payment", tags=["payment"])

# Initialize Stripe with your secret key
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


@router.post("/create-checkout-session")
async def create_checkout_session(
    request: Request, current_user: User = Depends(get_current_active_user)
):
    """
    Create a Stripe checkout session for subscription purchase
    """
    try:
        # Get the price ID from the request
        data = await request.json()
        price_id = data.get("priceId")

        if not price_id:
            raise HTTPException(status_code=400, detail="Price ID is required")

        # Create a checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price": price_id,
                    "quantity": 1,
                }
            ],
            mode="subscription",
            success_url=f"{os.getenv('FRONTEND_URL')}/payment/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{os.getenv('FRONTEND_URL')}/payment/cancel",
            customer_email=current_user.email,
            metadata={"user_id": str(current_user.id)},
        )

        return {"sessionId": session.id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhook")
async def stripe_webhook(request: Request):
    """
    Handle Stripe webhook events
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.getenv("STRIPE_WEBHOOK_SECRET")
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle the event
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        # Update user's subscription status
        db = await get_async_db()
        users = db["users"]

        users.update_one(
            {"_id": ObjectId(session["metadata"]["user_id"])},
            {
                "$set": {
                    "subscription_type": "premium",
                    "subscription_start": datetime.utcnow(),
                    "subscription_end": datetime.utcnow()
                    + timedelta(
                        days=(
                            30 if session["metadata"]["plan_type"] == "monthly" else 365
                        )
                    ),
                    "stripe_customer_id": session["customer"],
                    "stripe_subscription_id": session["subscription"],
                }
            },
        )

    return {"status": "success"}


@router.post("/verify-payment")
async def verify_payment(
    session_id: str, current_user: dict = Depends(get_current_active_user)
):
    """
    Verify a successful payment and update user's subscription status
    """
    try:
        # Retrieve the session from Stripe
        session = stripe.checkout.Session.retrieve(session_id)

        # Verify the session belongs to the current user
        if session.metadata.get("user_id") != str(current_user["_id"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Invalid session"
            )

        # Check if payment was successful
        if session.payment_status != "paid":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Payment not completed"
            )

        # Update user's subscription status
        db = await get_async_db()
        users = db["users"]

        users.update_one(
            {"_id": ObjectId(current_user["_id"])},
            {
                "$set": {
                    "subscription_type": "premium",
                    "subscription_start": datetime.utcnow(),
                    "subscription_end": datetime.utcnow()
                    + timedelta(
                        days=30 if session.metadata["plan_type"] == "monthly" else 365
                    ),
                    "stripe_customer_id": session.customer,
                    "stripe_subscription_id": session.subscription,
                }
            },
        )

        return {"status": "success", "message": "Payment verified successfully"}

    except stripe.error.StripeError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post("/create-portal-session")
async def create_portal_session(current_user: User = Depends(get_current_active_user)):
    """Create a Stripe customer portal session"""
    try:
        # Get the customer ID from the user's subscription
        if not current_user.stripe_customer_id:
            raise HTTPException(status_code=400, detail="No active subscription found")

        # Create a portal session
        session = stripe.billing_portal.Session.create(
            customer=current_user.stripe_customer_id,
            return_url=f"{os.getenv('FRONTEND_URL')}/account",
        )

        return {"url": session.url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=PaymentResponse)
async def create_payment(
    payment: PaymentCreate,
    db: AsyncIOMotorDatabase = Depends(get_async_db),
    current_user: dict = Depends(get_current_user),
):
    """Create a new payment."""
    payment_dict = payment.dict()
    payment_dict["user_id"] = current_user["id"]
    payment_dict["created_at"] = datetime.utcnow()
    payment_dict["updated_at"] = datetime.utcnow()

    result = await db.payments.insert_one(payment_dict)
    created_payment = await db.payments.find_one({"_id": result.inserted_id})
    return created_payment


@router.get("/", response_model=List[PaymentResponse])
async def get_payments(
    db: AsyncIOMotorDatabase = Depends(get_async_db),
    current_user: dict = Depends(get_current_user),
):
    """Get all payments for the current user."""
    cursor = db.payments.find({"user_id": current_user["id"]})
    payments = await cursor.to_list(length=None)
    return payments


@router.get("/payments/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: str, db: AsyncIOMotorDatabase = Depends(get_async_db)
):
    """Get a specific payment."""
    payment = await db.payments.find_one({"_id": payment_id})
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment


@router.post("/payments/{payment_id}/webhook")
async def payment_webhook(
    payment_id: str, request: Request, db: AsyncIOMotorDatabase = Depends(get_async_db)
):
    """Handle payment webhook."""
    # Get payment
    payment = await db.payments.find_one({"_id": payment_id})
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    # Get webhook data
    webhook_data = await request.json()

    # Update payment status
    result = await db.payments.update_one(
        {"_id": payment_id},
        {
            "$set": {
                "status": webhook_data.get("status", "failed"),
                "updated_at": datetime.utcnow(),
                "webhook_data": webhook_data,
            }
        },
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Payment not found")

    return {"message": "Webhook processed successfully"}
