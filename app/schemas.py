from pydantic import BaseModel, Field


class Product(BaseModel):
    name: str = Field(
        description="The product generic name")
    sku: str = Field(
        min_length=8,
        max_length=12,
        description="The product SKU identifier")
    stock: int = Field(
        default=100,
        ge=100,
        description="The product availability")


class ProductAdd(BaseModel):
    quantity: int = Field(
        ge=1,
        description="Quantity to add to product stock")


class ProductOrder(BaseModel):
    sku: str = Field(
        min_length=8,
        max_length=12,
        description="The product SKU identifier")
    quantity: int = Field(
        ge=1,
        description="The quantity of product requested")


class ProductResponse(Product):
    id: int = Field(
        description="The product database identifier")
    stock: int = Field(
        description="The product availability")
