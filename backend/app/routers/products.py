from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.deps import get_current_account
from app.models import Account, Product, Supplier
from app.schemas import ProductCreate, ProductUpdate, ProductOut
from app.image_upload import upload_product_image

router = APIRouter(prefix="/products", tags=["products"])

MAX_IMAGE_SIZE_BYTES = 8 * 1024 * 1024  # 8MB - generous for a phone photo, small enough to reject junk


def _validate_supplier_belongs_to_account(db: Session, supplier_id: Optional[int], account_id: int) -> None:
    """Without this check, one shop could link a product to another shop's
    supplier_id (e.g. by guessing small sequential IDs) - not a data leak
    on its own since supplier details still aren't returned, but it's a
    cross-tenant reference that should never be allowed to form."""
    if supplier_id is None:
        return
    exists = (
        db.query(Supplier)
        .filter(Supplier.id == supplier_id, Supplier.account_id == account_id)
        .first()
    )
    if not exists:
        raise HTTPException(status_code=400, detail="Supplier not found for this shop.")


@router.get("", response_model=List[ProductOut])
def list_products(
    search: Optional[str] = None,
    active_only: bool = True,
    db: Session = Depends(get_db),
    account: Account = Depends(get_current_account),
):
    query = db.query(Product).filter(Product.account_id == account.id)
    if active_only:
        query = query.filter(Product.is_active == True)  # noqa: E712
    if search:
        like = f"%{search}%"
        query = query.filter(
            or_(
                Product.brand.ilike(like),
                Product.suit_name.ilike(like),
                Product.product_code.ilike(like),
                Product.colour.ilike(like),
            )
        )
    return query.order_by(Product.brand, Product.suit_name).all()


@router.get("/low-stock", response_model=List[ProductOut])
def low_stock_products(
    db: Session = Depends(get_db), account: Account = Depends(get_current_account)
):
    threshold = account.low_stock_threshold
    products = (
        db.query(Product)
        .filter(Product.account_id == account.id, Product.is_active == True)  # noqa: E712
        .all()
    )
    # low_stock_threshold is per-product optional override, falling back to
    # the shop's default - same rule as the desktop app.
    return sorted(
        [p for p in products if p.quantity <= (p.low_stock_threshold or threshold)],
        key=lambda p: p.quantity,
    )


@router.get("/{product_id}", response_model=ProductOut)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    account: Account = Depends(get_current_account),
):
    product = (
        db.query(Product)
        .filter(Product.id == product_id, Product.account_id == account.id)
        .first()
    )
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")
    return product


@router.post("", response_model=ProductOut, status_code=201)
def create_product(
    payload: ProductCreate,
    db: Session = Depends(get_db),
    account: Account = Depends(get_current_account),
):
    # Duplicate detection: same brand+name+colour+code for this shop.
    # Caller (frontend) is expected to warn the user and offer
    # "increase quantity instead" - this endpoint just reports the match.
    existing = (
        db.query(Product)
        .filter(
            Product.account_id == account.id,
            Product.is_active == True,  # noqa: E712
            Product.brand == payload.brand,
            Product.suit_name == payload.suit_name,
            Product.colour == payload.colour,
            Product.product_code == payload.product_code,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=409,
            detail={
                "message": "A matching product already exists.",
                "existing_product_id": existing.id,
            },
        )

    _validate_supplier_belongs_to_account(db, payload.supplier_id, account.id)

    product = Product(account_id=account.id, **payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.post("/{product_id}/increase-quantity", response_model=ProductOut)
def increase_quantity(
    product_id: int,
    additional_quantity: int,
    db: Session = Depends(get_db),
    account: Account = Depends(get_current_account),
):
    product = (
        db.query(Product)
        .filter(Product.id == product_id, Product.account_id == account.id)
        .first()
    )
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")
    if additional_quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity to add must be greater than zero.")
    product.quantity += additional_quantity
    db.commit()
    db.refresh(product)
    return product


@router.put("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: int,
    payload: ProductUpdate,
    db: Session = Depends(get_db),
    account: Account = Depends(get_current_account),
):
    product = (
        db.query(Product)
        .filter(Product.id == product_id, Product.account_id == account.id)
        .first()
    )
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")
    _validate_supplier_belongs_to_account(db, payload.supplier_id, account.id)
    for field, value in payload.model_dump().items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product


@router.post("/{product_id}/image", response_model=ProductOut)
async def upload_image(
    product_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    account: Account = Depends(get_current_account),
):
    product = (
        db.query(Product)
        .filter(Product.id == product_id, Product.account_id == account.id)
        .first()
    )
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")

    if file.content_type not in ("image/jpeg", "image/png", "image/webp"):
        raise HTTPException(status_code=400, detail="Only JPEG, PNG, or WEBP images are accepted.")

    contents = await file.read()
    if len(contents) > MAX_IMAGE_SIZE_BYTES:
        raise HTTPException(status_code=400, detail="Image must be under 8MB.")

    try:
        url = upload_product_image(contents, account.id)
    except Exception:
        raise HTTPException(status_code=502, detail="Image upload failed. Please try again.")

    product.image_url = url
    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}", status_code=204)
def deactivate_product(
    product_id: int,
    db: Session = Depends(get_db),
    account: Account = Depends(get_current_account),
):
    """Soft delete, same as the desktop app - keeps historical sales correct."""
    product = (
        db.query(Product)
        .filter(Product.id == product_id, Product.account_id == account.id)
        .first()
    )
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")
    product.is_active = False
    db.commit()
