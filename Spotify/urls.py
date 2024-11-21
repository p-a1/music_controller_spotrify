from django.urls import path
from .views import auth_url,spotify_callback,is_authenticated,current_song,play_song,pause_song,skip_song
urlpatterns = [
    path('get-auth-url',auth_url.as_view()),
    path('redirect',spotify_callback),
    path('is_authenticated',is_authenticated.as_view()),
    path('current_song',current_song.as_view()),
    path('pause',pause_song.as_view()),
    path('play',play_song.as_view()),
    path('next',skip_song.as_view())
]