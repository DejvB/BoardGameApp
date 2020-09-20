from django.shortcuts import render
# from django.template import loader

# from .models import *
from .forms import *

from django.db.models import Count


def index(request):
    latest_games_list = Gameplay.objects.order_by('-date')[:5]
    mostplayed_games_list = Gameplay.objects.values('name__name').annotate(game_count=Count('name__name')).order_by('-game_count')[:5]
    context = {'latest_games_list': latest_games_list,
               'mostplayed_games_list': mostplayed_games_list
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
        return render(request, 'polls/index.html')
    context['form'] = form
    return render(request, 'polls/add_boardgame.html', context)




def add_play(request):
    context = {}
    form = GameplayForm()
    if request.method == 'POST': # and 'run_script' in request.POST:
        form = GameplayForm(request.POST)
        if form.is_valid():
            gp = form.save()
            gp.save()
        # print(form.cleaned_data['name'])
        context['player_count'] = form.cleaned_data['NumberOfPlayers']
        return render(request, 'polls/add_results.html', context)
    context['form'] = form
    context['boardgame'] = Boardgames.objects.all()
    # boardgame_id = form.cleaned_data['boardgame_name']
    # print(boardgame_id)
    # minP = Boardgames.objects.filter(name=boardgame_id).only('minNumberOfPlayers')
    # maxP = Boardgames.objects.filter(name=boardgame_id).only('maxNumberOfPlayers')
    context['players'] = [1,2,3]
    return render(request, 'polls/add_game.html', context)

def add_player(request):
    if request.method == 'POST':
        form = PlayerForm(request.POST)
        if form.is_valid():
            p = form.save()
            p.save()
        return render(request, 'polls/index.html')
    return render(request, 'polls/add_player.html')

from django.forms import formset_factory

def add_results(request):

    print(request)
    lastGame = Gameplay.objects.order_by('-id')[0]
    print(lastGame)
    ResultsFormSet = formset_factory(ResultsForm, extra=0)
    formset = ResultsFormSet(request.POST or None, initial=[{'order': i+1, 'gp_id':lastGame} for i in range(lastGame.NumberOfPlayers)])
    # formset = ResultsFormSet(request.POST or None, initial=[{'order':1}])
    # formset = ResultsFormSet()
    if formset.is_valid():
        for form in formset:
            print(form.cleaned_data)

    # if request.method == 'POST':
    #     if formset.is_valid():
    #         for form in formset:
    #             form.save()
    #         return render(request, 'polls/add_results.html')
    return render(request, 'polls/add_results.html', {'formset':formset})
