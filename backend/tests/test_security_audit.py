import pytest


def make_product(client, headers, **overrides):
    payload = {
        "brand": "Sapphire", "suit_name": "Lawn Suit A", "purchase_price": 2000,
        "selling_price": 3500, "quantity": 10,
    }
    payload.update(overrides)
    return client.post("/products", json=payload, headers=headers)


# ---- DATABASE_URL scheme normalization ----

def test_postgres_scheme_is_normalized_to_postgresql(monkeypatch):
    """Railway hands out 'postgres://...' - SQLAlchemy 1.4+ requires
    'postgresql://...'. Without normalization, the app crashes on startup
    the moment a real Postgres DB is attached."""
    monkeypatch.setenv("DATABASE_URL", "postgres://user:pass@host:5432/dbname")
    import importlib
    import app.config as config
    importlib.reload(config)
    assert config.DATABASE_URL.startswith("postgresql://")
    assert config.DATABASE_URL == "postgresql://user:pass@host:5432/dbname"
    # Reload again with no override so later tests aren't affected by this
    # module-level mutation.
    monkeypatch.delenv("DATABASE_URL", raising=False)
    importlib.reload(config)


# ---- Password / input validation floors ----

def test_signup_rejects_short_password(client):
    r = client.post(
        "/auth/signup",
        json={"shop_name": "Test", "email": "owner@test.com", "password": "1234"},
    )
    assert r.status_code == 422


def test_signup_rejects_empty_shop_name(client):
    r = client.post(
        "/auth/signup",
        json={"shop_name": "", "email": "owner@test.com", "password": "secret123"},
    )
    assert r.status_code == 422


def test_product_rejects_negative_price(client, auth_headers):
    r = make_product(client, auth_headers, purchase_price=-100)
    assert r.status_code == 422


def test_product_rejects_negative_quantity(client, auth_headers):
    r = make_product(client, auth_headers, quantity=-1)
    assert r.status_code == 422


def test_sale_rejects_negative_discount(client, auth_headers):
    product = make_product(client, auth_headers).json()
    r = client.post(
        "/sales",
        json={"product_id": product["id"], "quantity_sold": 1, "discount": -50},
        headers=auth_headers,
    )
    assert r.status_code == 422


# ---- Cross-tenant reference validation ----

def test_product_cannot_link_to_another_shops_supplier(client):
    r = client.post(
        "/auth/signup", json={"shop_name": "Shop A", "email": "a@test.com", "password": "secret123"}
    )
    headers_a = {"Authorization": f"Bearer {r.json()['access_token']}"}
    r = client.post(
        "/auth/signup", json={"shop_name": "Shop B", "email": "b@test.com", "password": "secret123"}
    )
    headers_b = {"Authorization": f"Bearer {r.json()['access_token']}"}

    supplier_b = client.post("/suppliers", json={"name": "B's Textiles"}, headers=headers_b).json()

    r = make_product(client, headers_a, supplier_id=supplier_b["id"])
    assert r.status_code == 400


def test_product_can_link_to_own_shops_supplier(client, auth_headers):
    supplier = client.post("/suppliers", json={"name": "My Textiles"}, headers=auth_headers).json()
    r = make_product(client, auth_headers, supplier_id=supplier["id"])
    assert r.status_code == 201
    assert r.json()["supplier_id"] == supplier["id"]


def test_sale_cannot_link_to_another_shops_customer(client):
    r = client.post(
        "/auth/signup", json={"shop_name": "Shop A", "email": "a@test.com", "password": "secret123"}
    )
    headers_a = {"Authorization": f"Bearer {r.json()['access_token']}"}
    r = client.post(
        "/auth/signup", json={"shop_name": "Shop B", "email": "b@test.com", "password": "secret123"}
    )
    headers_b = {"Authorization": f"Bearer {r.json()['access_token']}"}

    customer_b = client.post("/customers", json={"name": "B's Customer"}, headers=headers_b).json()
    product_a = make_product(client, headers_a).json()

    r = client.post(
        "/sales",
        json={"product_id": product_a["id"], "quantity_sold": 1, "customer_id": customer_b["id"]},
        headers=headers_a,
    )
    assert r.status_code == 400
