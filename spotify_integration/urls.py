from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.spotify_login, name='spotify-login'),
    path('callback/', views.spotify_callback, name='spotify-callback'),
    path('me/', views.get_spotify_profile, name='spotify-me'),
    path('refresh/', views.refresh_spotify_token, name='spotify-refresh'),
    path('status/', views.spotify_status, name='spotify-status'),
    path('top-genres/', views.get_user_top_genre, name='spotify-status'),
]
