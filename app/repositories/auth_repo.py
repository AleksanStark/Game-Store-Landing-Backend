import hashlib
import asyncpg
from datetime import datetime

def hash_token(token:str):
    return hashlib.sha256(token.encode()).hexdigest()


async def get_admin_by_email(conn: asyncpg.Connection, email: str):
    return await conn.fetchrow("SELECT id, email, password_hash FROM admins WHERE email = $1", email)


async def create_admin(conn: asyncpg.Connection, email: str, hashed_password: str):
    admin_email = await conn.fetchrow("INSERT INTO admins (email, password_hash) VALUES ($1, $2) RETURNING email", email, hashed_password)
    return dict(admin_email)



async def save_refresh_token(conn: asyncpg.Connection, admin_id: int, token: str, expires_at: datetime):
    await conn.execute(
        "INSERT INTO refresh_tokens (admin_id, token_hash, expires_at) VALUES ($1, $2, $3)",
        admin_id, hash_token(token), expires_at
    )



async def is_refresh_token_valid(conn: asyncpg.Connection, admin_id: int, token:str) -> bool:

    row = await conn.fetchrow(
        """
        SELECT id FROM refresh_tokens
        WHERE admin_id = $1 AND token_hash = $2
        AND revoked = false AND expires_at > now()
        """,
        admin_id, hash_token(token)
    )
   
    return row is not None


async def revoke_refresh_token(conn: asyncpg.Connection, token:str):
    await conn.execute(
        "UPDATE refresh_tokens SET revoked = true WHERE token_hash = $1", hash_token(token)
    )


async def revoke_all_admin_tokens(conn: asyncpg.Connection, admin_id: int):
    await conn.execute(
        "UPDATE refresh_tokens SET revoked = true WHERE admin_id = $1", admin_id
    )