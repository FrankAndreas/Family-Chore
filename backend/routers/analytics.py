from datetime import datetime, timedelta
from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from ..models import User, TaskInstance


router = APIRouter(
    prefix="/analytics",
    tags=["analytics"],
    responses={404: {"description": "Not found"}},
)


@router.get("/weekly", response_model=List[Dict[str, Any]])
def get_weekly_activity(db: Session = Depends(get_db)):
    """
    Returns task completion counts for the last 7 days, grouped by user.
    Output format:
    [
        {
            "date": "2023-10-27",
            "user_stats": {
                "Alice": 5,
                "Bob": 3
            }
        },
        ...
    ]
    """
    today = datetime.now().date()
    seven_days_ago = today - timedelta(days=6)

    # Query completed tasks in the last 7 days
    results = (
        db.query(
            func.date(TaskInstance.completed_at).label("date"),
            User.nickname,
            func.count(TaskInstance.id).label("count")
        )
        .join(User, TaskInstance.user_id == User.id)
        .filter(
            TaskInstance.status == "COMPLETED",
            func.date(TaskInstance.completed_at) >= seven_days_ago
        )
        .group_by(func.date(TaskInstance.completed_at), User.nickname)
        .all()
    )

    # Initialize data structure for the last 7 days
    data_map: Dict[str, Dict[str, int]] = {}
    for i in range(7):
        day = seven_days_ago + timedelta(days=i)
        day_str = day.strftime("%Y-%m-%d")
        data_map[day_str] = {}

    # Fill in the query results
    for r in results:
        # r.date might be a string or date object depending on SQLite driver
        date_str = str(r.date)
        if date_str in data_map:
            data_map[date_str][r.nickname] = r.count

    # Format for frontend
    formatted_data: List[Dict[str, Any]] = []
    for date_str in sorted(data_map.keys()):
        entry: Dict[str, Any] = {"date": date_str}
        entry.update(data_map[date_str])
        formatted_data.append(entry)

    return formatted_data


@router.get("/distribution", response_model=List[Dict[str, Any]])
def get_points_distribution(db: Session = Depends(get_db)):
    """
    Returns the distribution of lifetime points among all users.
    Useful for 'Fairness' pie charts.
    """
    users = db.query(User).all()

    distribution = []
    for user in users:
        distribution.append({
            "name": user.nickname,
            "value": user.lifetime_points,
            "role": user.role.name if user.role else "Unknown"
        })

    return distribution
