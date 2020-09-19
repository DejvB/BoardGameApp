from django.urls import path

from . import views

urlpatterns = [
    # ex: /polls/
    path('', views.index, name='home'),
    # ex: /polls/add_boardgame/
    path('add_boardgame/', views.add_boardgame, name='add_game'),
    # ex: /polls/add_playgame/       whole path http://127.0.0.1:8000/polls/add_play/
    path('add_play/', views.add_play, name='add_play'),
    # # ex: /polls/last_played_games/
    # path('last_played_games/', views.last_played_games, name='games'),
]