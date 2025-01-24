from rest_framework import serializers
from notification.models import NotificationTemplate


class NotificationTemplateModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationTemplate
        fields = '__all__'


class UserDataSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255)
    first_name = serializers.CharField(max_length=50, allow_null=True)
    last_name = serializers.CharField(max_length=50, allow_null=True)
