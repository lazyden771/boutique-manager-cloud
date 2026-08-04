"""One-off manual smoke test - not part of the pytest suite. Exercises
signup -> login -> create product -> record sale -> refund -> dashboard,
end to end, using FastAPI's TestClient (in-process, no real server needed)."""

import os
os.environ["DATABASE_URL"] = "sqlite:///./smoke_test.db"

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Signup
r = client.post("/auth/signup", json={
    "shop_name": "Test Boutique", "email": "owner@test.com", "password": "secret123"
})
assert r.status_code == 201, r.text
token = r.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print("signup OK ->", r.json())

# Login
r = client.post("/auth/login", json={"email": "owner@test.com", "password": "secret123"})
assert r.status_code == 200, r.text
print("login OK")

# Wrong password
r = client.post("/auth/login", json={"email": "owner@test.com", "password": "wrong"})
assert r.status_code == 401
print("wrong password correctly rejected")

# Create product
r = client.post("/products", json={
    "brand": "Sapphire", "suit_name": "Lawn Suit A", "purchase_price": 2000,
    "selling_price": 3500, "quantity": 10
}, headers=headers)
assert r.status_code == 201, r.text
product = r.json()
print("product created ->", product["id"])

# Duplicate detection
r = client.post("/products", json={
    "brand": "Sapphire", "suit_name": "Lawn Suit A", "purchase_price": 2000,
    "selling_price": 3500, "quantity": 5
}, headers=headers)
assert r.status_code == 409
print("duplicate correctly rejected ->", r.json())

# Record sale
r = client.post("/sales", json={"product_id": product["id"], "quantity_sold": 3}, headers=headers)
assert r.status_code == 201, r.text
sale = r.json()
assert sale["total_amount"] == 10500.0
assert sale["profit"] == 4500.0
print("sale recorded ->", sale)

# Stock reduced
r = client.get(f"/products/{product['id']}", headers=headers)
assert r.json()["quantity"] == 7
print("stock correctly reduced to 7")

# Overselling protection
r = client.post("/sales", json={"product_id": product["id"], "quantity_sold": 999}, headers=headers)
assert r.status_code == 400
print("overselling correctly rejected ->", r.json())

# Partial refund
r = client.post("/refunds", json={"sale_id": sale["id"], "quantity_refunded": 1}, headers=headers)
assert r.status_code == 201, r.text
refund = r.json()
assert refund["refund_amount"] == 3500.0
print("partial refund OK ->", refund)

# Stock restored
r = client.get(f"/products/{product['id']}", headers=headers)
assert r.json()["quantity"] == 8
print("stock correctly restored to 8")

# Over-refund protection (already refunded 1 of 3, try refunding 3 more)
r = client.post("/refunds", json={"sale_id": sale["id"], "quantity_refunded": 3}, headers=headers)
assert r.status_code == 400
print("over-refund correctly rejected ->", r.json())

# Multi-tenant isolation: second shop can't see first shop's product
r = client.post("/auth/signup", json={
    "shop_name": "Other Boutique", "email": "other@test.com", "password": "secret123"
})
other_token = r.json()["access_token"]
other_headers = {"Authorization": f"Bearer {other_token}"}
r = client.get(f"/products/{product['id']}", headers=other_headers)
assert r.status_code == 404
print("tenant isolation confirmed: other shop cannot see first shop's product")

# Dashboard
r = client.get("/dashboard/today", headers=headers)
assert r.status_code == 200
print("dashboard today ->", r.json())

print("\nALL SMOKE TESTS PASSED")
