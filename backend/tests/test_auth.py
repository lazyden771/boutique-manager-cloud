def test_signup_creates_account_and_returns_token(client):
    r = client.post(
        "/auth/signup",
        json={"shop_name": "Test Boutique", "email": "owner@test.com", "password": "secret123"},
    )
    assert r.status_code == 201
    body = r.json()
    assert body["shop_name"] == "Test Boutique"
    assert body["currency"] == "PKR"
    assert body["access_token"]


def test_signup_rejects_duplicate_email(client):
    payload = {"shop_name": "A", "email": "dupe@test.com", "password": "secret123"}
    client.post("/auth/signup", json=payload)
    r = client.post("/auth/signup", json=payload)
    assert r.status_code == 400


def test_login_succeeds_with_correct_credentials(client):
    client.post(
        "/auth/signup",
        json={"shop_name": "Test", "email": "owner@test.com", "password": "secret123"},
    )
    r = client.post("/auth/login", json={"email": "owner@test.com", "password": "secret123"})
    assert r.status_code == 200
    assert r.json()["access_token"]


def test_login_rejects_wrong_password(client):
    client.post(
        "/auth/signup",
        json={"shop_name": "Test", "email": "owner@test.com", "password": "secret123"},
    )
    r = client.post("/auth/login", json={"email": "owner@test.com", "password": "wrong"})
    assert r.status_code == 401


def test_login_rejects_unknown_email(client):
    r = client.post("/auth/login", json={"email": "nobody@test.com", "password": "secret123"})
    assert r.status_code == 401


def test_login_locks_out_after_repeated_failures(client):
    client.post(
        "/auth/signup",
        json={"shop_name": "Test", "email": "owner@test.com", "password": "secret123"},
    )
    for _ in range(5):
        r = client.post("/auth/login", json={"email": "owner@test.com", "password": "wrong"})
        assert r.status_code == 401

    # 6th attempt, even with the CORRECT password, is now blocked
    r = client.post("/auth/login", json={"email": "owner@test.com", "password": "secret123"})
    assert r.status_code == 429


def test_successful_login_clears_previous_failed_attempts(client):
    client.post(
        "/auth/signup",
        json={"shop_name": "Test", "email": "owner@test.com", "password": "secret123"},
    )
    for _ in range(3):
        client.post("/auth/login", json={"email": "owner@test.com", "password": "wrong"})

    r = client.post("/auth/login", json={"email": "owner@test.com", "password": "secret123"})
    assert r.status_code == 200  # 3 failures isn't enough to lock out, and this succeeds

    # After a successful login, the failure count should be reset - two
    # more wrong attempts shouldn't be treated as attempts 4 and 5.
    for _ in range(2):
        client.post("/auth/login", json={"email": "owner@test.com", "password": "wrong"})
    r = client.post("/auth/login", json={"email": "owner@test.com", "password": "secret123"})
    assert r.status_code == 200  # still not locked out


def test_protected_endpoint_rejects_missing_token(client):
    r = client.get("/products")
    assert r.status_code == 401


def test_protected_endpoint_rejects_garbage_token(client):
    r = client.get("/products", headers={"Authorization": "Bearer not-a-real-token"})
    assert r.status_code == 401
