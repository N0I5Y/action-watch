import stripe
from fastapi import APIRouter, Request, HTTPException, Depends, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.config import get_settings
from app.core.db import get_db
from app.models.subscription import Subscription
from app.models.workflow import Organization

router = APIRouter()
settings = get_settings()

stripe.api_key = settings.STRIPE_SECRET_KEY

class CheckoutRequest(BaseModel):
    installation_id: int
    success_url: str
    cancel_url: str

class PortalRequest(BaseModel):
    installation_id: int
    return_url: str

@router.post("/checkout")
async def create_checkout_session(req: CheckoutRequest, db: Session = Depends(get_db)):
    if not settings.STRIPE_SECRET_KEY or not settings.STRIPE_PRICE_ID_PRO:
        raise HTTPException(status_code=500, detail="Stripe not configured")

    # Check if org exists
    org = db.query(Organization).filter(Organization.github_org_id == req.installation_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    # Check if subscription exists
    sub = db.query(Subscription).filter(Subscription.installation_id == req.installation_id).first()
    
    customer_id = sub.stripe_customer_id if sub else None

    try:
        # If no customer, create one (or let Checkout do it, but better to track)
        # For simplicity, we'll let Checkout create it if we don't have one, 
        # but we need to pass metadata to link it back.
        
        checkout_session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=["card"],
            line_items=[
                {"price": settings.STRIPE_PRICE_ID_PRO, "quantity": 1},
            ],
            mode="subscription",
            success_url=req.success_url,
            cancel_url=req.cancel_url,
            client_reference_id=str(req.installation_id),
            subscription_data={
                "metadata": {
                    "installation_id": str(req.installation_id)
                }
            }
        )
        return {"url": checkout_session.url}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/portal")
async def create_portal_session(req: PortalRequest, db: Session = Depends(get_db)):
    if not settings.STRIPE_SECRET_KEY:
        raise HTTPException(status_code=500, detail="Stripe not configured")

    sub = db.query(Subscription).filter(Subscription.installation_id == req.installation_id).first()
    if not sub or not sub.stripe_customer_id:
        raise HTTPException(status_code=400, detail="No subscription found")

    try:
        portal_session = stripe.billing_portal.Session.create(
            customer=sub.stripe_customer_id,
            return_url=req.return_url,
        )
        return {"url": portal_session.url}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/webhook")
async def stripe_webhook(request: Request, stripe_signature: str = Header(None), db: Session = Depends(get_db)):
    if not settings.STRIPE_WEBHOOK_SECRET:
        raise HTTPException(status_code=500, detail="Stripe webhook secret not configured")

    payload = await request.body()

    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle events
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        # Fulfill the purchase...
        handle_checkout_completed(session, db)

    elif event["type"] == "customer.subscription.updated":
        subscription = event["data"]["object"]
        handle_subscription_updated(subscription, db)

    elif event["type"] == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        handle_subscription_deleted(subscription, db)

    return {"status": "success"}

def handle_checkout_completed(session, db: Session):
    installation_id = session.get("client_reference_id")
    customer_id = session.get("customer")
    subscription_id = session.get("subscription")
    
    if not installation_id:
        print("No installation_id in session")
        return

    # Upsert subscription
    sub = db.query(Subscription).filter(Subscription.installation_id == int(installation_id)).first()
    if not sub:
        sub = Subscription(installation_id=int(installation_id), stripe_customer_id=customer_id)
        db.add(sub)
    
    sub.stripe_customer_id = customer_id
    sub.stripe_subscription_id = subscription_id
    sub.status = "active" # Assume active on success
    db.commit()

def handle_subscription_updated(subscription, db: Session):
    sub_id = subscription.get("id")
    status = subscription.get("status")
    plan_id = subscription.get("plan", {}).get("id")
    
    # Find by subscription ID
    sub = db.query(Subscription).filter(Subscription.stripe_subscription_id == sub_id).first()
    if sub:
        sub.status = status
        sub.plan_id = plan_id
        db.commit()

def handle_subscription_deleted(subscription, db: Session):
    sub_id = subscription.get("id")
    sub = db.query(Subscription).filter(Subscription.stripe_subscription_id == sub_id).first()
    if sub:
        sub.status = "canceled"
        db.commit()
