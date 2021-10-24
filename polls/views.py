from django.shortcuts import render, redirect
# from django.template import loader

# from .models import *
from .forms import *

from django.db.models import Count, Sum, Q, Avg, Max, Min, F, ExpressionWrapper, fields, Value, DateTimeField
from django.db.models.functions import ExtractWeek, ExtractWeekDay, ExtractMonth, ExtractYear, ExtractIsoYear
from math import ceil
from django.contrib.auth.decorators import login_required



def compute_score(o, n):
    return (n - o + 1) / n


from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
# from django.contrib import messages

@login_required
def register_request(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect('home')
        messages.error(request, "Unsuccessful registration. Invalid information.")
    form = NewUserForm()
    return render(request=request, template_name="polls/register.html", context={"register_form": form})


def login_request(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect("home")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    form = AuthenticationForm()
    return render(request=request, template_name="polls/login.html", context={"login_form": form})


def my_view(request):
    userid = None
    if request.user.is_authenticated:
        userid = request.user.player.id
    return userid


def index(request):
    userid = my_view(request)
    games_own_list = games_list = Gameplay.objects.all()
    results_list = Results.objects.all()
    boardgames_list = Boardgames.objects.all()
    if userid:
        games_own_list = games_list.filter(name__owner__id=userid)
        played_list = Results.objects.filter(p_id__id=userid).values('gp_id__id')
        # print(Results.objects.filter(p_id__name=userid).values('gp_id__name__name'))
        games_list = games_list.filter(id__in=played_list)
        results_list = results_list.filter(gp_id__name__in=played_list).filter(~Q(p_id__id=userid))
        boardgames_list = boardgames_list.filter(owner__id=userid)

    players_list = results_list.values('p_id__name').annotate(Sum('gp_id__time'), Count('gp_id__time')).order_by('-gp_id__time__sum')
    latest_games_list = games_list.order_by('-date')[:5]
    games_name_list = games_list.values('name__name').annotate(game_count=Count('name__name')).annotate(game_time=Sum('time'))
    best_companion = players_list[:5]

    mostplayed_games_list = games_name_list.order_by('-game_count')[:5]
    # For bar plot it must be in list...
    games_for_bar_list = games_name_list.order_by('-game_count')
    leastplayed_games_list = games_name_list.order_by('game_count')[:5]
    long_time_no_see_games_list = games_own_list.values('name__name') \
                                      .annotate(id__max=Max('id'),
                                                date=Max('date')) \
                                      .order_by('id__max')[:5]
    mostplayed_games_list_names = [games_for_bar_list[i]['name__name'] for i in range(len(games_for_bar_list))]
    mostplayed_games_list_values = [games_for_bar_list[i]['game_count'] for i in range(len(games_for_bar_list))]
    # games in database which has not been played yet
    not_played_list = list(boardgames_list.values_list('name', flat=True))
    played_list = list(games_name_list.values_list('name__name', flat=True))
    not_played_list = [i for i in not_played_list if i not in played_list]
    mostplayed_games_list_names.extend(not_played_list)
    mostplayed_games_list_values.extend([0] * len(not_played_list))

    time_list = games_name_list.order_by('-game_time')[:5]
    # games_name_list = Gameplay.objects.values('name__name', 'date').annotate(game_count=Count('name__name'))

    context = {'latest_games_list': latest_games_list,
               'mostplayed_games_list': mostplayed_games_list,
               'leastplayed_games_list': leastplayed_games_list,
               'mosttimeplayed_games_list': time_list,
               'long_time_no_see_games_list': long_time_no_see_games_list,
               'best_companion': best_companion,
               'mostplayed_games_list_names': mostplayed_games_list_names,
               'mostplayed_games_list_values': mostplayed_games_list_values
               }
    # stats per week
    week = []
    totalTime = []
    totalTimestr = []
    totalCount = []
    stats = games_list.annotate(year=ExtractIsoYear('date'), week=ExtractWeek('date')).values('year',
                                                                                                    'week').annotate(
        Sum('time'), Count('time'))
    for stat in stats:
        if week and stat['week'] != week[-1] + 1 and stat['week'] != 1:
            for missing_week in range(week[-1] + 1, stat['week']):
                week.append(missing_week)
                totalTime.append(0)
                totalTimestr.append(str(0))
                totalCount.append(0)
        week.append(stat['week'])
        totalTime.append(stat['time__sum'].seconds * 1000)
        totalTimestr.append(str(stat['time__sum']))
        totalCount.append(stat['time__count'])

    # avg time per game
    avg = int(sum(totalTime) / sum(totalCount))
    # max number of game equivalent to avg time per game
    mg = ceil(max(totalTime) / (sum(totalTime) / sum(totalCount)))
    mg = max(mg, max(totalCount))

    # time equivalent to mg with avg time per game
    mt = mg * avg
    context['week'] = week
    context['totalTime'] = totalTime
    context['totalTimestr'] = totalTimestr
    context['totalCount'] = totalCount
    context['mg'] = mg
    context['mt'] = mt

    # stats per month
    month = []
    totalTime_month = []
    totalTimestr_month = []
    totalCount_month = []
    stats = games_list.annotate(year=ExtractYear('date'), month=ExtractMonth('date')).values('year',
                                                                                                   'month').annotate(
        Sum('time'), Count('time'))
    for stat in stats:
        month.append(stat['month'])
        totalTime_month.append(stat['time__sum'].days * 1000 * 86400 + stat['time__sum'].seconds * 1000)
        totalTimestr_month.append(str(stat['time__sum']))
        totalCount_month.append(stat['time__count'])
    # print(stats)
    context['month'] = month
    context['totalTime_month'] = totalTime_month
    context['totalTimestr_month'] = totalTimestr_month
    context['totalCount_month'] = totalCount_month

    weekday = list(
        games_list.annotate(weekday=ExtractWeekDay('date')).values('weekday').annotate(Count('time')).values_list(
            'time__count', flat=True))
    weekday = weekday[1:] + [weekday[0]]
    context['weekday'] = weekday
    return render(request, 'polls/index.html', context)


@login_required
def add_boardgame(request):
    context = {}
    form = BoardgameForm()
    if request.method == 'POST':  # and 'run_script' in request.POST:
        form = BoardgameForm(request.POST)
        if form.is_valid():
            b = form.save()
            b.save()
        return redirect('home')
    context['form'] = form
    return render(request, 'polls/add_boardgame.html', context)


@login_required
def add_play(request):
    context = {}
    gp_form = GameplayForm()

    Expansions = []
    Expansionformset = formset_factory(UsedExpansionForm, extra=0)  # len(Expansions))
    e_formset = Expansionformset(request.POST or None,
                                 initial=[{'e_id': Expansions[i], 'gp_id': bg_id} for i in range(len(Expansions))])
    if request.method == 'POST':
        gp_form = GameplayForm(request.POST)
        if gp_form.is_valid() and e_formset.is_valid():  # can be and e_formset.is_valid()
            gp = gp_form.save()
            gp.save()
            # print(gp.name.id)
            #
            #
            #     Expansions = list(
            #         Expansion
            #             .objects
            #             .filter(basegame__id=gp.name.id)
            #             .order_by('name')
            #             .values_list('id', flat=True))
            # for i, e_form in enumerate(e_formset):
            #     print(e_form)
            #     e_form.gp_id = gp.id
            #     e_form.e_id = Expansions[i]
            for e_form in e_formset:
                e = e_form.save()
                e.gp_id = gp
                e.save()
            if gp.with_results:
                return redirect('add_results')
            else:
                return redirect('add_results')
    context['gp_form'] = gp_form
    context['e_formset'] = e_formset
    context['boardgame'] = Boardgames.objects.all()
    # context['players'] = range(1,7)
    return render(request, 'polls/add_game.html', context)


def randomizer(request):
    games = list(Boardgames.objects.all().values_list('name', flat=True))
    return JsonResponse(data={'games': games})


def expansions_select_options(request):
    bg_id = request.GET.get('name')
    Expansions = list(Expansion.objects.filter(basegame__id=bg_id).order_by('name').values_list('id', flat=True))
    ExpansionsNames = list(Expansion.objects.filter(basegame__id=bg_id).order_by('name').values_list('name', flat=True))
    Expansionformset = formset_factory(UsedExpansionForm, extra=0)  # len(Expansions))
    Gameplays = list(Gameplay.objects.all().order_by('name').values_list('name', flat=True))
    e_formset = Expansionformset(request.POST or None,
                                 initial=[{'e_id': Expansions[i], 'gp_id': Gameplays[0]} for i in
                                          range(len(Expansions))])

    return render(request, 'polls/expansions_select_options.html', {'e_formset': e_formset,
                                                                    'Expansions': Expansions,
                                                                    'ExpansionsNames': ExpansionsNames, 'tex': 'haha'})


def load_player_count(request):
    bg_id = request.GET.get('name')
    playersRange = Boardgames.objects.filter(id=bg_id).values('minNumberOfPlayers', 'maxNumberOfPlayers')[0]
    minP = playersRange['minNumberOfPlayers']
    maxP = playersRange['maxNumberOfPlayers']
    PossibleNumberOfPlayers = range(minP, maxP + 1)

    return render(request, 'polls/players_dropdown_options.html', {'PossibleNumberOfPlayers': PossibleNumberOfPlayers})


def basic_stats(request):
    # basic stats for new gameplay page
    bg_id = request.GET.get('name')
    game_id = Gameplay.objects.filter(name__id=bg_id).values('id').order_by('-id')[0]['id']
    result = Results.objects.filter(gp_id__id=game_id).values('p_id__name', 'points')
    result = [[r['p_id__name'], r['points']] for r in result]
    queryset = Results.objects.filter(gp_id__name__id=bg_id) \
        .filter(gp_id__with_results=True) \
        .values('gp_id', 'p_id__name', 'gp_id__NumberOfPlayers', 'points', 'order').order_by('-points')
    maxws = queryset[0]['points']
    minws = queryset.filter(order=1).order_by('points')[0]['points']
    avgws = round(queryset.filter(order=1).aggregate(Avg('points'))['points__avg'], 2)
    avgtot = round(queryset.aggregate(Avg('points'))['points__avg'], 2)
    maxnws = queryset.filter(order=2)[0]['points']

    return JsonResponse(data={'result': result,
                              'maxws': maxws,
                              'minws': minws,
                              'avgws': avgws,
                              'avgtot': avgtot,
                              'maxnws': maxnws,
                              })


@login_required
def add_expansion(request):
    context = {}
    form = ExpansionForm()
    if request.method == 'POST':
        form = ExpansionForm(request.POST)
        if form.is_valid():
            e = form.save()
            e.save()
            return redirect('home')
    context['form'] = form
    return render(request, 'polls/add_expansion.html', context)


@login_required
def add_player(request):
    context = {}
    form = PlayerForm()
    if request.method == 'POST':
        form = PlayerForm(request.POST)
        if form.is_valid():
            p = form.save()
            p.save()
        return redirect('home')
    context['form'] = form
    return render(request, 'polls/add_player.html', context)


from django.forms import formset_factory
from django.contrib import messages


@login_required
def add_results(request):
    # if 'player_count' in request.session:
    #     print(request.session['player_count'])
    lastGame = Gameplay.objects.order_by('-id')[0]
    ResultsFormSet = formset_factory(ResultsForm, extra=0)
    if lastGame.with_results:
        formset = ResultsFormSet(request.POST or None, initial=[{'order': i + 1, 'gp_id': lastGame} for i in
                                                                range(max(2, lastGame.NumberOfPlayers))])
    else:
        formset = ResultsFormSet(request.POST or None, initial=[{'order': 0, 'gp_id': lastGame} for _ in
                                                                range(max(2, lastGame.NumberOfPlayers))])
    if formset.is_valid():
        messages.success(request, 'Form submission successful')
        for form in formset:
            r = form.save()
            r.save()
        if lastGame.with_results:
            changes = compute_tournament(lastGame.results.all())
            update_elo(changes)
            print(changes)
        return redirect('home')
    return render(request, 'polls/add_results.html', {'formset': formset})


def pie_chart(request):
    labels = []
    data = []
    colors = []
    context = {}
    players = Player.objects.order_by('name').values_list('name', flat=True)

    # for gameplayes with three of us
    if False:
        queryset = Results.objects.values('gp_id', 'p_id__name',
                                          'gp_id__NumberOfPlayers', 'points',
                                          'order').order_by('-points')
        gp_queryset = list(Gameplay.objects.values_list('id', flat=True))
        gp_queryset_forloop = gp_queryset.copy()
        for gp in gp_queryset_forloop:
            for n in ['David', 'Bára']:
                if not queryset.filter(gp_id=gp).filter(p_id__name=n):
                    gp_queryset.remove(gp)
                    break
    else:
        gp_queryset = list(Gameplay.objects.values_list('id', flat=True))

    # points
    points = []
    for player in players:
        p_sum = 0
        queryset = Results.objects.filter(p_id__name=player).filter(order__gte=1).values('p_id__name',
                                                                                         'gp_id__NumberOfPlayers',
                                                                                         'order')
        for query in queryset:
            p_sum = p_sum + compute_score(query['order'], query['gp_id__NumberOfPlayers'])
        points.append([player, round(p_sum / len(queryset), 3)])
    context['points'] = sorted(points, key=lambda x: -x[1])
    for i in range(6):
        data.append([])
        # queryset = Results.objects.filter(order=i + 1).values('p_id__name').annotate(total=Count('p_id__name'))

        queryset = Results.objects.filter(gp_id__in=gp_queryset).filter(order=i + 1).values('p_id__name').annotate(
            total=Count('p_id__name'))

        for player in players:
            if len(Results.objects.filter(p_id__name=player).values(
                    'p_id__name')) < 10:  # this is kind of stupid - I could filter players before
                continue
            p = queryset.filter(p_id__name=player)
            try:
                data[i].append(p[0]['total'])
            except:
                data[i].append(0)
            if i == 0:
                labels.append(player)
                colors.append(Player.objects.filter(name=player).values_list('color', flat=True)[0])
    context['labels'] = labels
    context['colors'] = colors
    context['data0'] = data[0]
    context['data1'] = data[1]
    context['data2'] = data[2]
    context['data3'] = data[3]
    context['data4'] = data[4]
    context['data5'] = data[5]
    # print(queryset)
    return render(request, 'polls/pie_chart.html', context)


def highscores(request):
    userid = my_view(request)
    gameplays = Gameplay.objects.all()
    if userid:
        played_list = Results.objects.filter(p_id__id=userid).values('gp_id__id')
        gameplays = gameplays.filter(id__in=played_list)

    context = {'boardgames': gameplays.values('name__name').distinct().order_by('name__name'),
               'lastgame': gameplays.latest('date').name}

    # datas = ['1','2','3']
    # colors = ['#FFB6C1','#ADD8E6','#90EE90','#ffcccb''#FFFF66']
    # labels = ['a','b','v']
    #
    # context['labels'] = labels
    # context['colors'] = colors
    # context['data'] = datas
    return render(request, 'polls/highscores.html', context)


from django.http import JsonResponse


def load_chart_data(request):
    userid = my_view(request)
    labels = []
    data = []
    colors = []
    display = []
    names = []
    position = []
    diff = []

    bg_name = request.GET.get('name')
    p_count = request.GET.get('NoP')
    chk = request.GET.get('chk')
    gameplays = Gameplay.objects.filter(name__name=bg_name)
    queryset = Results.objects.filter(gp_id__name__name=bg_name) \
        .filter(gp_id__with_results=True) \
        .values('gp_id', 'p_id__name', 'gp_id__NumberOfPlayers', 'points', 'order').order_by('-points')
    if userid:
        played_list = Results.objects.filter(p_id__id=userid).values('gp_id__id')
        queryset = queryset.filter(gp_id__in=played_list)
        gameplays = gameplays.filter(id__in=played_list)
    if chk == 'true':
        gp_queryset = list(Gameplay.objects.filter(name__name=bg_name).values_list('id', flat=True))
        gp_queryset_forloop = gp_queryset.copy()
        for gp in gp_queryset_forloop:
            for n in ['David', 'Bára', 'Adam']:
                if not queryset.filter(gp_id=gp).filter(p_id__name=n):
                    gp_queryset.remove(gp)
                    break
        queryset = Results.objects.filter(gp_id__in=gp_queryset) \
            .filter(gp_id__with_results=True) \
            .values('p_id__name', 'gp_id__NumberOfPlayers',
                    'points', 'order').order_by('-points')

    for query in queryset:
        if (str(query['gp_id__NumberOfPlayers'])) in labels:
            display.append(False)
        else:
            display.append(True)
        data.append([query['points']])
        # colors.append(c[query['p_id__name']])
        colors.append(Player.objects.filter(name=query['p_id__name']).values_list('color', flat=True)[0])
        labels.append(str(query['gp_id__NumberOfPlayers']))
        names.append(query['p_id__name'])
        position.append(query['order'])

    # queryset = Results.objects.filter(gp_id__name__name=bg_name).values('gp_id', 'points', 'order').order_by('-points')
    # print(queryset)
    maxws = queryset[0]['points']
    minws = queryset.filter(order=1).order_by('points')[0]['points']
    avgws = round(queryset.filter(order=1).aggregate(Avg('points'))['points__avg'], 2)
    avgtot = round(queryset.aggregate(Avg('points'))['points__avg'], 2)
    try:
        maxnws = queryset.filter(order=2)[0]['points']
    except:
        maxnws = 0
    queryset_gp = gameplays.values('time')
    longest_gp = str(queryset_gp.order_by('-time')[0]['time'])
    sg = str(queryset_gp.order_by('time')[0]['time'])
    avgg = str(queryset_gp.aggregate(Avg('time'))['time__avg'])

    gp_id_queryset = list(gameplays.values_list('id', flat=True))
    for gp_id in gp_id_queryset:
        q = queryset.filter(gp_id=gp_id)
        try:
            diff.append(q.filter(order=1)[0]['points'] - q.filter(order=2)[0]['points'])
        except:
            diff =[0]
            # empty queryset. You take id from all gp, not just from games with all three
            pass
    avgmp = round(sum(diff) / len(diff), 2)
    uw = queryset.filter(order=1).values('p_id__name').annotate(Count('p_id__name')).order_by('-p_id__name__count')[0][
        'p_id__name']
    avgp = []
    pp = sorted(list(
        gameplays.values('NumberOfPlayers').distinct().values_list('NumberOfPlayers',
                                                                                                     flat=True)))
    for i in pp:
        avgp.append(list(
            queryset.filter(gp_id__NumberOfPlayers=i).values('p_id__name', 'gp_id__NumberOfPlayers').annotate(
                Avg('points')).order_by('-points__avg').values_list('p_id__name', 'points__avg')))
    gp_list = list(gameplays.order_by('date').values_list('date', flat=True))
    first_gp = gp_list[0].date()
    last_gp = gp_list[-1].date()
    nogp = len(gp_list)

    order_data = []
    for p in Player.objects.all():
        player_exists = False
        count = 0
        p_order = [{'x': 0, 'y': 'Nan'}]
        p_points = [{'x': 0, 'y': 'Nan'}]
        for ids in list(queryset.values('gp_id').order_by('gp_id').distinct().values_list('gp_id', flat=True)):
            count += 1
            order = queryset.filter(p_id__name=p).filter(gp_id=ids).values('order')
            points = queryset.filter(p_id__name=p).filter(gp_id=ids).values('points')
            if order:
                p_order.append({'x': count, 'y': order[0]['order']})
                p_points.append({'x': count, 'y': points[0]['points']})
                player_exists = True
            else:
                p_order.append({'x': count, 'y': 'Nan'})
                p_points.append({'x': count, 'y': 'Nan'})
        p_order.append({'x': count + 1, 'y': 'Nan'})
        p_points.append({'x': count + 1, 'y': 'Nan'})
        if player_exists:
            order_data.append([p.name, p.color, p_order, p_points])
    # print(order_data)
    ## attempt without x and y and with global x axis
    # order_data = []
    # for p in Player.objects.all():
    #     p_order = []
    #     p_points = []
    #     for ids in list(queryset.values('gp_id').order_by('gp_id').distinct().values_list('gp_id', flat=True)):
    #         order = queryset.filter(p_id__name=p).filter(gp_id=ids).values('order','points')
    #         if order:
    #             p_order.append(order[0]['order'])
    #             p_points.append(order[0]['points'])
    #         else:
    #             p_order.append('Nan')
    #             p_points.append('Nan')
    #     if p_order:
    #         order_data.append([p.name, p.color, p_order, p_points])
    # order_x_axis = range(1, len(list(queryset.values('gp_id').order_by('gp_id').distinct().values_list('gp_id', flat=True))) + 1)
    # print(order_data)

    # for i in pp:
    #     hm = queryset.filter(gp_id__NumberOfPlayers=i).values('p_id__name', 'gp_id__NumberOfPlayers')
    #     hm.
    #     denominator = X.dot(X) - X.mean() * X.sum()
    #     a = (X.dot(Y) - Y.mean() * X.sum()) / denominator
    #     # b = (Y.mean() * X.dot(X) - X.mean() * X.dot(Y)) / denominator

    return JsonResponse(data={'labels': labels,
                              'data': data,
                              'colors': colors,
                              'display': display,
                              'names': names,
                              'position': position,
                              'maxws': maxws,
                              'minws': minws,
                              'avgws': avgws,
                              'avgtot': avgtot,
                              'maxnws': maxnws,
                              'longest_gp': longest_gp,
                              'sg': sg,
                              'avgg': avgg,
                              'avgmp': avgmp,
                              'uw': uw,
                              'pp': pp,
                              'avgp': avgp,
                              'first_gp': first_gp,
                              'last_gp': last_gp,
                              'nogp': nogp,
                              'order_data': order_data,
                              })


def history(request):
    context = {}
    context['games'] = GameplayTable(Gameplay.objects.all().order_by('date'))
    return render(request, 'polls/history.html', context)


from .tables import GameplayTable


def get_history(request):
    fromdate = request.GET.get('from')
    todate = request.GET.get('to')
    games = GameplayTable(Gameplay.objects.filter(date__range=[fromdate, todate]))
    return render(request, "polls/get_history.html", {"games": games})

elos = {}
elo_history = {}

def playerstats(request):
    global elos
    global elo_history
    elo_history = {p.id: [] for p in Player.objects.all()}
    elos = {p.id: 1000 for p in Player.objects.all()}
    numbers = [10, 20, 50, 100, 'all']
    context = {'players': Player.objects.all().values('name', 'id').distinct().order_by('id'), 'numbers': numbers}
    return render(request, 'polls/playerstats.html', context)


import numpy as np


def load_playerstats(request):

    # reset_all_elo()
    elo_history = elo()
    # compute_tournament(Gameplay.objects.get(id = 336).results.all())
    print_all_elo()
    p_id = request.GET.get('p_id')
    number = request.GET.get('number')
    if number == 'all':
        number = 9999
    else:
        number = int(number)
    p_name = Player.objects.filter(id=p_id).values('name')[0]['name']
    results = Results.objects.filter(p_id__id=p_id).filter(order__gte=1).values('gp_id__name__name',
                                                                                'gp_id__NumberOfPlayers', 'order',
                                                                                'points').order_by('-id')[:number]
    points = list(results.values_list('points', flat=True))[::-1]
    order = list(results.values_list('order', flat=True))[::-1]
    NoP = list(results.values_list('gp_id__NumberOfPlayers', flat=True))[::-1]
    g_name = list(results.values_list('gp_id__name__name', flat=True))[::-1]
    # cummean = [cs / n for cs, n in
    #            zip(np.cumsum([compute_score(o, n) for o, n in zip(order, NoP)]), range(1, len(results) + 1))]
    try:
        lws = max(len(list(y)) for (c, y) in itertools.groupby(order) if c == 1)
    except:
        lws = 0
    try:
        lls = max(len(list(y)) for (c, y) in itertools.groupby(([a == b for a, b in zip(order, NoP)])) if c)
    except:
        lls = 0
    try:
        lnws = max(len(list(y)) for (c, y) in itertools.groupby(([a != 1 for a in order])) if c)
    except:
        lnws = 0
    try:
        lbl = max(len(list(y)) for (c, y) in itertools.groupby(order) if c == 2)
    except:
        lbl = 0

    base = elo_history[int(p_id)]
    if base[0] < 100:
        base[0] = 1000 + base[0]
    cummean = np.cumsum(base).tolist()[-number:]

    meanelo = round(np.mean(cummean), 2)
    celo = cummean[-1]
    maxelo = max(cummean)
    minelo = min(cummean)

    print_all_elo()
    return JsonResponse(data={"p_id": p_id,
                              "p_name": p_name,
                              "g_name": g_name,
                              "order": order,
                              "points": points,
                              "NoP": NoP,
                              "cummean": cummean,
                              "lws": lws,
                              "lls": lls,
                              "lbl": lbl,
                              "lnws": lnws,
                              "meanelo": meanelo,
                              "celo": celo,
                              "maxelo": maxelo,
                              "minelo": minelo,
                              })

def update_elo_local(elos, changes):
    for key, value in changes.items():
        elos[key] = elos[key] + value
    return None

def elo():
    if any([v != 1000 for v in elos.values()]):
        return elo_history
    # elo_history = {p.id: [] for p in Player.objects.all()}
    # elos = {p.id: 1000 for p in Player.objects.all()}
    gms = Gameplay.objects.filter(with_results=True).order_by('id')
    for g in gms:
        changes = compute_tournament_local(g.results.all(), elos)
        update_elo_local(elos, changes)
        add_to_history(elo_history, changes)
    return elo_history


import itertools


def add_to_history(hist, changes):
    for key, value in changes.items():
        hist[key].append(value)
    return None


def computeW(elo1, elo2):
    return 1 / (10 ** (-(elo1 - elo2) / 400) + 1)


def computeKW(elo1, elo2, res, k=60):
    return round(k * (res - computeW(elo1, elo2)))


def compute_tournament(results):
    changes = {p.p_id.id: 0 for p in results}
    for i, j in itertools.combinations(results, 2):
        elo_change = computeKW(i.p_id.elo, j.p_id.elo,
                               (np.sign(j.order - i.order) + 1) / 2, int(60/len(results)))  # i is winner -> i is smaller
        changes[i.p_id.id] = changes[i.p_id.id] + elo_change
        changes[j.p_id.id] = changes[j.p_id.id] - elo_change
    return changes

def compute_tournament_local(results, elos):
    changes = {p.p_id.id: 0 for p in results}
    for i, j in itertools.combinations(results, 2):
        elo_change = computeKW(elos[i.p_id.id], elos[j.p_id.id],
                               (np.sign(j.order - i.order) + 1) / 2,
                               int(60 / len(results)))  # i is winner -> i is smaller
        changes[i.p_id.id] = changes[i.p_id.id] + elo_change
        changes[j.p_id.id] = changes[j.p_id.id] - elo_change
    if 17 in changes.keys():  # Automa
        changes[17] = 0
    if 33 in changes.keys():  # Guest
        changes[33] = 0
    return changes

def update_elo(changes):
    for key, value in changes.items():
        p = Player.objects.get(id=key)
        p.elo = p.elo + value
        p.save(update_fields=['elo'])
    return None


def reset_all_elo():
    for p in Player.objects.all():
        p.elo = 1000
        p.save(update_fields=['elo'])
    return None


def print_all_elo():
    total_elo = 0
    for p in Player.objects.all():
        total_elo = total_elo + p.elo
        print(p, p.elo)
    print(total_elo)
    return None
