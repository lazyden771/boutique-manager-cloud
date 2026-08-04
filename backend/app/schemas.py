"""
Pydantic schemas - these define what JSON shapes the API accepts and
returns. Kept separate from the ORM models (app/models.py) on purpose:
the DB model can have fields (like password_hash) that should never be
sent back to a client.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict, Field


# ---- Auth ----

class SignupRequest(BaseModel):
    shop_name: str = Field(min_length=1)
    email: EmailStr
    # 8 characters is a floor, not a real strength policy - fine for a small
    # boutique app, but note this is not enforcing complexity, just length.
    password: str = Field(min_length=8)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    shop_name: str
    currency: str


# ---- Product ----

class ProductCreate(BaseModel):
    brand: str = Field(min_length=1)
    product_code: Optional[str] = None
    suit_name: str = Field(min_length=1)
    colour: Optional[str] = None
    purchase_price: float = Field(ge=0)
    selling_price: float = Field(ge=0)
    quantity: int = Field(ge=0)
    low_stock_threshold: Optional[int] = Field(default=None, ge=0)
    notes: Optional[str] = None
    image_url: Optional[str] = None
    supplier_id: Optional[int] = None


class ProductUpdate(ProductCreate):
    pass


class ProductOut(ProductCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


# ---- Customer / Supplier ----

class CustomerCreate(BaseModel):
    name: str = Field(min_length=1)
    phone: Optional[str] = None


class CustomerOut(CustomerCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


class SupplierCreate(BaseModel):
    name: str = Field(min_length=1)
    phone: Optional[str] = None
    notes: Optional[str] = None


class SupplierOut(SupplierCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


# ---- Sale / Refund ----

class SaleCreate(BaseModel):
    product_id: int
    quantity_sold: int = Field(gt=0)
    discount: float = Field(default=0.0, ge=0)
    customer_id: Optional[int] = None


class SaleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    product_id: int
    customer_id: Optional[int]
    quantity_sold: int
    unit_price: float
    unit_cost: float
    discount: float
    total_amount: float
    profit: float
    sale_date: datetime


class RefundCreate(BaseModel):
    sale_id: int
    quantity_refunded: int = Field(gt=0)
    reason: Optional[str] = None


class RefundOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    sale_id: int
    product_id: int
    quantity_refunded: int
    refund_amount: float
    profit_reversed: float
    reason: Optional[str]
    refund_date: datetime
