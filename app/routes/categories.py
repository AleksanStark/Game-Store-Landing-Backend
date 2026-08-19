from fastapi import APIRouter, Depends, HTTPException
from app.core.database import get_connection
from app.schemas.category import CategoryCreate
from app.api.deps import get_current_admin_id
import asyncpg

router = APIRouter(prefix="/categories")


@router.get("")
async def list_categories(conn: asyncpg.Connection=Depends(get_connection)):
    rows = await conn.fetch("SELECT * FROM categories")

    return [dict(row) for row in rows]



@router.post("")
async def create_category(payload: CategoryCreate, admin_id: int = Depends(get_current_admin_id),conn: asyncpg.Connection=Depends(get_connection)):

    if admin_id:
        category = await conn.fetchrow("INSERT INTO categories (name) VALUES ($1) RETURNING *", payload.name)

        return dict(category)



@router.delete("/{category_id}")
async def delete_category(category_id: int, admin_id: int = Depends(get_current_admin_id), conn: asyncpg.Connection=Depends(get_connection)):
    if admin_id:
        existing = await conn.fetchrow("SELECT id FROM categories WHERE id = $1", category_id)

        if not existing:
            raise  HTTPException(status_code=404, detail="Категория не найдена")

        await conn.execute("DELETE FROM categories WHERE id = $1", category_id)

    return {"message", "Категория удалена"}