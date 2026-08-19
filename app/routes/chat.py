# app/api/routes/chat.py
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, HTTPException
from app.core.database import get_connection, db
from app.api.deps import get_current_admin_id
from app.repositories import chat_repo
from app.services.chat_manager import manager
from app.schemas.chat import GuestOut, MessageOut, ConversationOut

router = APIRouter()


# ---------- REST ----------

@router.post("/chat/guest", response_model=GuestOut)
async def create_guest(conn=Depends(get_connection)):
    """
    Вызывается один раз с фронта, если в localStorage ещё нет guest_id.
    Возвращённый id фронт сохраняет и переиспользует при каждом визите.
    """
    guest_id = await chat_repo.create_guest(conn)
    return GuestOut(guest_id=guest_id)


@router.get("/chat/history/{guest_id}", response_model=list[MessageOut])
async def get_history(guest_id: str, conn=Depends(get_connection)):
    ok = await chat_repo.touch_guest(conn, guest_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Гость не найден")
    messages = await chat_repo.get_history(conn, guest_id)
    return [MessageOut(**m) for m in messages]


@router.get("/chat/conversations", response_model=list[ConversationOut])
async def list_conversations(
    admin_id: int = Depends(get_current_admin_id),
    conn=Depends(get_connection),
):
    """Инбокс для админки — список всех диалогов с последним сообщением и unread-счётчиком."""
    convos = await chat_repo.list_conversations(conn)
    return  [ConversationOut(**c) for c in convos] 


@router.post("/chat/mark-read/{guest_id}")
async def mark_conversation_read(
    guest_id: str,
    admin_id: int = Depends(get_current_admin_id),
    conn=Depends(get_connection),
):
    await chat_repo.mark_read(conn, guest_id, sender_to_mark="guest")
    return {"message": "ok"}


# ---------- WEBSOCKET: ГОСТЬ ----------

@router.websocket("/chat/ws/guest/{guest_id}")
async def guest_ws(websocket: WebSocket, guest_id: str):
    await manager.connect_guest(guest_id, websocket)
    async with db.pool.acquire() as conn:
        exists = await chat_repo.touch_guest(conn, guest_id)
    if not exists:
        await websocket.close(code=4404)
        return

    try:
        while True:
            data = await websocket.receive_json()
            body = data.get("body", "").strip()
            if not body:
                continue

            async with db.pool.acquire() as conn:
                message = await chat_repo.save_message(conn, guest_id, "guest", body)

            payload = {
                "id": message["id"],
                "guest_id": guest_id,
                "sender": "guest",
                "body": message["body"],
                "created_at": message["created_at"].isoformat(),
            }
            # эхо гостю (подтверждение доставки) + всем подключённым админам
            await websocket.send_json(payload)
            await manager.broadcast_to_admins(payload)

    except WebSocketDisconnect:
        manager.disconnect_guest(guest_id)


# ---------- WEBSOCKET: АДМИН ----------

@router.websocket("/chat/ws/admin")
async def admin_ws(websocket: WebSocket, token: str):
    """
    Токен передаётся как query-параметр (?token=...), потому что браузерный
    WebSocket API не поддерживает произвольные заголовки при подключении.
    """
    from jose import jwt, JWTError
    from app.core.config import settings

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        if payload.get("type") != "access":
            raise ValueError
    except (JWTError, ValueError):
        await websocket.close(code=4401)
        return

    await manager.connect_admin(websocket)

    try:
        while True:
            data = await websocket.receive_json()
            guest_id = data.get("guest_id")
            body = data.get("body", "").strip()
            if not guest_id or not body:
                continue

            async with db.pool.acquire() as conn:
                message = await chat_repo.save_message(conn, guest_id, "admin", body)

            payload = {
                "id": message["id"],
                "guest_id": guest_id,
                "sender": "admin",
                "body": message["body"],
                "created_at": message["created_at"].isoformat(),
            }
            # доставляем гостю, если он сейчас онлайн; эхо остальным админам (мультитаб)
            await manager.send_to_guest(guest_id, payload)
            await manager.broadcast_to_admins(payload)

    except WebSocketDisconnect:
        manager.disconnect_admin(websocket)