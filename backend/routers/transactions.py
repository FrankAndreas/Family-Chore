import datetime
from typing import List, Optional
import logging

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from .. import schemas, crud, models
from ..database import get_db
from ..dependencies import get_current_user, get_current_admin_user, require_self_or_admin

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Transactions"])


@router.get("/users/{user_id}/transactions",
            response_model=List[schemas.Transaction])
def read_user_transactions(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    txn_type: Optional[str] = None,
    search: Optional[str] = Query(default=None, max_length=200),
    start_date: Optional[datetime.datetime] = None,
    end_date: Optional[datetime.datetime] = None,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get history for a specific user."""
    require_self_or_admin(current_user, user_id)
    return crud.get_user_transactions(
        db, user_id=user_id, skip=skip, limit=limit,
        txn_type=txn_type, search=search, start_date=start_date, end_date=end_date
    )


@router.get("/transactions", response_model=List[schemas.Transaction], dependencies=[Depends(get_current_admin_user)])
def read_all_transactions(
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    txn_type: Optional[str] = None,
    search: Optional[str] = Query(default=None, max_length=200),
    start_date: Optional[datetime.datetime] = None,
    end_date: Optional[datetime.datetime] = None,
    db: Session = Depends(get_db)
):
    """Get global history (for Admin/Family Dashboard)."""
    return crud.get_all_transactions(
        db, skip=skip, limit=limit,
        user_id=user_id, txn_type=txn_type, search=search, start_date=start_date, end_date=end_date
    )
