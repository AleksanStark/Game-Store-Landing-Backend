import asyncpg



async def add_image(conn: asyncpg.Connection, product_id: int, path: str, position: int = 0) -> dict:
    row = await conn.fetchrow(
        """
        INSERT INTO product_images (product_id, path, position)
        VALUES ($1, $2, $3)
        RETURNING id, product_id, path, position, created_at
        """, product_id, path, position,
    )
    return dict(row)



async def list_images(conn: asyncpg.Connection, product_id: int) -> list[dict]:
    rows = await conn.fetch(
        "SELECT id, product_id, path, position, created_at FROM product_images WHERE product_id = $1 ORDER BY position ASC, id ASC",
          product_id,

    )
    return [dict(row) for row in rows]


async def get_image(conn: asyncpg.Connection, image_id: int) -> dict | None:
    print("ID OF IMAGE", image_id)
    row = await conn.fetchrow(
        "SELECT id, product_id, path FROM product_images WHERE id = $1", image_id
    )
    print("ROW",row)
    return dict(row) if row else None


async def delete_image(conn: asyncpg.Connection, image_id: int) -> None:
    await conn.execute("DELETE FROM product_images WHERE id = $1", image_id)


async def reorder_images(conn, product_id: int, ordered_ids: list[int]) -> list[dict]:
    """
    Индекс в списке = позиция сверху вниз.
    Нижний элемент (последний индекс) получает наибольшее числовое position —
    именно он трактуется как обложка везде, где выбирается "последнее" фото.
    """
    async with conn.transaction():
        for index, image_id in enumerate(ordered_ids):
            await conn.execute(
                "UPDATE product_images SET position = $1 WHERE id = $2 AND product_id = $3",
                index, image_id, product_id,
            )
 
    rows = await conn.fetch(
        "SELECT id, path, position FROM product_images WHERE product_id = $1 ORDER BY position ASC",
        product_id,
    )
    return [dict(r) for r in rows]




async def replace_image_file_path(conn, image_id: int, new_path: str) -> dict | None:
    """Меняет только path у существующей записи — id и position остаются прежними."""
    row = await conn.fetchrow(
        """
        UPDATE product_images
        SET path = $1
        WHERE id = $2
        RETURNING id, product_id, path, position, created_at
        """,
        new_path, image_id,
    )
    return dict(row) if row else None
 
 
async def get_image_by_id(conn, image_id: int) -> dict | None:
    row = await conn.fetchrow(
        "SELECT id, product_id, path FROM product_images WHERE id = $1", image_id
    )
    return dict(row) if row else None