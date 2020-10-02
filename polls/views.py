from django.shortcuts import render, redirect
# from django.template import loader

# from .models import *
from .forms import *

from django.db.models import Count, Sum, Q

def index(request):
    latest_games_list = Gameplay.objects.order_by('-date')[:5]
    best_companion = Results.objects.filter(~Q(p_id__name='David')).values('p_id__name').annotate(Sum('gp_id__time'), Count('gp_id__time')).order_by('-gp_id__time__sum')
    mostplayed_games_list = Gameplay.objects.values('name__name').annotate(game_count=Count('name__name')).order_by('-game_count')[:5]
    context = {'latest_games_list': latest_games_list,
               'mostplayed_games_list': mostplayed_games_list,
               'best_companion': best_companion
               }
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
    form = GameplayForm()
    if request.method == 'POST':
        form = GameplayForm(request.POST)
        if form.is_valid():
            gp = form.save()
            gp.save()
        return redirect('add_results')
    context['form'] = form
    context['boardgame'] = Boardgames.objects.all()
    # context['players'] = range(1,7)
    return render(request, 'polls/add_game.html', context)

def load_player_count(request):
    bg_id = request.GET.get('name')
    playersRange = Boardgames.objects.filter(id=bg_id).values('minNumberOfPlayers','maxNumberOfPlayers')[0]
    minP = playersRange['minNumberOfPlayers']
    maxP = playersRange['maxNumberOfPlayers']
    PossibleNumberOfPlayers = range(minP, maxP + 1)
    return render(request, 'polls/players_dropdown_options.html', {'PossibleNumberOfPlayers':PossibleNumberOfPlayers})

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

def add_results(request):
    # if 'player_count' in request.session:
    #     print(request.session['player_count'])
    lastGame = Gameplay.objects.order_by('-id')[0]
    ResultsFormSet = formset_factory(ResultsForm, extra=0)
    formset = ResultsFormSet(request.POST or None, initial=[{'order': i+1, 'gp_id':lastGame} for i in range(lastGame.NumberOfPlayers)])
    if formset.is_valid():
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
    c = {'Adam':'#FFB6C1','David':'#ADD8E6','Bára':'#90EE90','Anička':'#FFFF66', 'Jana':'#ffcccb'}
    for i in range(4):
        data.append([])
        queryset = Results.objects.filter(order=i + 1).values('p_id__name').annotate(total=Count('p_id__name'))

        for player in players:
            p = queryset.filter(p_id__name=player)
            try:
                data[i].append(p[0]['total'])
            except:
                data[i].append(0)
            if i == 0:
                labels.append(player)
                colors.append(c[player])
    context['labels'] = labels
    context['colors'] = colors
    context['data0'] = data[0]
    context['data1'] = data[1]
    context['data2'] = data[2]
    context['data3'] = data[3]
    return render(request, 'polls/pie_chart.html', context)

def highscores(request):
    context = {'boardgames': Boardgames.objects.all().order_by('name')}

    datas = ['1','2','3']
    colors = ['#FFB6C1','#ADD8E6','#90EE90','#ffcccb''#FFFF66']
    labels = ['a','b','v']
    # minP = playersRange['minNumberOfPlayers']
    # maxP = playersRange['maxNumberOfPlayers']
    # PossibleNumberOfPlayers = range(minP, maxP + 1)

    context['labels'] = labels
    context['colors'] = colors
    context['data'] = datas
    return render(request, 'polls/highscores.html', context)

from django.http import JsonResponse

def load_chart_data(request):
    labels = []
    data = []
    colors = []
    c = {'Adam':'#FFB6C1','David':'#ADD8E6','Bára':'#90EE90','Anička':'#FFFF66', 'Jana':'#ffcccb'}

    bg_id = request.GET.get('name')
    p_count = request.GET.get('NoP')
    print(bg_id, p_count)
    queryset = Results.objects.filter(gp_id__name__id=bg_id).filter(gp_id__NumberOfPlayers=p_count).values('p_id__name','points','order').order_by('-points')
    print(queryset)
    for query in queryset:
        data.append([query['points']])
        colors.append(c[query['p_id__name']])
        labels.append(query['p_id__name'])
    try:
        return JsonResponse(data={'labels': labels,'data': data, 'colors':colors})
    except:
        return JsonResponse(data={'labels': ['a','b','v'], 'data': ['1','5','3'],
    'colors': ['#FFB6C1','#ADD8E6','#90EE90','#ffcccb''#FFFF66']})
