from http import HTTPStatus

from fastapi import APIRouter, HTTPException, Depends, Request

from notification_service.src.model.notification import Notification, NotificationResponse
from notification_service.src.service.notification import NotificationService, \
    get_notification_service

router = APIRouter()


@router.post('/notifications/', response_model=NotificationResponse)
async def send_notification(notification: Notification, request: Request,
                            notification_service: NotificationService = Depends(
                                get_notification_service)):
    try:
        request_id = request.headers.get('X-Request-Id')
        return await notification_service.send_notification(notification, request_id)
    except ValueError as e:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                            detail=f'Sending message error: {str(e)}')
