import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _


class NotificationTemplate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(_('title'), max_length=255)
    template = models.TextField(_('template'))
    created_at = models.DateTimeField(_('created_at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated_at'), auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'notification_template'
        verbose_name = _('Notification template')
        verbose_name_plural = _('Notification template')
        ordering = ['-title']
