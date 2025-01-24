import asyncio
import logging

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, Personalization

from notification_workers.src.models.notification import EnrichedNotification
from notification_workers.src.services.senders.base import BaseSender

logger = logging.getLogger(__name__)


class EmailSender(BaseSender):
    def __init__(self, sendgrid_email_key: str, default_from_email: str):
        self.sendgrid_api_key = sendgrid_email_key
        self.default_from_email = default_from_email

    async def send(self, notification: EnrichedNotification) -> None:
        recipients = [r for r in notification.recipients if r.email]
        if not recipients:
            logger.warning('No valid email addresses found for notification: skip sending.')
            return

        mail = Mail()
        mail.from_email = Email(self.default_from_email)
        mail.template_id = notification.template_id
        for r in recipients:
            personalization = Personalization()
            personalization.add_to(Email(r.email, r.name))
            personalization.dynamic_template_data = {
                'name': r.name,
                'user_id': r.user_id,
                'email': r.email,
                'global_subject': notification.subject,
                'global_text': notification.text
            }

            mail.add_personalization(personalization)
        sg_client = SendGridAPIClient(self.sendgrid_api_key)

        try:
            response = await asyncio.to_thread(sg_client.send, mail)
            logger.info('SendGrid response status: %s', response.status_code)
        except Exception as exc:
            logger.exception('Failed to send email via SendGrid')
            raise
