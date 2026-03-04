from datetime import datetime, timedelta
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from ..dependencies import get_current_user
from ..models import User, Task, TaskInstance
from ..schemas import (
    HeatmapDay, UserHeatmap, HeatmapResponse,
    HeatmapTaskDetail, HeatmapDayDetails,
    StreakInfo, TopPerformer, AnalyticsSummary,
)


router = APIRouter(
    prefix="/analytics",
    tags=["analytics"],
    responses={404: {"description": "Not found"}},
)


@router.get("/weekly", response_model=List[Dict[str, Any]], dependencies=[Depends(get_current_user)])
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


@router.get("/distribution", response_model=List[Dict[str, Any]], dependencies=[Depends(get_current_user)])
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


@router.get("/heatmap", response_model=HeatmapResponse, dependencies=[Depends(get_current_user)])
def get_heatmap_data(
    days: int = Query(default=30, ge=7, le=90, description="Number of days of history"),
    db: Session = Depends(get_db),
) -> HeatmapResponse:
    """
    Returns per-user, per-day task completion counts for heatmap visualisation.
    """
    today = datetime.now().date()
    start_date = today - timedelta(days=days - 1)

    # Pre-build date range
    date_range = [(start_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days)]

    # Query completed tasks in the window
    results = (
        db.query(
            TaskInstance.user_id,
            func.date(TaskInstance.completed_at).label("date"),
            func.count(TaskInstance.id).label("count"),
        )
        .filter(
            TaskInstance.status == "COMPLETED",
            func.date(TaskInstance.completed_at) >= start_date,
        )
        .group_by(TaskInstance.user_id, func.date(TaskInstance.completed_at))
        .all()
    )

    # Index results by (user_id, date_str)
    counts: Dict[int, Dict[str, int]] = {}
    for r in results:
        uid = r.user_id
        d = str(r.date)
        counts.setdefault(uid, {})[d] = r.count

    # Build response for every active user
    users = db.query(User).all()
    user_heatmaps: List[UserHeatmap] = []
    for user in users:
        uid = int(user.id)
        user_counts = counts.get(uid, {})
        days_list = [
            HeatmapDay(date=d, count=user_counts.get(d, 0))
            for d in date_range
        ]
        user_heatmaps.append(UserHeatmap(user_id=uid, nickname=str(user.nickname), days=days_list))

    return HeatmapResponse(users=user_heatmaps)


@router.get("/summary", response_model=AnalyticsSummary, dependencies=[Depends(get_current_user)])
def get_analytics_summary(db: Session = Depends(get_db)) -> AnalyticsSummary:
    """
    Returns aggregated summary stats: total tasks this week, top performer, and streaks.
    """
    today = datetime.now().date()
    week_start = today - timedelta(days=6)

    # Total completed tasks this week
    week_total: int = (
        db.query(func.count(TaskInstance.id))
        .filter(
            TaskInstance.status == "COMPLETED",
            func.date(TaskInstance.completed_at) >= week_start,
        )
        .scalar()
    ) or 0

    # Per-user counts this week → top performer
    per_user = (
        db.query(
            User.nickname,
            func.count(TaskInstance.id).label("cnt"),
        )
        .join(TaskInstance, TaskInstance.user_id == User.id)
        .filter(
            TaskInstance.status == "COMPLETED",
            func.date(TaskInstance.completed_at) >= week_start,
        )
        .group_by(User.nickname)
        .order_by(func.count(TaskInstance.id).desc())
        .all()
    )

    top: TopPerformer | None = None
    if per_user:
        top = TopPerformer(nickname=per_user[0].nickname, count=per_user[0].cnt)

    # Streak leaderboard (all users, sorted desc)
    users = db.query(User).order_by(User.current_streak.desc()).all()
    streaks = [
        StreakInfo(nickname=str(u.nickname), current_streak=int(u.current_streak))
        for u in users
    ]

    return AnalyticsSummary(
        week_total_tasks=week_total,
        top_performer=top,
        streaks=streaks,
    )


@router.get(
    "/heatmap/details",
    response_model=HeatmapDayDetails,
    dependencies=[Depends(get_current_user)],
)
def get_heatmap_day_details(
    user_id: int = Query(..., description="User ID"),
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    db: Session = Depends(get_db),
) -> HeatmapDayDetails:
    """
    Returns the list of completed tasks for a specific user on a specific date.
    Used when clicking a heatmap cell.
    """
    user = db.query(User).filter(User.id == user_id).first()
    nickname = str(user.nickname) if user else "Unknown"

    instances = (
        db.query(TaskInstance)
        .join(Task, TaskInstance.task_id == Task.id)
        .filter(
            TaskInstance.user_id == user_id,
            TaskInstance.status == "COMPLETED",
            func.date(TaskInstance.completed_at) == date,
        )
        .all()
    )

    tasks_detail: List[HeatmapTaskDetail] = []
    for inst in instances:
        completed_str = inst.completed_at.isoformat() if inst.completed_at else ""
        tasks_detail.append(HeatmapTaskDetail(
            task_name=inst.task.name if inst.task else "Unknown",
            base_points=inst.task.base_points if inst.task else 0,
            completed_at=completed_str,
        ))

    return HeatmapDayDetails(
        user_id=user_id,
        nickname=nickname,
        date=date,
        tasks=tasks_detail,
    )
