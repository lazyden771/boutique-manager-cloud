import io
from unittest.mock import patch


def make_product(client, headers, **overrides):
    payload = {
        "brand": "Sapphire", "suit_name": "Lawn Suit A", "purchase_price": 2000,
        "selling_price": 3500, "quantity": 10,
    }
    payload.update(overrides)
    return client.post("/products", json=payload, headers=headers).json()


def test_image_upload_sets_product_image_url(client, auth_headers):
    product = make_product(client, auth_headers)
    fake_image = io.BytesIO(b"fake-jpeg-bytes")

    with patch("app.routers.products.upload_product_image") as mock_upload:
        mock_upload.return_value = "https://res.cloudinary.com/demo/image/upload/v1/test.jpg"
        r = client.post(
            f"/products/{product['id']}/image",
            files={"file": ("photo.jpg", fake_image, "image/jpeg")},
            headers=auth_headers,
        )
    assert r.status_code == 200
    assert r.json()["image_url"] == "https://res.cloudinary.com/demo/image/upload/v1/test.jpg"
    mock_upload.assert_called_once()


def test_image_upload_rejects_wrong_file_type(client, auth_headers):
    product = make_product(client, auth_headers)
    fake_file = io.BytesIO(b"not an image")
    r = client.post(
        f"/products/{product['id']}/image",
        files={"file": ("notes.txt", fake_file, "text/plain")},
        headers=auth_headers,
    )
    assert r.status_code == 400


def test_image_upload_on_missing_product_returns_404(client, auth_headers):
    fake_image = io.BytesIO(b"fake-jpeg-bytes")
    r = client.post(
        "/products/9999/image",
        files={"file": ("photo.jpg", fake_image, "image/jpeg")},
        headers=auth_headers,
    )
    assert r.status_code == 404


def test_image_upload_failure_returns_502(client, auth_headers):
    product = make_product(client, auth_headers)
    fake_image = io.BytesIO(b"fake-jpeg-bytes")
    with patch("app.routers.products.upload_product_image") as mock_upload:
        mock_upload.side_effect = Exception("network error")
        r = client.post(
            f"/products/{product['id']}/image",
            files={"file": ("photo.jpg", fake_image, "image/jpeg")},
            headers=auth_headers,
        )
    assert r.status_code == 502
