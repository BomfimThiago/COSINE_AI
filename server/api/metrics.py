from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import get_db
from models import UserMetrics
from dependencies import get_current_user

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

@router.get("/metrics", response_model=UserMetrics)
async def get_user_metrics(current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Retrieve user-specific metrics data from the database.
    
    Args:
        current_user (str): The authenticated user's username.
        db (Session): The database session.
    
    Returns:
        UserMetrics: The metrics data for the authenticated user.
    """
    metrics = db.query(UserMetrics).filter(UserMetrics.user_id == current_user.id).first()
    if not metrics:
        raise HTTPException(status_code=404, detail="Metrics not found")
    return metrics