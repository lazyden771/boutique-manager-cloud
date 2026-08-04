from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_account
from app.models import Account, Supplier
from app.schemas import SupplierCreate, SupplierOut

router = APIRouter(prefix="/suppliers", tags=["suppliers"])


@router.get("", response_model=List[SupplierOut])
def list_suppliers(db: Session = Depends(get_db), account: Account = Depends(get_current_account)):
    return db.query(Supplier).filter(Supplier.account_id == account.id).order_by(Supplier.name).all()


@router.post("", response_model=SupplierOut, status_code=201)
def create_supplier(
    payload: SupplierCreate, db: Session = Depends(get_db), account: Account = Depends(get_current_account)
):
    supplier = Supplier(account_id=account.id, **payload.model_dump())
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return supplier
