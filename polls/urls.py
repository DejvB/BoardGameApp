from django.urls import path

from . import views

urlpatterns = [
    # ex: /polls/
    path('', views.index, name='home'),
    # ex: /polls/add_boardgame/
    path('add_boardgame/', views.add_boardgame, name='add_game'),
    # ex: /polls/add_play/       whole path http://127.0.0.1:8000/polls/add_play/
    path('add_play/', views.add_play, name='add_play'),
    # ex: /polls/add_player/
    path('add_player/', views.add_player, name='add_player'),
    # ex: /polls/add_results/
    path('add_results/', views.add_results, name='add_results'),
    # ex: /polls/hs/
    path('hs/', views.highscores, name='highscores'),


    path('pie_chart/', views.pie_chart, name='pie-chart'),


    # AJAX
    path('ajax/load_player_count/', views.load_player_count, name='load_player_count'),
    path('ajax/chart_options/', views.load_chart_data, name='chart_options'),

 ]