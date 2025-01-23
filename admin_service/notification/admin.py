from django.contrib import admin
from django.urls import path, reverse
from django.utils.html import format_html
from django.shortcuts import render, redirect
from django.utils.translation import gettext_lazy as _

from .models import NotificationTemplate
from .forms import NotificationRecipientForm
from config.authentication.admin import PermissionAdmin


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(PermissionAdmin):
    resource_name = 'admin:notification_template'
    list_display = ('title', 'template', 'created_at', 'updated_at', 'send_button')
    search_fields = ('title', 'id')

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
        notification_template = self.get_object(request, notification_template_id)

        if request.method == 'POST':
            form = NotificationRecipientForm(request.POST)
            if form.is_valid():
                recipient_type = form.cleaned_data['recipients']
                message_type = form.cleaned_data['message_type']
                send_time = form.cleaned_data['send_time']

                # TODO: Реализовать логику отправки данных в сервис нотификации
                self.message_user(
                    request,
                    f"Уведомление успешно отправлено {recipient_type} через {message_type} в {send_time}."
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
