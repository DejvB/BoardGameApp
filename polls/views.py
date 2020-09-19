from django.shortcuts import render
# from django.template import loader

# from .models import *
from .forms import *


from django.urls import reverse_lazy


def index(request):
    latest_games_list = Boardgames.objects.order_by('lastTimePlayed')[:5]
    mostplayed_games_list = Boardgames.objects.order_by('-totalTime')[:5]
    context = {'latest_games_list': latest_games_list,
               'mostplayed_games_list': mostplayed_games_list
               }
    return render(request, 'polls/index.html', context)


def add_boardgame(request):
    context = {}
    model = Boardgames
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
    model = Boardgames
    form = GameplayForm()
    if request.method == 'POST': # and 'run_script' in request.POST:
        form = GameplayForm(request.POST)
        if form.is_valid():
            b = form.save()
            b.save()
        return render(request, 'polls/index.html')
    context['form'] = form
    context['boardgame'] = Boardgames.objects.all()

    boardgame_id = request.GET.get('name')
    minP = Boardgames.objects.filter(name=boardgame_id).only('minNumberOfPlayers')
    maxP = Boardgames.objects.filter(name=boardgame_id).only('maxNumberOfPlayers')
    context['players'] = [minP,maxP]
    return render(request, 'polls/add_game.html', context)

# def last_played_games(request):
#     latest_games_list = Boardgames.objects.order_by('-lastTimePlayed')[:5]
#     context = {'latest_games_list': latest_games_list}
#     return render(request, 'polls/index.html', context)


# def load_boardgames(request):
#     context = {}
#     boardgame_id = request.GET.get('name')
#     minP = Boardgames.objects.filter(name=boardgame_id).minNumberOfPlayers
#     maxP = Boardgames.objects.filter(name=boardgame_id).maxNumberOfPlayers
#     context['players'] = ['1','2']
#     return render(request, 'polls/add_game.html', context)

# def last_played_games(request):
#     latest_games_list = Boardgames.objects.order_by('-lastTimePlayed')[:5]
#     template = loader.get_template('polls/index.html')
#     context = {'latest_games_list': latest_games_list,
#     }
#     return HttpResponse(template.render(context, request))

# def detail(request, question_id):
#     return HttpResponse("You're looking at question %s." % question_id)
#
# def results(request, question_id):
#     response = "You're looking at the results of question %s."
#     return HttpResponse(response % question_id)
#
# def vote(request, question_id):
#     return HttpResponse("You're voting on question %s." % question_id)
