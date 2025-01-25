from fastapi import APIRouter, Depends
from push_service.src.models.dto.message import SendMessageRequest
from push_service.src.services.message import MessageService, get_message_service

router = APIRouter()


@router.post('/send')
async def send_message(
        message_data: SendMessageRequest,
        message_service: MessageService = Depends(get_message_service),
):
    await message_service.send(message_data.user_id, message_data.message)

    return {'message': message_data.message}
