from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models import UserMetrics
from ..schemas import UserMetricsResponse

router = APIRouter()

@router.get("/user/{user_id}/metrics", response_model=List[UserMetricsResponse])
async def get_user_metrics(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieve user-specific metrics from the database.
    
    Args:
        user_id (int): The ID of the user to retrieve metrics for.
        db (Session): The database session.
    
    Returns:
        List[UserMetricsResponse]: A list of user metrics.
    """
    metrics = db.query(UserMetrics).filter(UserMetrics.user_id == user_id).all()
    if not metrics:
        raise HTTPException(status_code=404, detail="Metrics not found for the user.")
    return metrics
