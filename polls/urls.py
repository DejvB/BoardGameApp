from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

from .views import helpers, gamebrary
from .views.adds import results_specifics, specifics

urlpatterns = [
    # ex: /polls/
    path('', views.index, name='home'),
    # ex: /polls/add_boardgame/
    path('add_boardgame/', views.add_boardgame, name='add_game'),
    path('add_boardgame/<int:page>', views.add_boardgame, name='add_game'),
    # ex: /polls/add_boardgame/
    path('add_boardgame_old/', views.add_boardgame_old, name='add_bg_old'),
    # ex: /polls/add_play/   whole path http://127.0.0.1:8000/polls/add_play/
    path('add_play/', views.add_play, name='add_play'),
    # ex: /polls/add_player/
    path('add_player/', views.add_player, name='add_player'),
    # ex: /polls/add_expansion/
    path('add_expansion/', views.add_expansion, name='add_expansion'),
    path('add_expansion_old/', views.add_expansion_old, name='add_exp_old'),
    # ex: /polls/add_results/
    path('add_results/', views.add_results, name='add_results'),
    path('add_results/<str:gp_id>', views.add_results, name='add_results'),
    path('add_results_specifics/', results_specifics.add_results_specifics, name='add_results_specifics'),
    path('edit_results_specifics/<str:gp_id>', helpers.edit_results_specifics, name='edit_results_specifics'),
    path('add_specifics/', specifics.add_specifics, name='add_specifics'),
    # ex: /polls/hs/
    path('hs/', views.highscores, name='highscores'),
    # ex: /polls/history/
    path('history/', views.history, name='history'),
    # ex: /polls/playerstats/
    path('playerstats/', views.playerstats, name='playerstats'),
    # registration page
    path('register/', views.register_request, name='register'),
    # login page
    path('login/', views.login_request, name='login'),
    # logout page
    path('logout/', LogoutView.as_view(), name='logout'),
    path('pie_chart/', views.pie_chart, name='pie-chart'),
    path('userpage/', views.userpage, name='userpage'),
    path('userpage/gamebrary/', gamebrary.gamebrary, name='gamebrary'),
    path('userpage/gamebrary/<str:sort_key>/', gamebrary.gamebrary, name='gamebrary'),
    path('plus_result/', views.plus_result, name='plus_result'),
    path('plus_result/<str:site>/', views.plus_result, name='plus_result'),
    path('plus_result/<str:site>/<str:gp_id>/', views.plus_result, name='plus_result'),
    path('minus_result/', views.minus_result, name='minus_result'),
    path('minus_result/<str:site>/', views.minus_result, name='minus_result'),
    path('minus_result/<str:site>/<str:gp_id>/', views.minus_result, name='minus_result'),
    # AJAX new_game_in_library
    path(
        'ajax/load_player_count/',
        views.load_player_count,
        name='load_player_count',
    ),
    path(
        'ajax/new_game_in_library/',
        views.new_game_in_library,
        name='new_game_in_library',
    ),
    path(
        'ajax/new_exp_in_library/',
        views.new_exp_in_library,
        name='new_exp_in_library',
    ),
    path(
        'ajax/expansions_select_options/',
        views.expansions_select_options,
        name='expansions_select_options',
    ),
    path(
        'ajax/load_playerstats/',
        views.load_playerstats,
        name='load_playerstats',
    ),
    path('ajax/chart_options/', views.load_chart_data, name='chart_options'),
    path('ajax/get_history/', views.get_history, name='get_history'),
    path('ajax/randomizer/', views.randomizer, name='randomizer'),
    path('ajax/basic_stats/', views.basic_stats, name='basic_stats'),
    path('ajax/god_button/', views.god_button, name='god_button'),
    path('ajax/bg_submit/', views.bg_submit, name='bg_submit'),
    path('ajax/exp_submit/', views.exp_submit, name='exp_submit'),
    path('ajax/specifics_list/', specifics.specifics_list, name='specifics_list'),
    path(
        'ajax/expansions_dropdown_options/',
        views.expansions_dropdown_options,
        name='expansions_dropdown_options',
    ),
    path(
        'ajax/add_results_specifics_to_existing_game/',
        specifics.add_results_specifics_to_existing_game,
        name='add_results_specifics_to_existing_game',
    ),
    path(
        'ajax/boardgame_box/',
        views.load_boardgame_box,
        name='boardgame_box',
    ),
]
