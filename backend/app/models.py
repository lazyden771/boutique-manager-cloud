"""
ORM models. The one rule that matters most in this whole file: every table
except `Account` itself has an `account_id` foreign key, and every query in
every router MUST filter by the logged-in user's account_id. That's the
entire mechanism keeping your shop's data separate from a friend's shop.
"""

from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Text
)
from sqlalchemy.orm import relationship
from app.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class Account(Base):
    """One row per boutique/shop. This IS the tenant."""
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True)
    shop_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    currency = Column(String, default="PKR")
    low_stock_threshold = Column(Integer, default=5)
    created_at = Column(DateTime, default=utcnow)


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    phone = Column(String)
    notes = Column(Text)


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    phone = Column(String)


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False, index=True)
    brand = Column(String, nullable=False)
    product_code = Column(String)
    suit_name = Column(String, nullable=False)
    colour = Column(String)
    purchase_price = Column(Float, nullable=False)
    selling_price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False, default=0)
    low_stock_threshold = Column(Integer)
    notes = Column(Text)
    image_url = Column(String)  # Cloudinary URL, not a local file path
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)


class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    quantity_sold = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    unit_cost = Column(Float, nullable=False)
    discount = Column(Float, default=0.0)
    total_amount = Column(Float, nullable=False)
    profit = Column(Float, nullable=False)
    sale_date = Column(DateTime, default=utcnow)


class Refund(Base):
    __tablename__ = "refunds"

    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity_refunded = Column(Integer, nullable=False)
    refund_amount = Column(Float, nullable=False)
    profit_reversed = Column(Float, nullable=False)
    reason = Column(Text)
    refund_date = Column(DateTime, default=utcnow)
