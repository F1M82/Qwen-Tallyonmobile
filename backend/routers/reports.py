"""Reports router — trial balance, P&L, balance sheet, outstanding"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from database import get_db
from routers.auth import get_current_user, User

router = APIRouter()


def _fiscal_year_start() -> date:
    today = date.today()
    year = today.year if today.month >= 4 else today.year - 1
    return date(year, 4, 1)


def _fiscal_year_end() -> date:
    today = date.today()
    year = today.year if today.month < 4 else today.year + 1
    return date(year, 3, 31)


@router.get("/trial-balance")
def trial_balance(
    from_date: Optional[date] = Query(default=None),
    to_date: Optional[date] = Query(default=None),
    company_id: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from_date = from_date or _fiscal_year_start()
    to_date = to_date or _fiscal_year_end()
    return {
        "from_date": str(from_date),
        "to_date": str(to_date),
        "assets": 0.0,
        "liabilities": 0.0,
        "outstanding": 0.0,
        "data": [],
    }


@router.get("/profit-loss")
def profit_loss(
    from_date: Optional[date] = Query(default=None),
    to_date: Optional[date] = Query(default=None),
    company_id: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from_date = from_date or _fiscal_year_start()
    to_date = to_date or _fiscal_year_end()
    return {
        "from_date": str(from_date), "to_date": str(to_date),
        "income": 0.0, "expenses": 0.0, "net_profit": 0.0,
    }


@router.get("/balance-sheet")
def balance_sheet(
    as_of_date: Optional[date] = Query(default=None),
    company_id: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return {"as_of_date": str(as_of_date or date.today()), "assets": [], "liabilities": []}


@router.get("/outstanding")
def outstanding(
    party_type: str = Query(default="Sundry Debtors"),
    company_id: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return {"party_type": party_type, "items": [], "total": 0.0}
