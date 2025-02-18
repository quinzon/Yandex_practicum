from django.urls import path
from profiles.views import profiles, search_profiles

urlpatterns = [
    path('', profiles, name='profiles'),
    path('search_profiles/', search_profiles, name='search_profiles'),
]
