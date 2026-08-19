# app/services/chat_manager.py
from fastapi import WebSocket


class ChatConnectionManager:
    """
    Держит активные соединения:
    - guest_connections: guest_id -> WebSocket (один гость = одно активное окно чата)
    - admin_connections: множество WebSocket всех подключённых сейчас админов
      (админ видит входящие сообщения от ЛЮБОГО гостя, роутинг по guest_id внутри payload)
    """

    def __init__(self) -> None:
        self.guest_connections: dict[str, WebSocket] = {}
        self.admin_connections: set[WebSocket] = set()

    async def connect_guest(self, guest_id: str, ws: WebSocket) -> None:
        await ws.accept()
        self.guest_connections[guest_id] = ws

    async def connect_admin(self, ws: WebSocket) -> None:
        await ws.accept()
        self.admin_connections.add(ws)

    def disconnect_guest(self, guest_id: str) -> None:
        self.guest_connections.pop(guest_id, None)

    def disconnect_admin(self, ws: WebSocket) -> None:
        self.admin_connections.discard(ws)

    async def send_to_guest(self, guest_id: str, payload: dict) -> bool:
        ws = self.guest_connections.get(guest_id)
        if ws is None:
            return False
        await ws.send_json(payload)
        return True

    async def broadcast_to_admins(self, payload: dict) -> None:
        dead = []
        for ws in self.admin_connections:
            try:
                await ws.send_json(payload)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.admin_connections.discard(ws)

    def is_guest_online(self, guest_id: str) -> bool:
        return guest_id in self.guest_connections


manager = ChatConnectionManager()