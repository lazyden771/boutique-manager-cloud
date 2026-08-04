from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_account
from app.models import Account
from app.schemas import AccountOut, AccountSettingsUpdate

router = APIRouter(prefix="/account", tags=["account"])


@router.get("", response_model=AccountOut)
def get_account(account: Account = Depends(get_current_account)):
    return account


@router.put("", response_model=AccountOut)
def update_account(
    payload: AccountSettingsUpdate,
    db: Session = Depends(get_db),
    account: Account = Depends(get_current_account),
):
    """
    Shop-level settings: name, currency, and the default low-stock
    threshold used across the dashboard and inventory low-stock list
    whenever a product doesn't set its own override. This is the piece
    that was missing entirely before - the Account model always had these
    fields, but nothing let a shop actually change them after signup.
    """
    account.shop_name = payload.shop_name
    account.currency = payload.currency
    account.low_stock_threshold = payload.low_stock_threshold
    db.commit()
    db.refresh(account)
    return account
