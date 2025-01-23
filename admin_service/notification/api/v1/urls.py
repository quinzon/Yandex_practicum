from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

from .views import NotificationTemplateViewSet, get_user_data

router = DefaultRouter()
router.register(r'template', NotificationTemplateViewSet)

urlpatterns = [
    path('', include(router.urls)),

    path('users/', get_user_data, name='get_user_data'),

    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
