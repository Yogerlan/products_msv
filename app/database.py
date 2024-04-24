from sqlalchemy import select
from sqlalchemy.ext.asyncio import (AsyncAttrs, async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from .schemas import Product

PROD_DB_URL = "sqlite+aiosqlite:///./products.db"
TEST_DB_URL = "sqlite+aiosqlite://"


class BaseModel(AsyncAttrs, DeclarativeBase):
    pass


class ProductModel(BaseModel):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    sku: Mapped[str] = mapped_column(unique=True, index=True)
    stock: Mapped[int]


class DatabaseHandler:
    def __init__(self, testing=False):
        self.__testing = testing
        url = TEST_DB_URL if self.__testing else PROD_DB_URL
        self.__engine = create_async_engine(url, echo=testing)

    async def __create_all(self):
        async with self.__engine.begin() as conn:
            await conn.run_sync(BaseModel.metadata.create_all)

    async def __drop_all(self):
        async with self.__engine.begin() as conn:
            await conn.run_sync(BaseModel.metadata.drop_all)

    async def connect(self):
        await self.__create_all()
        self.__async_session = async_sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.__engine
        )

    async def disconnect(self):
        if self.__testing:
            await self.__drop_all()

        await self.__engine.dispose()

    async def create_product(self, product: Product):
        async with self.__async_session() as session:
            db_product = ProductModel(
                name=product.name,
                sku=product.sku,
                stock=product.stock)
            session.add(db_product)
            await session.commit()
            await session.refresh(db_product)

            return db_product

    async def get_product_by_sku(self, sku: str):
        async with self.__async_session() as session:
            result = await session.execute(select(ProductModel).filter(ProductModel.sku == sku).limit(1))

            return result.scalar_one_or_none()

    async def update_product_by_sku(self, sku: str, stock: int):
        async with self.__async_session() as session:
            result = await session.execute(select(ProductModel).filter(ProductModel.sku == sku).limit(1))
            db_product = result.scalar_one()
            db_product.stock += stock
            await session.commit()
            await session.refresh(db_product)

            return db_product

    async def get_low_stock_products(self):
        async with self.__async_session() as session:
            result = await session.execute(select(ProductModel).filter(ProductModel.stock < 10))

            return result.scalars().all()
