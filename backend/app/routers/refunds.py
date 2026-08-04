from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.deps import get_current_account
from app.models import Account, Sale, Product, Refund
from app.schemas import RefundCreate, RefundOut

router = APIRouter(prefix="/refunds", tags=["refunds"])


@router.get("", response_model=List[RefundOut])
def list_recent_refunds(
    limit: int = 15,
    db: Session = Depends(get_db),
    account: Account = Depends(get_current_account),
):
    return (
        db.query(Refund)
        .filter(Refund.account_id == account.id)
        .order_by(Refund.refund_date.desc())
        .limit(limit)
        .all()
    )


@router.post("", response_model=RefundOut, status_code=201)
def process_refund(
    payload: RefundCreate,
    db: Session = Depends(get_db),
    account: Account = Depends(get_current_account),
):
    """
    Same rules as the desktop app's process_refund(): validates the refund
    doesn't exceed what's left on the sale (supports partial + protects
    against double refunds), calculates the refund proportionally so a
    discount on the original sale is honoured correctly, restocks the
    product, and records the refund - all atomically.
    """
    if payload.quantity_refunded <= 0:
        raise HTTPException(status_code=400, detail="Quantity to refund must be greater than zero.")

    sale = (
        db.query(Sale)
        .filter(Sale.id == payload.sale_id, Sale.account_id == account.id)
        .first()
    )
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found.")

    already_refunded = (
        db.query(func.coalesce(func.sum(Refund.quantity_refunded), 0))
        .filter(Refund.sale_id == sale.id)
        .scalar()
    )
    remaining = sale.quantity_sold - already_refunded
    if payload.quantity_refunded > remaining:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Only {remaining} unit(s) from this sale can still be refunded "
                f"({already_refunded} already refunded)."
            ),
        )

    proportion = payload.quantity_refunded / sale.quantity_sold
    refund_amount = round(sale.total_amount * proportion, 2)
    profit_reversed = round(sale.profit * proportion, 2)

    product = db.query(Product).filter(Product.id == sale.product_id, Product.account_id == account.id).first()

    refund = Refund(
        account_id=account.id,
        sale_id=sale.id,
        product_id=sale.product_id,
        quantity_refunded=payload.quantity_refunded,
        refund_amount=refund_amount,
        profit_reversed=profit_reversed,
        reason=payload.reason,
    )
    try:
        if product:
            product.quantity += payload.quantity_refunded
        db.add(refund)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Could not process refund. Nothing was changed.")

    db.refresh(refund)
    return refund
