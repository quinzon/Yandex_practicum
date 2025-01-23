from django import forms
from django.utils.translation import gettext_lazy as _


class NotificationRecipientForm(forms.Form):
    RECIPIENT_CHOICES = [
        ('subscriber', _('Subscriber')),
        ('all_users', _('All users')),
    ]
    MESSAGE_TYPE_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push'),
    ]

    recipients = forms.ChoiceField(choices=RECIPIENT_CHOICES, label=_('Choose recipient'))
    message_type = forms.ChoiceField(choices=MESSAGE_TYPE_CHOICES, label=_('Type of message'))
    send_time = forms.DateTimeField(label=_('Time of send'),
                                    widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
