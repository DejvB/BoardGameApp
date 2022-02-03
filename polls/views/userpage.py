import datetime
import numpy as np
from collections import Counter

from django.contrib.auth.decorators import login_required
from django.db.models.functions import (
    ExtractIsoYear,
    ExtractMonth,
    ExtractWeek,
)
from django.shortcuts import render

from polls.forms import OwnBoardgameForm, OwnExpansionForm

from ..models import Player, Boardgames
from .helpers import get_bgg_info, my_view, show_success_tooltip


@login_required
def userpage(request):
    userid = my_view(request)
    bg_owned_list = Player.objects.get(id=userid).get_owned(userid)
    data = {
        'rank': [],
        'weight': [],
        'year': [],
        'mechanics': [],
        'category': [],
        'designer': [],
    }
    for bg_id in bg_owned_list:
        bgg_info = get_bgg_info(bg_id)
        data['rank'].append(float(bgg_info['rank']))
        data['weight'].append(float(bgg_info['weight']))
        data['year'].append(int(bgg_info['year']))
        data['mechanics'].extend(bgg_info['mechanics'])
        data['category'].extend(bgg_info['category'])
        data['designer'].extend(bgg_info['designer'])
    weight_bins = np.linspace(1, 5, 9)
    rank_bins = np.linspace(0, 10, 21)
    year_bins = np.linspace(min(data['year']),
                            max(data['year']),
                            max(data['year']) - min(data['year']) + 1)
    context = {
        'NoG': len(bg_owned_list),
        'ranks': list(np.histogram(data['rank'], bins=rank_bins)[0]),
        'weight_bins': list(weight_bins),
        'rank_bins': list(rank_bins),
        'year_bins': list(year_bins),
        'weights': list(np.histogram(data['weight'], bins=weight_bins)[0]),
        'years': list(np.histogram(data['year'], bins=year_bins)[0]),
        'MoC': Counter(data['category']).most_common(3),
        'MoM': Counter(data['mechanics']).most_common(3),
        'MoD': Counter(data['designer']).most_common(3),
    }
    games_list = Player.objects.get(id=userid).get_played(userid)
    games_list = games_list.annotate(
        year=ExtractIsoYear('date'),
        month=ExtractMonth('date'),
        week=ExtractWeek('date'),
    )
    # gameplays vs previous week
    curr_year, curr_week, _ = datetime.date.today().isocalendar()
    prev_year, prev_week, _ = (
        datetime.date.today() - datetime.timedelta(days=7)
    ).isocalendar()
    week_diff = [
        games_list.filter(year=curr_year, week=curr_week).count(),
        -games_list.filter(year=prev_year, week=prev_week).count(),
    ]

    # gameplays vs previous month
    curr_month = datetime.date.today().month
    prev_month = curr_month - 1 if curr_month > 1 else 12
    prev_year = curr_year if curr_month > 1 else curr_year - 1
    month_diff = [
        games_list.filter(year=curr_year, month=curr_month).count(),
        -games_list.filter(year=prev_year, month=prev_month).count(),
    ]

    # gameplays vs previous month
    year_diff = [
        games_list.filter(year=curr_year).count(),
        -games_list.filter(year=prev_year).count(),
    ]
    context.update(
        {
            'week_diff': week_diff,
            'month_diff': month_diff,
            'year_diff': year_diff,
        }
    )
    context.update(new_game_in_library(request, userid))
    context.update(new_exp_in_library(request, userid))
    return render(request, 'polls/userpage.html', context)


def new_game_in_library(request, userid):
    context = {}
    newgame_form = OwnBoardgameForm(initial={'p_id': userid})
    if request.method == 'POST' and 'add_game' in request.POST:
        newgame_form = OwnBoardgameForm(request.POST)
        if newgame_form.is_valid():
            b = newgame_form.save()
            b.save()
            show_success_tooltip(context, 'tooltip_board')
        newgame_form = OwnBoardgameForm(initial={'p_id': userid})
    context['newgame_form'] = newgame_form
    return context


def new_exp_in_library(request, userid):
    context = {}
    newexp_form = OwnExpansionForm(initial={'p_id': userid},)
    if request.method == 'POST' and 'add_exp' in request.POST:
        newexp_form = OwnExpansionForm(request.POST)
        if newexp_form.is_valid():
            e = newexp_form.save(commit=False)
            e.bg_id = newexp_form.cleaned_data['expansion']
            e.save()
            show_success_tooltip(context, 'tooltip_exp')
        newexp_form = OwnExpansionForm(initial={'p_id': userid})
    context['newexp_form'] = newexp_form
    return context


def expansions_dropdown_options(request):
    basegame_id = request.GET.get('basegame_id')
    expansions = Boardgames.objects.filter(basegame__id=basegame_id).order_by('name')
    return render(request, 'polls/expansions_dropdown_options.html', {'expansions': expansions})
