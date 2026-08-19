
from collections.abc import AsyncGenerator
from app.core.config import settings
import asyncpg

class Database:
    pool: asyncpg.Pool | None = None


    async def connect(self):
        self.pool = await asyncpg.create_pool(
            dsn=settings.database_url,
            min_size=5,
            max_size=20
        )

    async def disconnect(self):
        if self.pool is not None:
            await self.pool.close()

db = Database()


async def get_connection() -> AsyncGenerator[asyncpg.Connection, None]:
    if db.pool is None:
        raise RuntimeError("Database pool is not initialized")
    async with db.pool.acquire() as conn:
        yield conn