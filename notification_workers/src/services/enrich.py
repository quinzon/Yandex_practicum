import logging
from typing import List

import httpx

from notification_workers.src.models.notification import (
    NotificationMessage,
    EnrichedNotification,
    RecipientData
)

logger = logging.getLogger(__name__)


class EnrichService:
    def __init__(self, admin_service_url: str):
        self.admin_service_url = admin_service_url

    async def get_enriched_notification(self, msg: NotificationMessage) -> EnrichedNotification:
        if msg.recipient_group:
            recipients = await self._fetch_recipients_by_group(msg.recipient_group)
        else:
            if not msg.user_id:
                raise ValueError('user_id is missing for an individual notification')
            single = await self._fetch_recipient_by_user_id(msg.user_id)
            recipients = [single]

        tmpl_subject, tmpl_text = await self._fetch_template_data(msg.template_id)

        final_subject = msg.subject or tmpl_subject or 'No Subject'
        final_text = msg.text or tmpl_text or 'No Text'

        return EnrichedNotification(
            type=msg.type,
            subject=final_subject,
            text=final_text,
            recipients=recipients
        )

    async def _fetch_recipient_by_user_id(self, user_id: str) -> RecipientData:
        url = f'{self.admin_service_url}/users/{user_id}'
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                return RecipientData(
                    user_id=data['id'],
                    email=data.get('email'),
                    phone=data.get('phone'),
                    push_token=data.get('push_token'),
                    name=data.get('name')
                )
            except httpx.HTTPError as exc:
                logger.exception('Failed to fetch user_id=%s', user_id)
                raise RuntimeError(f'Error fetching user {user_id}: {exc}') from exc

    async def _fetch_recipients_by_group(self, group_id: str) -> List[RecipientData]:
        url = f'{self.admin_service_url}/groups/{group_id}/users'
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                recipients = []
                for item in data:
                    recipients.append(RecipientData(
                        user_id=item['id'],
                        email=item.get('email'),
                        phone=item.get('phone'),
                        push_token=item.get('push_token'),
                        name=item.get('name')
                    ))
                return recipients
            except httpx.HTTPError as exc:
                logger.exception('Failed to fetch group=%s users', group_id)
                raise RuntimeError(f'Error fetching group {group_id} users: {exc}') from exc

    async def _fetch_template_data(self, template_id: str) -> (str | None, str | None):
        url = f'{self.admin_service_url}/templates/{template_id}'
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                return data.get('subject'), data.get('text')
            except httpx.HTTPError as exc:
                logger.exception('Failed to fetch template_id=%s', template_id)
                return None, None
