from django import forms
from django.utils.translation import gettext_lazy as _


class NotificationRecipientForm(forms.Form):
    RECIPIENT_CHOICES = [
        ('subscriber', _('Subscribers')),
        ('all_users', _('All users')),
    ]
    MESSAGE_TYPE_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push'),
    ]

    recipients = forms.ChoiceField(choices=RECIPIENT_CHOICES, label=_('Choose recipient'))
    message_type = forms.ChoiceField(choices=MESSAGE_TYPE_CHOICES, label=_('Type of message'))
    send_time = forms.DateTimeField(
        label=_('Time of send (GMT-0)'),
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        required=False
    )
    priority = forms.IntegerField(
        label=_('Priority (0-7)'),
        min_value=0,
        max_value=7,
        initial=0
    )
