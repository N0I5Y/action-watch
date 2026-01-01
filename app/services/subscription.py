from sqlalchemy.orm import Session
from app.models.subscription import Subscription


def is_pro_user(organization_id: int, db: Session) -> bool:
    """
    Check if an organization has an active Pro subscription.
    
    Args:
        organization_id: The organization's database ID
        db: Database session
        
    Returns:
        True if organization has active subscription, False otherwise
    """
    subscription = db.query(Subscription).filter(
        Subscription.organization_id == organization_id,
        Subscription.status == "active"
    ).first()
    
    return subscription is not None


def get_subscription_info(organization_id: int, db: Session) -> dict:
    """
    Get subscription information for an organization.
    
    Returns:
        Dictionary with isPro, status, and currentPeriodEnd
    """
    subscription = db.query(Subscription).filter(
        Subscription.organization_id == organization_id
    ).first()
    
    if not subscription or subscription.status != "active":
        return {
            "isPro": False,
            "status": "free",
            "currentPeriodEnd": None
        }
    
    return {
        "isPro": True,
        "status": subscription.status,
        "currentPeriodEnd": subscription.current_period_end.isoformat() if subscription.current_period_end else None
    }
