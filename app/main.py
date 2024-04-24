import asyncio
import logging
import os
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Body, FastAPI, HTTPException, Path

from .database import DatabaseHandler
from .schemas import Product, ProductAdd, ProductOrder, ProductResponse

context = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    testing = os.getenv("TESTING") is not None
    context["db"] = DatabaseHandler(testing)
    await context["db"].connect()
    loop = asyncio.get_running_loop()
    loop.create_task(watchdog())
    yield
    await context["db"].disconnect()
    context.clear()


async def watchdog():
    while True:
        products = await context["db"].get_low_stock_products()

        if len(products):
            logging.warning(f"{len(products)} product stocks are depleting:")

            for product in products:
                logging.warning(f"\t{product.sku}: {product.stock}")

        await asyncio.sleep(5)

app = FastAPI(
    lifespan=lifespan,
    title="Products MSV",
    summary="Product management API REST Microservice",
    description="""
Take your inventory management experience to the next level by integrating
our API into your business services. You can add your products, update stocks,
and place orders with our endpoints. We offer stability, security, and clear
and detailed documentation.
""",
    license_info={
        "name": "MIT License",
        "identifier": "MIT"
    }
)


@app.get(
    "/ping",
    summary="An ancient game",
    description="Challenge the server for a match"
)
async def ping():
    return {"msg": "pong"}


@app.post(
    "/api/products",
    response_model=ProductResponse,
    response_description="The created product database record",
    summary="Creates a product",
    description="A new product record is created with the name, SKU, and initial stock"
)
async def create_product(
    product: Annotated[Product, Body(description="The new product data")]
):
    if await context["db"].get_product_by_sku(product.sku) is not None:
        raise HTTPException(
            status_code=400,
            detail=f"SKU {product.sku} already registered."
        )

    return await context["db"].create_product(product)


@app.patch(
    "/api/inventories/product/{product_id}",
    response_model=ProductResponse,
    response_description="The updated product database record",
    summary="Adds stock to a product",
    description="The requested product stock gets increased by a specified quantity"
)
async def add_product_stock(
    product_id: Annotated[str, Path(description="The product SKU identifier")],
    product: Annotated[ProductAdd, Body(
        description="The product data to update")]
):
    if await context["db"].get_product_by_sku(product_id) is None:
        raise HTTPException(
            status_code=404,
            detail=f"SKU {product_id} not found."
        )

    return await context["db"].update_product_by_sku(product_id, product.quantity)


@app.post(
    "/api/orders",
    response_model=list[ProductResponse],
    response_description="The updated database records of the ordered products",
    summary="Orders a list of products",
    description="For each product requested, the SKU and quantity to remove from stock are specified"
)
async def order_products(
    products: Annotated[list[ProductOrder], Body(
        description="The products' order data")]
):
    for product in products:
        db_product = await context["db"].get_product_by_sku(product.sku)

        if db_product is None:
            raise HTTPException(
                status_code=404,
                detail=f"SKU {product.sku} not found."
            )

        if db_product.stock < product.quantity:
            raise HTTPException(
                status_code=422,
                detail=f"Product {product.sku} with insufficient stock: {
                    db_product.stock}/{product.quantity}"
            )

    db_products = []

    for product in products:
        db_product = await context["db"].update_product_by_sku(product.sku, -product.quantity)
        db_products.append(db_product)

    return db_products
