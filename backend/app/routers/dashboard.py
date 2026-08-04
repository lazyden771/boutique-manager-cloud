"""
Dashboard + Reports aggregation endpoints.

One deliberate simplification vs. the desktop app: the desktop version
converts UTC timestamps to the shop's LOCAL time before deciding what
counts as "today" (see the note in the original sale_repository.py) - it
could do that because it only ever ran on one shop's own PC, in one
timezone. Here, "today" and "this month" are calculated in UTC calendar
terms, because a single shop's account could reasonably be accessed from
different timezones (phone while traveling, etc.), and there's no single
correct "local" without asking the shop to set one. If a day-boundary-off-
by-a-few-hours issue ever bites, the fix is to add a timezone field to
Account and convert using it - flagging this now so it's not a silent
behavior change.
"""

from datetime import datetime, timezone, date, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.deps import get_current_account
from app.models import Account, Sale, Refund, Product

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def _net_totals(db: Session, account_id: int, start: datetime, end: datetime) -> dict:
    sales = (
        db.query(
            func.coalesce(func.sum(Sale.total_amount), 0),
            func.coalesce(func.sum(Sale.profit), 0),
        )
        .filter(Sale.account_id == account_id, Sale.sale_date >= start, Sale.sale_date < end)
        .first()
    )
    refunds = (
        db.query(
            func.coalesce(func.sum(Refund.refund_amount), 0),
            func.coalesce(func.sum(Refund.profit_reversed), 0),
        )
        .filter(Refund.account_id == account_id, Refund.refund_date >= start, Refund.refund_date < end)
        .first()
    )
    return {
        "sales": round(sales[0] - refunds[0], 2),
        "profit": round(sales[1] - refunds[1], 2),
    }


@router.get("/today")
def today_totals(db: Session = Depends(get_db), account: Account = Depends(get_current_account)):
    now = datetime.now(timezone.utc)
    start = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
    end = start + timedelta(days=1)
    return _net_totals(db, account.id, start, end)


@router.get("/month-profit")
def month_profit(db: Session = Depends(get_db), account: Account = Depends(get_current_account)):
    now = datetime.now(timezone.utc)
    start = datetime(now.year, now.month, 1, tzinfo=timezone.utc)
    next_month = start.month % 12 + 1
    next_year = start.year + (1 if start.month == 12 else 0)
    end = datetime(next_year, next_month, 1, tzinfo=timezone.utc)
    return {"profit": _net_totals(db, account.id, start, end)["profit"]}


@router.get("/range")
def net_totals_between(
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db),
    account: Account = Depends(get_current_account),
):
    start = datetime(start_date.year, start_date.month, start_date.day, tzinfo=timezone.utc)
    end = datetime(end_date.year, end_date.month, end_date.day, tzinfo=timezone.utc) + timedelta(days=1)
    return _net_totals(db, account.id, start, end)


@router.get("/inventory-value")
def inventory_value(db: Session = Depends(get_db), account: Account = Depends(get_current_account)):
    total = (
        db.query(func.coalesce(func.sum(Product.purchase_price * Product.quantity), 0))
        .filter(Product.account_id == account.id, Product.is_active == True)  # noqa: E712
        .scalar()
    )
    stock_count = (
        db.query(func.coalesce(func.sum(Product.quantity), 0))
        .filter(Product.account_id == account.id, Product.is_active == True)  # noqa: E712
        .scalar()
    )
    return {"inventory_value": round(total, 2), "total_stock": stock_count}


@router.get("/best-selling-products")
def best_selling_products(
    limit: int = 5, db: Session = Depends(get_db), account: Account = Depends(get_current_account)
):
    rows = (
        db.query(
            Product.suit_name,
            Product.brand,
            func.sum(Sale.quantity_sold).label("total_sold"),
        )
        .join(Sale, Sale.product_id == Product.id)
        .filter(Sale.account_id == account.id)
        .group_by(Product.id)
        .order_by(func.sum(Sale.quantity_sold).desc())
        .limit(limit)
        .all()
    )
    return [{"suit_name": r[0], "brand": r[1], "total_sold": r[2]} for r in rows]
