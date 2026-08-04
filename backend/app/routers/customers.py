from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_account
from app.models import Account, Customer, Sale
from app.schemas import CustomerCreate, CustomerOut

router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("", response_model=List[CustomerOut])
def list_customers(db: Session = Depends(get_db), account: Account = Depends(get_current_account)):
    return db.query(Customer).filter(Customer.account_id == account.id).order_by(Customer.name).all()


@router.post("", response_model=CustomerOut, status_code=201)
def create_customer(
    payload: CustomerCreate, db: Session = Depends(get_db), account: Account = Depends(get_current_account)
):
    customer = Customer(account_id=account.id, **payload.model_dump())
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


@router.get("/{customer_id}/total-spent")
def customer_total_spent(
    customer_id: int, db: Session = Depends(get_db), account: Account = Depends(get_current_account)
):
    customer = (
        db.query(Customer)
        .filter(Customer.id == customer_id, Customer.account_id == account.id)
        .first()
    )
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found.")
    total = (
        db.query(Sale)
        .filter(Sale.customer_id == customer_id, Sale.account_id == account.id)
        .with_entities(Sale.total_amount)
        .all()
    )
    return {"total_spent": round(sum(t[0] for t in total), 2)}
