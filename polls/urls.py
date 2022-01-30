from django.contrib.auth.views import LogoutView
from django.urls import path

from polls.views.adds.boardgame import add_boardgame, add_boardgame_old, bg_submit
from polls.views.adds.expansion import add_expansion
from polls.views.adds.gameplay import add_play, basic_stats, expansions_select_options, load_player_count, randomizer
from polls.views.adds.player import add_player
from polls.views.adds.results import add_results
from polls.views.highscore import highscores, load_chart_data
from polls.views.history import get_history, history
from polls.views.homepage import god_button, index
from polls.views.login import login_request
from polls.views.pie_graph import pie_chart
from polls.views.registration import register_request
from polls.views.statistics import load_playerstats, playerstats
from polls.views.userpage import new_exp_in_library, new_game_in_library, userpage


urlpatterns = [
    # ex: /polls/
    path('', index, name='home'),
    # ex: /polls/add_boardgame/
    path('add_boardgame/', add_boardgame, name='add_game'),
    # ex: /polls/add_boardgame/
    path('add_boardgame_old/', add_boardgame_old, name='add_bg_old'),
    # ex: /polls/add_play/   whole path http://127.0.0.1:8000/polls/add_play/
    path('add_play/', add_play, name='add_play'),
    # ex: /polls/add_player/
    path('add_player/', add_player, name='add_player'),
    # ex: /polls/add_expansion/
    path('add_expansion/', add_expansion, name='add_expansion'),
    # ex: /polls/add_results/
    path('add_results/', add_results, name='add_results'),
    # ex: /polls/hs/
    path('hs/', highscores, name='highscores'),
    # ex: /polls/history/
    path('history/', history, name='history'),
    # ex: /polls/playerstats/
    path('playerstats/', playerstats, name='playerstats'),
    # registration page
    path('register/', register_request, name='register'),
    # login page
    path('login/', login_request, name='login'),
    # logout page
    path('logout/', LogoutView.as_view(), name='logout'),
    path('pie_chart/', pie_chart, name='pie-chart'),
    path('userpage/', userpage, name='userpage'),
    # AJAX new_game_in_library
    path('ajax/load_player_count/', load_player_count, name='load_player_count'),
    path('ajax/new_game_in_library/', new_game_in_library, name='new_game_in_library'),
    path('ajax/new_exp_in_library/', new_exp_in_library, name='new_exp_in_library'),
    path('ajax/expansions_select_options/', expansions_select_options, name='expansions_select_options'),
    path('ajax/load_playerstats/', load_playerstats, name='load_playerstats'),
    path('ajax/chart_options/', load_chart_data, name='chart_options'),
    path('ajax/get_history/', get_history, name='get_history'),
    path('ajax/randomizer/', randomizer, name='randomizer'),
    path('ajax/basic_stats/', basic_stats, name='basic_stats'),
    path('ajax/god_button/', god_button, name='god_button'),
    path('ajax/bg_submit/', bg_submit, name='bg_submit'),
]
