from http import HTTPStatus
import requests

from django.contrib import admin
from django.urls import path, reverse
from django.utils.html import format_html
from django.shortcuts import render, redirect
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import PermissionDenied

from notification.models import NotificationTemplate
from notification.forms import NotificationRecipientForm
from config.authentication.admin import PermissionAdmin
from django.conf import settings
from config.utils import prepare_headers

NOTIFICATION_SERVICE_URL = settings.NOTIFICATION_SERVICE_URL


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(PermissionAdmin):
    resource_name = 'admin:notification_template'
    list_display = ('title', 'template', 'created_at', 'updated_at', 'send_button')
    search_fields = ('title', 'id')

    def has_send_permission(self, request):
        return self._check_permission(request, 'send')

    def send_button(self, obj):
        return format_html(
            f'<a class="button" href="{{}}">{_("Send it out")}</a>',
            reverse('admin:send_notification_template', args=[obj.id])
        )

    send_button.short_description = _('Sending message')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('send/<uuid:notification_template_id>/', self.admin_site.admin_view(self.send_notification),
                 name='send_notification_template'),
        ]
        return custom_urls + urls

    def send_notification(self, request, notification_template_id):
        if not self.has_send_permission(request):
            raise PermissionDenied("У вас нет прав для отправки уведомлений.")

        notification_template = self.get_object(request, notification_template_id)

        if request.method == 'POST':
            form = NotificationRecipientForm(request.POST)
            if form.is_valid():
                recipient_group = form.cleaned_data['recipients']
                message_type = form.cleaned_data['message_type']
                send_time = form.cleaned_data['send_time']
                priority = form.cleaned_data['priority']

                response = requests.post(
                    f'{NOTIFICATION_SERVICE_URL}notifications/',
                    headers=prepare_headers(
                        request,
                        {
                            'accept': 'application/json',
                            'Content-Type': 'application/json'
                        }
                    ),
                    json={
                        'type': message_type,
                        'user_id': None,
                        'template_id': str(notification_template_id),
                        'subject': 'admin messaging',
                        'is_delayed': send_time is not None,
                        'send_time': str(send_time),
                        'priority': priority,
                        'recipient_group': recipient_group,
                    }
                )
                if response.status_code == HTTPStatus.OK:
                    self.message_user(
                        request,
                        f"Уведомление успешно отправлено {recipient_group} через {message_type} в {send_time}."
                    )
                else:
                    self.message_user(
                        request,
                        f"Ошибка при отправке уведомления {recipient_group} через {message_type}. "
                        f"Статус код: {response.status_code}.",
                        level='error'
                    )

                return redirect(request.META.get('HTTP_REFERER'))

        else:
            form = NotificationRecipientForm()

        context = {
            'form': form,
            'notification_template': notification_template,
            'title': f'{_("Send message out")}: {notification_template.title}',
        }

        return render(request, 'admin/send_notification.html', context)
