def make_product(client, headers, **overrides):
    payload = {
        "brand": "Sapphire", "suit_name": "Lawn Suit A", "purchase_price": 2000,
        "selling_price": 3500, "quantity": 10,
    }
    payload.update(overrides)
    return client.post("/products", json=payload, headers=headers).json()


def test_record_sale_calculates_total_and_profit(client, auth_headers):
    product = make_product(client, auth_headers)
    r = client.post(
        "/sales", json={"product_id": product["id"], "quantity_sold": 3}, headers=auth_headers
    )
    assert r.status_code == 201
    body = r.json()
    assert body["total_amount"] == 10500.0
    assert body["profit"] == 4500.0


def test_record_sale_applies_discount(client, auth_headers):
    product = make_product(client, auth_headers)
    r = client.post(
        "/sales",
        json={"product_id": product["id"], "quantity_sold": 2, "discount": 500},
        headers=auth_headers,
    )
    body = r.json()
    assert body["total_amount"] == 6500.0  # (3500*2) - 500
    assert body["profit"] == 2500.0  # 6500 - (2000*2)


def test_record_sale_reduces_stock(client, auth_headers):
    product = make_product(client, auth_headers)
    client.post("/sales", json={"product_id": product["id"], "quantity_sold": 3}, headers=auth_headers)
    r = client.get(f"/products/{product['id']}", headers=auth_headers)
    assert r.json()["quantity"] == 7


def test_overselling_is_rejected_and_stock_unchanged(client, auth_headers):
    product = make_product(client, auth_headers, quantity=5)
    r = client.post("/sales", json={"product_id": product["id"], "quantity_sold": 6}, headers=auth_headers)
    assert r.status_code == 400
    r = client.get(f"/products/{product['id']}", headers=auth_headers)
    assert r.json()["quantity"] == 5  # unchanged


def test_zero_or_negative_quantity_rejected(client, auth_headers):
    product = make_product(client, auth_headers)
    r = client.post("/sales", json={"product_id": product["id"], "quantity_sold": 0}, headers=auth_headers)
    # 422 because Pydantic's Field(gt=0) on SaleCreate now catches this
    # before the request even reaches the router's own logic checks.
    assert r.status_code == 422


def test_partial_refund_is_proportional(client, auth_headers):
    product = make_product(client, auth_headers)
    sale = client.post(
        "/sales",
        json={"product_id": product["id"], "quantity_sold": 4, "discount": 400},
        headers=auth_headers,
    ).json()
    # total = 3500*4 - 400 = 13600, profit = 13600 - 2000*4 = 5600
    r = client.post(
        "/refunds", json={"sale_id": sale["id"], "quantity_refunded": 1}, headers=auth_headers
    )
    assert r.status_code == 201
    refund = r.json()
    assert refund["refund_amount"] == 3400.0  # 13600 / 4
    assert refund["profit_reversed"] == 1400.0  # 5600 / 4


def test_refund_restocks_product(client, auth_headers):
    product = make_product(client, auth_headers)
    sale = client.post(
        "/sales", json={"product_id": product["id"], "quantity_sold": 3}, headers=auth_headers
    ).json()
    client.post("/refunds", json={"sale_id": sale["id"], "quantity_refunded": 2}, headers=auth_headers)
    r = client.get(f"/products/{product['id']}", headers=auth_headers)
    assert r.json()["quantity"] == 9  # 10 - 3 + 2


def test_double_refund_protection(client, auth_headers):
    product = make_product(client, auth_headers)
    sale = client.post(
        "/sales", json={"product_id": product["id"], "quantity_sold": 3}, headers=auth_headers
    ).json()
    r1 = client.post("/refunds", json={"sale_id": sale["id"], "quantity_refunded": 3}, headers=auth_headers)
    assert r1.status_code == 201
    r2 = client.post("/refunds", json={"sale_id": sale["id"], "quantity_refunded": 1}, headers=auth_headers)
    assert r2.status_code == 400  # nothing left to refund


def test_refund_across_two_partial_calls(client, auth_headers):
    product = make_product(client, auth_headers)
    sale = client.post(
        "/sales", json={"product_id": product["id"], "quantity_sold": 5}, headers=auth_headers
    ).json()
    r1 = client.post("/refunds", json={"sale_id": sale["id"], "quantity_refunded": 2}, headers=auth_headers)
    assert r1.status_code == 201
    r2 = client.post("/refunds", json={"sale_id": sale["id"], "quantity_refunded": 3}, headers=auth_headers)
    assert r2.status_code == 201  # exactly the remaining amount
    r3 = client.post("/refunds", json={"sale_id": sale["id"], "quantity_refunded": 1}, headers=auth_headers)
    assert r3.status_code == 400  # now fully refunded


def test_sale_on_another_shops_product_is_rejected(client):
    r = client.post(
        "/auth/signup", json={"shop_name": "Shop A", "email": "a@test.com", "password": "secret123"}
    )
    headers_a = {"Authorization": f"Bearer {r.json()['access_token']}"}
    r = client.post(
        "/auth/signup", json={"shop_name": "Shop B", "email": "b@test.com", "password": "secret123"}
    )
    headers_b = {"Authorization": f"Bearer {r.json()['access_token']}"}

    product = make_product(client, headers_a)
    r = client.post(
        "/sales", json={"product_id": product["id"], "quantity_sold": 1}, headers=headers_b
    )
    assert r.status_code == 404
