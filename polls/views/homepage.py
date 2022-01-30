import random
from math import ceil
from typing import List

from django.db.models import Count, Max, Q, Sum
from django.db.models.functions import ExtractIsoYear, ExtractMonth, ExtractWeek, ExtractWeekDay, ExtractYear
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render

from polls.models import Boardgames, Gameplay, Player, Results
from polls.views.helpers import my_view


def index(request: HttpRequest) -> HttpResponse:
    request.session['test'] = 'Blue'
    userid = my_view(request)
    games_own_list = games_list = Gameplay.objects.all()
    results_list = Results.objects.all()
    boardgames_list = Boardgames.objects.all()
    if userid:
        bg_owned_list = list(Player.objects.get(id=userid).get_owned(userid))
        games_own_list = games_list.filter(name__id__in=bg_owned_list)
        played_list = Results.objects.filter(p_id__id=userid).values('gp_id__id')
        games_list = games_list.filter(id__in=played_list)
        results_list = results_list.filter(gp_id__id__in=played_list).filter(~Q(p_id__id=userid))
        boardgames_list = boardgames_list.filter(id__in=bg_owned_list)
    else:
        gp_ids = random.choices(list(Gameplay.objects.all().values_list('id', flat=True)), k=10)
        games_list = games_own_list = Gameplay.objects.filter(id__in=gp_ids)
        results_list = Results.objects.filter(gp_id__id__in=gp_ids)
        b_list = games_list.values_list('name__name')
        boardgames_list = Boardgames.objects.filter(name__in=b_list)

    players_list = (
        results_list.values('p_id__name')
        .annotate(Sum('gp_id__time'), Count('gp_id__time'))
        .order_by('-gp_id__time__sum')
    )
    latest_games_list = games_list.order_by('-date')[:5]
    games_name_list = (
        games_list.values('name__name').annotate(game_count=Count('name__name')).annotate(game_time=Sum('time'))
    )
    best_companion = players_list[:5]

    mostplayed_games_list = games_name_list.order_by('-game_count')[:5]
    # For bar plot it must be in list...
    games_for_bar_list = games_name_list.order_by('-game_count')
    leastplayed_games_list = games_name_list.order_by('game_count')[:5]
    long_time_no_see_games_list = (
        games_own_list.values('name__name').annotate(id__max=Max('id'), date=Max('date')).order_by('id__max')[:5]
    )
    mostplayed_games_list_names = [games_for_bar_list[i]['name__name'] for i in range(len(games_for_bar_list))]
    mostplayed_games_list_values = [games_for_bar_list[i]['game_count'] for i in range(len(games_for_bar_list))]
    # games in database which has not been played yet
    not_played_list = list(boardgames_list.values_list('name', flat=True))
    played_list = list(games_name_list.values_list('name__name', flat=True))
    not_played_list = [i for i in not_played_list if i not in played_list]
    mostplayed_games_list_names.extend(not_played_list)
    mostplayed_games_list_values.extend([0] * len(not_played_list))

    time_list = games_name_list.order_by('-game_time')[:5]

    context = {
        'latest_games_list': latest_games_list,
        'mostplayed_games_list': mostplayed_games_list,
        'leastplayed_games_list': leastplayed_games_list,
        'mosttimeplayed_games_list': time_list,
        'long_time_no_see_games_list': long_time_no_see_games_list,
        'best_companion': best_companion,
        'mostplayed_games_list_names': mostplayed_games_list_names,
        'mostplayed_games_list_values': mostplayed_games_list_values,
    }
    # stats per week
    week: List[int] = []
    total_time = []
    total_timestr = []
    total_count = []
    stats = (
        games_list.annotate(year=ExtractIsoYear('date'), week=ExtractWeek('date'))
        .values('year', 'week')
        .annotate(Sum('time'), Count('time'))
    )
    for stat in stats:
        if week and stat['week'] != week[-1] + 1 and stat['week'] != 1:
            for missing_week in range(week[-1] + 1, stat['week']):
                week.append(missing_week)
                total_time.append(0)
                total_timestr.append(str(0))
                total_count.append(0)
        week.append(stat['week'])
        total_time.append(stat['time__sum'].days * 1000 * 86400 + stat['time__sum'].seconds * 1000)
        total_timestr.append(str(stat['time__sum']))
        total_count.append(stat['time__count'])

    # avg time per game
    avg = int(sum(total_time) / sum(total_count))
    # max number of game equivalent to avg time per game
    mg = ceil(max(total_time) / (sum(total_time) / sum(total_count)))
    mg = max(mg, max(total_count))

    # time equivalent to mg with avg time per game
    mt = mg * avg
    context['week'] = week
    context['totalTime'] = total_time
    context['total_timestr'] = total_timestr
    context['totalCount'] = total_count
    context['mg'] = mg
    context['mt'] = mt

    # stats per month
    month = []
    total_time_month = []
    total_timestr_month = []
    total_count_month = []
    stats = (
        games_list.annotate(year=ExtractYear('date'), month=ExtractMonth('date'))
        .values('year', 'month')
        .annotate(Sum('time'), Count('time'))
    )
    for stat in stats:
        month.append(stat['month'])
        total_time_month.append(stat['time__sum'].days * 1000 * 86400 + stat['time__sum'].seconds * 1000)
        total_timestr_month.append(str(stat['time__sum']))
        total_count_month.append(stat['time__count'])
    # print(stats)
    context['month'] = month
    context['totalTime_month'] = total_time_month
    context['total_timestr_month'] = total_timestr_month
    context['totalCount_month'] = total_count_month

    weekdays = list(
        games_list.annotate(weekday=ExtractWeekDay('date'))
        .values('weekday')
        .annotate(Count('time'))
        .values_list('weekday', 'time__count')
    )
    weekday = [0] * 7
    for day in weekdays:
        weekday[day[0] - 1] = day[1]
    weekday = weekday[1:] + [weekday[0]]
    context['weekday'] = weekday
    context['players'] = Player.objects.all()
    return render(request, 'polls/index.html', context)


def god_button(request: HttpRequest) -> JsonResponse:
    request.session['fake_id'] = request.GET.get('fake_id')
    return JsonResponse(data={})
