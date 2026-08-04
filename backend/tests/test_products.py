def make_product(client, headers, **overrides):
    payload = {
        "brand": "Sapphire", "suit_name": "Lawn Suit A", "purchase_price": 2000,
        "selling_price": 3500, "quantity": 10,
    }
    payload.update(overrides)
    return client.post("/products", json=payload, headers=headers)


def test_create_and_list_product(client, auth_headers):
    r = make_product(client, auth_headers)
    assert r.status_code == 201
    r = client.get("/products", headers=auth_headers)
    assert len(r.json()) == 1


def test_duplicate_product_detection(client, auth_headers):
    make_product(client, auth_headers)
    r = make_product(client, auth_headers)
    assert r.status_code == 409
    assert "existing_product_id" in r.json()["detail"]


def test_increase_quantity_on_existing_product(client, auth_headers):
    r = make_product(client, auth_headers)
    product_id = r.json()["id"]
    r = client.post(f"/products/{product_id}/increase-quantity?additional_quantity=5", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["quantity"] == 15


def test_deactivate_product_soft_deletes(client, auth_headers):
    r = make_product(client, auth_headers)
    product_id = r.json()["id"]
    r = client.delete(f"/products/{product_id}", headers=auth_headers)
    assert r.status_code == 204
    r = client.get("/products", headers=auth_headers)
    assert len(r.json()) == 0  # active_only=True by default
    r = client.get("/products?active_only=false", headers=auth_headers)
    assert len(r.json()) == 1


def test_low_stock_uses_shop_default_threshold(client, auth_headers):
    make_product(client, auth_headers, quantity=3)  # default threshold is 5
    r = client.get("/products/low-stock", headers=auth_headers)
    assert len(r.json()) == 1


def test_low_stock_respects_per_product_override(client, auth_headers):
    make_product(client, auth_headers, quantity=10, low_stock_threshold=20)
    r = client.get("/products/low-stock", headers=auth_headers)
    assert len(r.json()) == 1


def test_update_product_saves_changes(client, auth_headers):
    r = make_product(client, auth_headers)
    product_id = r.json()["id"]
    r = client.put(
        f"/products/{product_id}",
        json={
            "brand": "Sapphire", "suit_name": "Lawn Suit A (Updated)", "purchase_price": 2200,
            "selling_price": 3800, "quantity": 12, "supplier_id": None,
        },
        headers=auth_headers,
    )
    assert r.status_code == 200
    assert r.json()["suit_name"] == "Lawn Suit A (Updated)"
    assert r.json()["quantity"] == 12


def test_update_product_on_missing_product_returns_404(client, auth_headers):
    r = client.put(
        "/products/9999",
        json={"brand": "X", "suit_name": "Y", "purchase_price": 1, "selling_price": 2, "quantity": 1},
        headers=auth_headers,
    )
    assert r.status_code == 404


def test_multi_tenant_isolation(client):
    """The single most important test in this whole suite: shop A's data
    must be completely invisible to shop B, even by direct ID guessing."""
    r = client.post(
        "/auth/signup",
        json={"shop_name": "Shop A", "email": "a@test.com", "password": "secret123"},
    )
    headers_a = {"Authorization": f"Bearer {r.json()['access_token']}"}

    r = client.post(
        "/auth/signup",
        json={"shop_name": "Shop B", "email": "b@test.com", "password": "secret123"},
    )
    headers_b = {"Authorization": f"Bearer {r.json()['access_token']}"}

    r = make_product(client, headers_a)
    product_id = r.json()["id"]

    # Shop B can't fetch it directly by ID
    r = client.get(f"/products/{product_id}", headers=headers_b)
    assert r.status_code == 404

    # Shop B's product list is empty
    r = client.get("/products", headers=headers_b)
    assert r.json() == []

    # Shop B can't update or delete it either
    r = client.delete(f"/products/{product_id}", headers=headers_b)
    assert r.status_code == 404
