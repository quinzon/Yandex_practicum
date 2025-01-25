from functools import lru_cache

from fastapi import Depends

from push_service.src.services.websocket import WebsocketService, get_websocket_service


class MessageService:
    def __init__(self, websocket_service: WebsocketService):
        self.websocket = websocket_service

    async def send(self, user_id: str, message: str) -> None:
        connections = await self.websocket.get_connections(user_id)
        await self.websocket.send_message(connections, message)


@lru_cache()
def get_message_service(
        websocket_service: WebsocketService = Depends(get_websocket_service)
) -> MessageService:
    return MessageService(websocket_service)
