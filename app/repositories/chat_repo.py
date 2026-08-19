# app/repositories/chat_repo.py
from uuid import UUID


def _row_to_message_dict(row) -> dict:
    d = dict(row)
    d["guest_id"] = str(d["guest_id"])
    return d

def _uuid_to_str(row_dict: dict, field: str = "guest_id") -> dict:
    row_dict[field] = str(row_dict[field])
    return row_dict

async def create_guest(conn) -> str:
    row = await conn.fetchrow(
        "INSERT INTO guests DEFAULT VALUES RETURNING id"
    )
    return str(row["id"])


async def touch_guest(conn, guest_id: str) -> bool:
    """Обновляет last_seen_at. Возвращает False, если такого гостя нет."""
    row = await conn.fetchrow(
        "UPDATE guests SET last_seen_at = now() WHERE id = $1 RETURNING id",
        UUID(guest_id),
    )
    return row is not None


async def save_message(conn, guest_id: str, sender: str, body: str) -> dict:
    row = await conn.fetchrow(
        """
        INSERT INTO chat_messages (guest_id, sender, body)
        VALUES ($1, $2, $3)
        RETURNING id, guest_id, sender, body, read_at, created_at
        """,
        UUID(guest_id), sender, body,
    )
    return _row_to_message_dict(row)


async def get_history(conn, guest_id: str, limit: int = 100) -> list[dict]:
    rows = await conn.fetch(
        """
        SELECT id, guest_id, sender, body, read_at, created_at
        FROM chat_messages
        WHERE guest_id = $1
        ORDER BY created_at ASC
        LIMIT $2
        """,
        UUID(guest_id), limit,
    )
    return [_uuid_to_str(dict(r)) for r in rows]


async def mark_read(conn, guest_id: str, sender_to_mark: str) -> None:
    """Например, при открытии чата админом помечаем прочитанными сообщения гостя."""
    await conn.execute(
        """
        UPDATE chat_messages SET read_at = now()
        WHERE guest_id = $1 AND sender = $2 AND read_at IS NULL
        """,
        UUID(guest_id), sender_to_mark,
    )


async def list_conversations(conn) -> list[dict]:
    """Для админского инбокса: гости + последнее сообщение + счётчик непрочитанных."""
    rows = await conn.fetch(
        """
        SELECT
            g.id AS guest_id,
            g.last_seen_at,
            lm.body AS last_message,
            lm.sender AS last_sender,
            lm.created_at AS last_message_at,
            COALESCE(unread.count, 0) AS unread_count
        FROM guests g
        LEFT JOIN LATERAL (
            SELECT body, sender, created_at
            FROM chat_messages
            WHERE guest_id = g.id
            ORDER BY created_at DESC
            LIMIT 1
        ) lm ON true
        LEFT JOIN (
            SELECT guest_id, COUNT(*) AS count
            FROM chat_messages
            WHERE sender = 'guest' AND read_at IS NULL
            GROUP BY guest_id
        ) unread ON unread.guest_id = g.id
        WHERE lm.body IS NOT NULL
        ORDER BY lm.created_at DESC
        """
    )
    return [_uuid_to_str(dict(r)) for r in rows]