from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict
from database import get_db
from models import UserMetrics

router = APIRouter()

@router.get("/metrics", response_model=List[Dict[str, float]])
async def get_user_metrics(db: Session = next(get_db())):
    try:
        metrics = db.query(UserMetrics).all()
        aggregated_metrics = aggregate_metrics(metrics)
        return aggregated_metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def aggregate_metrics(metrics: List[UserMetrics]) -> List[Dict[str, float]]:
    aggregated = []
    total_users = len(metrics)
    total_activity = sum(metric.activity for metric in metrics)
    total_engagement = sum(metric.engagement for metric in metrics)

    if total_users > 0:
        aggregated.append({
            "total_users": total_users,
            "average_activity": total_activity / total_users,
            "average_engagement": total_engagement / total_users
        })
    return aggregated
