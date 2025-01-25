import uuid
from functools import lru_cache
from typing import Dict

from fastapi import Depends, WebSocket

from push_service.src.services.connection_repository import ConnectionRepositoryService, get_connection_repository


active_connections: Dict[str, WebSocket] = {}


class WebsocketService:
    def __init__(self, connection_repository: ConnectionRepositoryService):
        self.repository = connection_repository

    async def create_connection(self, user_id: str, websocket: WebSocket) -> str:
        await websocket.accept()

        ws_token = str(uuid.uuid4())
        active_connections[ws_token] = websocket

        await self.put_connection(user_id, str(ws_token))

        return ws_token

    async def put_connection(self, user_id: str, ws_token: str) -> None:
        await self.repository.put_by_id(user_id, ws_token)

    async def get_connections(self, user_id: str) -> list[WebSocket] | None:
        ws_tokens = await self.repository.get_list_by_id(user_id)
        if not ws_tokens:
            return None

        connections = []
        for token in ws_tokens:
            websocket = active_connections.get(token)
            if websocket:
                connections.append(websocket)
        return connections

    async def remove_connection(self, user_id: str, ws_token: str) -> None:
        active_connections.pop(ws_token, None)
        await self.repository.remove_value_by_id(user_id, ws_token)

    @staticmethod
    async def send_message(connections: list, message: str) -> None:
        for connection in connections:
            await connection.send_text(message)


@lru_cache()
def get_websocket_service(
        connection_repository: ConnectionRepositoryService = Depends(get_connection_repository)
) -> WebsocketService:
    return WebsocketService(connection_repository)
