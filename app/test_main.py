import os

from fastapi.testclient import TestClient

from .main import app

os.environ["TESTING"] = ""


def test_ping():
    with TestClient(app) as client:
        response = client.get("/ping")
        assert response.status_code == 200
        assert response.json() == {"msg": "pong"}


def test_create_product():
    with TestClient(app) as client:
        # Test non-valid SKUs.
        response = client.post("/api/products", json={
            "name": "milk",
            "sku": "0123456"
        })
        assert response.status_code == 422

        response = client.post("/api/products", json={
            "name": "milk",
            "sku": "0123456789ABC"
        })
        assert response.status_code == 422

        # Test non-valid stock.
        response = client.post("/api/products", json={
            "name": "milk",
            "sku": "0123456789AB",
            "stock": 90
        })
        assert response.status_code == 422

        # Test valid data.
        response = client.post("/api/products", json={
            "name": "milk",
            "sku": "0123456789AB",
        })
        assert response.status_code == 200
        assert response.json().get("stock") == 100


def test_add_product_stock():
    with TestClient(app) as client:
        client.post("/api/products", json={
            "name": "milk",
            "sku": "0123456789AB",
        })

        # Test non-valid SKU.
        response = client.patch("/api/inventories/product/0123456789", json={
            "quantity": 50
        })
        assert response.status_code == 404

        # Test non-valid quantity.
        response = client.patch("/api/inventories/product/0123456789AB", json={
            "quantity": 0
        })
        assert response.status_code == 422

        # Test valid data.
        response = client.patch("/api/inventories/product/0123456789AB", json={
            "quantity": 50
        })
        assert response.status_code == 200
        assert response.json().get("stock") == 150


def test_order_products():
    with TestClient(app) as client:
        client.post("/api/products", json={
            "name": "milk",
            "sku": "A8F96DB0",
        })
        client.post("/api/products", json={
            "name": "coffee",
            "sku": "A8F96DB1",
        })
        client.post("/api/products", json={
            "name": "tea",
            "sku": "A8F96DB2",
        })

        # Test non-valid SKUs.
        response = client.post("/api/orders", json=[
            {
                "sku": "A8F96DB3",
                "quantity": 15
            }
        ])
        assert response.status_code == 404

        # Test non-valid quantities.
        response = client.post("/api/orders", json=[
            {
                "sku": "A8F96DB0",
                "quantity": 15,
            }, {
                "sku": "A8F96DB1",
                "quantity": 0
            }
        ])
        assert response.status_code == 422
        response = client.post("/api/orders", json=[
            {
                "sku": "A8F96DB0",
                "quantity": 15
            }, {
                "sku": "A8F96DB1",
                "quantity": 150
            }
        ])
        assert response.status_code == 422

        # Test valid data
        response = client.post("/api/orders", json=[
            {
                "sku": "A8F96DB0",
                "quantity": 15
            }, {
                "sku": "A8F96DB1",
                "quantity": 100
            }, {
                "sku": "A8F96DB2",
                "quantity": 10
            }
        ])
        assert response.status_code == 200
