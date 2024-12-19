import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from persistent.db.base import Base
from settings.settings import settings

async def main():
    engine = create_async_engine(
        f"postgresql+asyncpg://{settings.pg.username}:{settings.pg.password}@"
        f"{settings.pg.host}:{settings.pg.port}/{settings.pg.database}",
        echo=False,
        future=True
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("Tables created successfully.")

if __name__ == "__main__":
    asyncio.run(main())
