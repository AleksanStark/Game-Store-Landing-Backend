from fastapi import APIRouter, Depends
from app.core.database import get_connection
from app.api.deps import get_current_admin_id
from app.schemas.product import ProductCreate, ProductUpdate
import asyncpg

router = APIRouter(prefix="/products")

@router.get("")
async def list_products(conn: asyncpg.Connection=Depends(get_connection)):
    rows = await conn.fetch(
        """
      SELECT
            p.id, p.name, p.price, p.condition,
            p.category_id, c.name AS category_name,
            img.path AS img,
            img.id AS img_id
        FROM products p
        LEFT JOIN categories c ON c.id = p.category_id
        LEFT JOIN LATERAL (
            SELECT path, id
            FROM product_images
            WHERE product_id = p.id
            ORDER BY position DESC, id DESC   -- DESC, не ASC — обложка это НИЗ списка
            LIMIT 1
        ) img ON true
        """
        )
    return [dict(row) for row in rows]

@router.patch("/{product_id}")
async def update_product(product_id: int, payload: ProductUpdate, admin_id: int = Depends(get_current_admin_id),conn: asyncpg.Connection = Depends(get_connection), ):
    if admin_id:
        row = await conn.fetchrow(
            """
            UPDATE products 
            SET 
                name = COALESCE($2, name),
                category_id = COALESCE($3, category_id),
                condition = COALESCE($4, condition),
                price = COALESCE($5, price)
            WHERE id = $1
            RETURNING id, name, category_id, condition, price
            """,
            product_id, payload.name, payload.category_id, payload.condition, payload.price
        )
        return dict(row) if row else None


@router.delete("/{product_id}")
async def delete_product(product_id: int, admin_id: int =  Depends(get_current_admin_id), conn: asyncpg.Connection = Depends(get_connection)):
    if admin_id:
        await conn.execute("DELETE FROM products WHERE id = $1", product_id)    

@router.post("")
async def create_product(payload: ProductCreate,admin_id: int = Depends(get_current_admin_id),conn: asyncpg.Connection=Depends(get_connection)):
    if admin_id:
        product = await conn.fetchrow("INSERT INTO products (category_id, name, price, condition) VALUES ($1, $2, $3, $4) RETURNING *", payload.category_id ,payload.name, str(payload.price), payload.condition)

        return dict(product)