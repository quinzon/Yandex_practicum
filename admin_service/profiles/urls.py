from django.urls import path
from profiles.views import profiles, get_profiles, find_profile

urlpatterns = [
    path('', profiles, name='profiles'),
    path('get_profiles/', get_profiles, name='get_profiles'),
    path('find_profile/', find_profile, name='find_profile'),
]
