from pathlib import Path
import asyncpg

MIGRATIONS_DIR = Path(__file__).parent.parent.parent / "migrations"

async def run_migrations(pool: asyncpg.Pool):
    print("Migrations directory:", MIGRATIONS_DIR)
    print("Migration files:", list(MIGRATIONS_DIR.glob("*.sql")))
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                filename TEXT PRIMARY KEY,
                applied_at TIMESTAMPTZ NOT NULL DEFAULT now()
            )
        """)

        applied = {
                   r["filename"] 
                   for r in await conn.fetch("SELECT filename FROM schema_migrations")
                }
        migration_files = sorted(MIGRATIONS_DIR.glob("*.sql"))

        for path in  migration_files:
            if path.name in applied:
                continue

            sql = path.read_text()
            async with conn.transaction():
                await conn.execute(sql)
                await conn.execute("INSERT INTO schema_migrations (filename) VALUES ($1)", path.name)
            print(f"Применена миграция: {path.name}")