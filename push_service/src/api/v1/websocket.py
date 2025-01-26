import logging

from fastapi import APIRouter, WebSocket, Depends

from push_service.src.services.websocket import WebsocketService, get_websocket_service
from push_service.src.services.auth import AuthService, get_auth_service


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket('/push/')
async def websocket_endpoint(
        websocket: WebSocket,
        websocket_service: WebsocketService = Depends(get_websocket_service),
        auth_service: AuthService = Depends(get_auth_service),
):
    query_params = websocket.query_params
    auth_token = query_params.get('token')

    if auth_token is None:
        await websocket.close(code=1008)
        return

    try:
        user_id = await auth_service.get_user_id(auth_token)
    except Exception as e:
        logger.error(f'Connection closed: {websocket}. Error: {e}')
        await websocket.close(code=1008)
        return

    ws_token = await websocket_service.create_connection(user_id, websocket)
    logger.info(f'Connection opened: {ws_token} for user: {user_id}')

    try:
        while True:
            await websocket.receive_text()
    except Exception as e:
        logger.error(f'Connection closed: {ws_token}. Error: {e}')
    finally:
        await websocket_service.remove_connection(user_id, ws_token)
        logger.info(f'Connection closed: {ws_token} for user: {user_id}')
