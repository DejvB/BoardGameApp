from django.shortcuts import render, redirect
# from django.template import loader

# from .models import *
from .forms import *

from django.db.models import Count, Sum, Q, Avg, Max, Min, F, ExpressionWrapper, fields, Value, DateTimeField
from django.db.models.functions import ExtractWeek, ExtractWeekDay
from math import ceil


def index(request):
    latest_games_list = Gameplay.objects.order_by('-date')[:5]
    best_companion = Results.objects.filter(~Q(p_id__name='Davi')).values('p_id__name').annotate(Sum('gp_id__time'), Count('gp_id__time')).order_by('-gp_id__time__sum')[:5]
    games_list = Gameplay.objects.values('name__name').annotate(game_count=Count('name__name')).annotate(game_time=Sum('time'))
    mostplayed_games_list = games_list.order_by('-game_count')[:5]
    leastplayed_games_list = games_list.order_by('game_count')[:5]
    time_list = games_list.order_by('-game_time')[:5]
    games_list = Gameplay.objects.values('name__name', 'date').annotate(game_count=Count('name__name'))
    long_time_no_see_games_list = games_list.values('name__name')\
                                    .annotate(id__max=Max('id'),today=Value(datetime.datetime.now(), DateTimeField()))\
                                    .order_by('id__max')[:5]
    context = {'latest_games_list': latest_games_list,
               'mostplayed_games_list': mostplayed_games_list,
               'leastplayed_games_list': leastplayed_games_list,
               'mosttimeplayed_games_list': time_list,
               'long_time_no_see_games_list': long_time_no_see_games_list,
               'best_companion': best_companion
               }
    week = []
    totalTime = []
    totalTimestr = []
    totalCount = []
    stats = Gameplay.objects.annotate(week=ExtractWeek('date')).values('week').annotate(Sum('time'), Count('time'))
    for stat in stats:
        week.append(stat['week'])
        totalTime.append(stat['time__sum'].seconds * 1000)
        totalTimestr.append(str(stat['time__sum']))
        totalCount.append(stat['time__count'])

    # avg time per game
    avg = int(sum(totalTime) / sum(totalCount))
    # max number of game equivalent to avg time per game
    mg = ceil(max(totalTime)/(sum(totalTime) / sum(totalCount)))
    mg = max(mg, max(totalCount))
# time equivalent to mg with avg time per game
    mt = mg * avg
    context['week'] = week
    context['totalTime'] = totalTime
    context['totalTimestr'] = totalTimestr
    context['totalCount'] =  totalCount
    context['mg'] = mg
    context['mt'] = mt

    weekday = list(Gameplay.objects.annotate(weekday=ExtractWeekDay('date')).values('weekday').annotate(Count('time')).values_list('time__count', flat=True))
    weekday = weekday[1:] + [weekday[0]]
    context['weekday'] = weekday
    return render(request, 'polls/index.html', context)


def add_boardgame(request):
    context = {}
    form = BoardgameForm()
    if request.method == 'POST': # and 'run_script' in request.POST:
        form = BoardgameForm(request.POST)
        if form.is_valid():
            b = form.save()
            b.save()
        return redirect('home')
    context['form'] = form
    return render(request, 'polls/add_boardgame.html', context)




def add_play(request):
    context = {}
    gp_form = GameplayForm()

    Expansions = []
    Expansionformset = formset_factory(UsedExpansionForm, extra=0) # len(Expansions))
    e_formset = Expansionformset(request.POST or None,
                                 initial=[{'e_id': Expansions[i], 'gp_id': bg_id} for i in range(len(Expansions))])
    if request.method == 'POST':
        gp_form = GameplayForm(request.POST)
        if gp_form.is_valid() and e_formset.is_valid(): # can be and e_formset.is_valid()
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
            return redirect('add_results')
    context['gp_form'] = gp_form
    context['e_formset'] = e_formset
    context['boardgame'] = Boardgames.objects.all()
    # context['players'] = range(1,7)
    return render(request, 'polls/add_game.html', context)


def expansions_select_options(request):
    bg_id = request.GET.get('name')
    Expansions = list(Expansion.objects.filter(basegame__id=bg_id).order_by('name').values_list('id', flat=True))
    ExpansionsNames = list(Expansion.objects.filter(basegame__id=bg_id).order_by('name').values_list('name', flat=True))
    Expansionformset = formset_factory(UsedExpansionForm, extra=0) # len(Expansions))
    Gameplays = list(Gameplay.objects.all().order_by('name').values_list('name', flat=True))
    e_formset = Expansionformset(request.POST or None,
                                 initial=[{'e_id': Expansions[i], 'gp_id': Gameplays[0]} for i in range(len(Expansions))])

    return render(request, 'polls/expansions_select_options.html', {'e_formset':e_formset,
                                                                    'Expansions':Expansions,
                                                                    'ExpansionsNames':ExpansionsNames, 'tex':'haha'})

def load_player_count(request):
    bg_id = request.GET.get('name')
    playersRange = Boardgames.objects.filter(id=bg_id).values('minNumberOfPlayers','maxNumberOfPlayers')[0]
    minP = playersRange['minNumberOfPlayers']
    maxP = playersRange['maxNumberOfPlayers']
    PossibleNumberOfPlayers = range(minP, maxP + 1)
    return render(request, 'polls/players_dropdown_options.html', {'PossibleNumberOfPlayers':PossibleNumberOfPlayers})

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
    return render(request, 'polls/add_expansion.html',context)

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
    return render(request, 'polls/add_player.html',context)

from django.forms import formset_factory
from django.contrib import messages

def add_results(request):
    # if 'player_count' in request.session:
    #     print(request.session['player_count'])
    lastGame = Gameplay.objects.order_by('-id')[0]
    ResultsFormSet = formset_factory(ResultsForm, extra=0)
    formset = ResultsFormSet(request.POST or None, initial=[{'order': i+1, 'gp_id':lastGame} for i in range(max(2, lastGame.NumberOfPlayers))])
    if formset.is_valid():
        messages.success(request, 'Form submission successful')
        for form in formset:
            r = form.save()
            r.save()
        return redirect('home')
    return render(request, 'polls/add_results.html', {'formset':formset})


def pie_chart(request):
    labels = []
    data = []
    colors = []
    context = {}
    players = Player.objects.order_by('name').values_list('name', flat=True)

    # for gameplayes with three of us
    if True:
        queryset = Results.objects.values('gp_id', 'p_id__name',
                                          'gp_id__NumberOfPlayers', 'points',
                                          'order').order_by('-points')
        gp_queryset = list(Gameplay.objects.values_list('id', flat=True))
        gp_queryset_forloop = gp_queryset.copy()
        for gp in gp_queryset_forloop:
            for n in ['David', 'Bára', 'Adam']:
                if not queryset.filter(gp_id=gp).filter(p_id__name=n):
                    gp_queryset.remove(gp)
                    break
    else:
        gp_queryset = list(Gameplay.objects.values_list('id', flat=True))


    for i in range(4):
        data.append([])
        # queryset = Results.objects.filter(order=i + 1).values('p_id__name').annotate(total=Count('p_id__name'))


        queryset = Results.objects.filter(gp_id__in=gp_queryset).filter(order=i + 1).values('p_id__name').annotate(total=Count('p_id__name'))

        for player in players:
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
    return render(request, 'polls/pie_chart.html', context)

def highscores(request):
    context = {'boardgames': Gameplay.objects.all().values('name__name').distinct().order_by('name__name')}
    context['lastgame'] = Gameplay.objects.latest('date').name

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
    queryset = Results.objects.filter(gp_id__name__name=bg_name).values('gp_id','p_id__name','gp_id__NumberOfPlayers','points','order').order_by('-points')
    if chk == 'true':
        gp_queryset = list(Gameplay.objects.filter(name__name=bg_name).values_list('id', flat=True))
        gp_queryset_forloop = gp_queryset.copy()
        for gp in gp_queryset_forloop:
            for n in ['David','Bára','Adam']:
                if not queryset.filter(gp_id=gp).filter(p_id__name=n):
                    gp_queryset.remove(gp)
                    break
        queryset = Results.objects.filter(gp_id__in=gp_queryset).values('p_id__name', 'gp_id__NumberOfPlayers',
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
    avgws = round(queryset.filter(order=1).aggregate(Avg('points'))['points__avg'],2)
    avgtot = round(queryset.aggregate(Avg('points'))['points__avg'],2)
    maxnws = queryset.filter(order=2)[0]['points']

    queryset_gp = Gameplay.objects.filter(name__name=bg_name).values('time')
    lg = str(queryset_gp.order_by('-time')[0]['time'])
    sg = str(queryset_gp.order_by('time')[0]['time'])
    avgg = str(queryset_gp.aggregate(Avg('time'))['time__avg'])

    gp_id_queryset = list(Gameplay.objects.filter(name__name=bg_name).values_list('id', flat=True))
    for gp_id in gp_id_queryset:
        q = queryset.filter(gp_id=gp_id)
        diff.append(q.filter(order=1)[0]['points'] - q.filter(order=2)[0]['points'])
    avgmp = round(sum(diff) / len(diff),2)
    uw = queryset.filter(order=1).values('p_id__name').annotate(Count('p_id__name')).order_by('-p_id__name__count')[0]['p_id__name']
    return JsonResponse(data={'labels': labels,
                              'data': data,
                              'colors':colors,
                              'display': display,
                              'names': names,
                              'position':position,
                              'maxws':maxws,
                              'minws':minws,
                              'avgws':avgws,
                              'avgtot':avgtot,
                              'maxnws':maxnws,
                              'lg':lg,
                              'sg':sg,
                              'avgg':avgg,
                              'avgmp':avgmp,
                              'uw':uw})

def history(request):
    context = {}
    context['games'] = GameplayTable(Gameplay.objects.all())
    return render(request, 'polls/history.html', context)

from .tables import GameplayTable

def get_history(request):
    fromdate = request.GET.get('from')
    todate = request.GET.get('to')
    games = GameplayTable(Gameplay.objects.filter(date__range=[fromdate, todate]))
    return render(request, "polls/get_history.html", {"games": games})
