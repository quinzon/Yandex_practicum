import logging
import httpx
from typing import List

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
            recipients = await self._fetch_recipients_by_role(msg.recipient_group)
        else:
            if not msg.user_id:
                raise ValueError('user_id is missing for an individual notification')
            single_user = await self._fetch_user_by_id(msg.user_id)
            recipients = [single_user]

        tmpl_subject, tmpl_text = await self._fetch_template_data(msg.template_id)

        final_subject = msg.subject or tmpl_subject or 'No Subject'
        final_text = msg.text or tmpl_text or 'No Text'

        return EnrichedNotification(
            type=msg.type,
            subject=final_subject,
            text=final_text,
            recipients=recipients
        )

    async def _fetch_user_by_id(self, user_id: str) -> RecipientData:
        url = f'{self.admin_service_url}/users/?id={user_id}'
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                if not data:
                    raise ValueError(f'No user found with id={user_id}')
                user_obj = data[0]
                full_name = self._build_name(user_obj.get('first_name'), user_obj.get('last_name'))
                return RecipientData(
                    user_id=user_obj['id'],
                    email=user_obj.get('email'),
                    name=full_name
                )
            except httpx.HTTPError as exc:
                logger.exception('Failed to fetch user_id=%s', user_id)
                raise RuntimeError(f'Error fetching user {user_id}: {exc}') from exc

    async def _fetch_recipients_by_role(self, role: str) -> List[RecipientData]:
        url = f'{self.admin_service_url}/users/?role={role}'
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                recipients = []
                for user_obj in data:
                    full_name = self._build_name(user_obj.get('first_name'), user_obj.get('last_name'))
                    recipients.append(RecipientData(
                        user_id=user_obj['id'],
                        email=user_obj.get('email'),
                        name=full_name
                    ))
                return recipients
            except httpx.HTTPError as exc:
                logger.exception('Failed to fetch users for role=%s', role)
                raise RuntimeError(f'Error fetching users for role {role}: {exc}') from exc

    async def _fetch_template_data(self, template_id: str) -> tuple[str | None, str | None]:
        url = f'{self.admin_service_url}/template/{template_id}/'
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                return data.get('title'), data.get('template')
            except httpx.HTTPError:
                logger.exception('Failed to fetch template_id=%s', template_id)
                return None, None

    def _build_name(self, first_name: str | None, last_name: str | None) -> str:
        if not first_name and not last_name:
            return ''
        if first_name and last_name:
            return f'{first_name} {last_name}'
        return first_name or last_name or ''
