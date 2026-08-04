def make_product(client, headers, **overrides):
    payload = {
        "brand": "Sapphire", "suit_name": "Lawn Suit A", "purchase_price": 2000,
        "selling_price": 3500, "quantity": 10,
    }
    payload.update(overrides)
    return client.post("/products", json=payload, headers=headers).json()


def test_today_totals_reflect_sale(client, auth_headers):
    product = make_product(client, auth_headers)
    client.post("/sales", json={"product_id": product["id"], "quantity_sold": 2}, headers=auth_headers)
    r = client.get("/dashboard/today", headers=auth_headers)
    assert r.json() == {"sales": 7000.0, "profit": 3000.0}


def test_today_totals_net_of_refund(client, auth_headers):
    product = make_product(client, auth_headers)
    sale = client.post(
        "/sales", json={"product_id": product["id"], "quantity_sold": 2}, headers=auth_headers
    ).json()
    client.post("/refunds", json={"sale_id": sale["id"], "quantity_refunded": 1}, headers=auth_headers)
    r = client.get("/dashboard/today", headers=auth_headers)
    # 7000 - 3500 = 3500 net sales, 3000 - 1500 = 1500 net profit
    assert r.json() == {"sales": 3500.0, "profit": 1500.0}


def test_inventory_value(client, auth_headers):
    make_product(client, auth_headers, purchase_price=2000, quantity=10)
    make_product(client, auth_headers, suit_name="Lawn Suit B", purchase_price=1000, quantity=5)
    r = client.get("/dashboard/inventory-value", headers=auth_headers)
    body = r.json()
    assert body["inventory_value"] == 25000.0  # 2000*10 + 1000*5
    assert body["total_stock"] == 15


def test_customer_create_and_list(client, auth_headers):
    r = client.post("/customers", json={"name": "Ayesha", "phone": "0300-1234567"}, headers=auth_headers)
    assert r.status_code == 201
    r = client.get("/customers", headers=auth_headers)
    assert len(r.json()) == 1
    assert r.json()[0]["name"] == "Ayesha"


def test_customer_total_spent(client, auth_headers):
    customer = client.post("/customers", json={"name": "Ayesha"}, headers=auth_headers).json()
    product = make_product(client, auth_headers)
    client.post(
        "/sales",
        json={"product_id": product["id"], "quantity_sold": 2, "customer_id": customer["id"]},
        headers=auth_headers,
    )
    r = client.get(f"/customers/{customer['id']}/total-spent", headers=auth_headers)
    assert r.json()["total_spent"] == 7000.0


def test_supplier_create_and_list(client, auth_headers):
    r = client.post("/suppliers", json={"name": "Al-Karam Textiles"}, headers=auth_headers)
    assert r.status_code == 201
    r = client.get("/suppliers", headers=auth_headers)
    assert len(r.json()) == 1
