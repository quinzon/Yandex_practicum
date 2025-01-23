from django.urls import path, include


urlpatterns = [
    path('api/v1/', include('notification.api.v1.urls')),
]
