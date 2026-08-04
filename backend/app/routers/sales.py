from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_account
from app.models import Account, Product, Sale, Customer
from app.schemas import SaleCreate, SaleOut

router = APIRouter(prefix="/sales", tags=["sales"])


@router.get("", response_model=List[SaleOut])
def list_recent_sales(
    limit: int = 10,
    db: Session = Depends(get_db),
    account: Account = Depends(get_current_account),
):
    return (
        db.query(Sale)
        .filter(Sale.account_id == account.id)
        .order_by(Sale.sale_date.desc())
        .limit(limit)
        .all()
    )


@router.post("", response_model=SaleOut, status_code=201)
def record_sale(
    payload: SaleCreate,
    db: Session = Depends(get_db),
    account: Account = Depends(get_current_account),
):
    """
    The single most important endpoint in the whole app - same role as
    record_sale() in the desktop app's sale_repository.py. Validates stock,
    calculates total/profit, reduces stock, and saves the sale - all inside
    one DB transaction, so a failure partway through leaves nothing changed
    rather than a sale with no stock reduction (or vice versa).
    """
    if payload.quantity_sold <= 0:
        raise HTTPException(status_code=400, detail="Quantity sold must be greater than zero.")

    product = (
        db.query(Product)
        .filter(Product.id == payload.product_id, Product.account_id == account.id)
        .first()
    )
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")
    if payload.quantity_sold > product.quantity:
        raise HTTPException(
            status_code=400,
            detail=f"Only {product.quantity} unit(s) of '{product.suit_name}' in stock.",
        )

    if payload.customer_id is not None:
        customer = (
            db.query(Customer)
            .filter(Customer.id == payload.customer_id, Customer.account_id == account.id)
            .first()
        )
        if not customer:
            raise HTTPException(status_code=400, detail="Customer not found for this shop.")

    unit_price = product.selling_price
    unit_cost = product.purchase_price
    total_amount = round((unit_price * payload.quantity_sold) - payload.discount, 2)
    profit = round(total_amount - (unit_cost * payload.quantity_sold), 2)

    sale = Sale(
        account_id=account.id,
        product_id=product.id,
        customer_id=payload.customer_id,
        quantity_sold=payload.quantity_sold,
        unit_price=unit_price,
        unit_cost=unit_cost,
        discount=payload.discount,
        total_amount=total_amount,
        profit=profit,
    )
    try:
        product.quantity -= payload.quantity_sold
        db.add(sale)
        db.commit()  # sale insert + stock update commit together, or neither does
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Could not record sale. Nothing was changed.")

    db.refresh(sale)
    return sale
