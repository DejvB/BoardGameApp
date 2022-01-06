from django.contrib.auth.decorators import login_required
from django.forms import formset_factory
from django.http import JsonResponse
from django.db.models import Avg
from django.shortcuts import redirect, render
from polls.forms import UsedExpansionForm, GameplayForm

from ...models import Expansion, Gameplay, Results
from ..helpers import *


@login_required
def add_play(request):
    context = {}
    gp_form = GameplayForm()

    expansions = []
    expansionformset = formset_factory(
        UsedExpansionForm, extra=0
    )  # len(Expansions))
    e_formset = expansionformset(
        request.POST or None,
        initial=[
            {'e_id': expansions[i], 'gp_id': bg_id}
            for i in range(len(expansions))
        ],
    )
    if request.method == 'POST':
        gp_form = GameplayForm(request.POST)
        if (
            gp_form.is_valid() and e_formset.is_valid()
        ):  # can be and e_formset.is_valid()
            gp = gp_form.save()
            gp.save()
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
    return render(request, 'polls/add_game.html', context)


def expansions_select_options(request):
    bg_id = request.GET.get('id')
    Expansions = list(
        Expansion.objects.filter(basegame__id=bg_id)
        .order_by('name')
        .values_list('id', flat=True)
    )
    ExpansionsNames = list(
        Expansion.objects.filter(basegame__id=bg_id)
        .order_by('name')
        .values_list('name', flat=True)
    )
    Expansionformset = formset_factory(
        UsedExpansionForm, extra=0
    )  # len(Expansions))
    Gameplays = list(
        Gameplay.objects.all().order_by('name').values_list('name', flat=True)
    )
    e_formset = Expansionformset(
        request.POST or None,
        initial=[
            {'e_id': Expansions[i], 'gp_id': Gameplays[0]}
            for i in range(len(Expansions))
        ],
    )

    return render(
        request,
        'polls/expansions_select_options.html',
        {
            'e_formset': e_formset,
            'Expansions': Expansions,
            'ExpansionsNames': ExpansionsNames,
            'tex': 'haha',
        },
    )


def load_player_count(request):
    bg_id = request.GET.get('id')
    print(bg_id)
    playersRange = Boardgames.objects.filter(id=bg_id).values(
        'minNumberOfPlayers', 'maxNumberOfPlayers'
    )[0]
    minP = playersRange['minNumberOfPlayers']
    maxP = playersRange['maxNumberOfPlayers']
    PossibleNumberOfPlayers = range(minP, maxP + 1)

    return render(
        request,
        'polls/players_dropdown_options.html',
        {'PossibleNumberOfPlayers': PossibleNumberOfPlayers},
    )


def basic_stats(request):
    # basic stats for new gameplay page
    bg_id = request.GET.get('id')
    game_id = (
        Gameplay.objects.filter(name__id=bg_id)
        .values('id')
        .order_by('-id')[0]['id']
    )
    result = Results.objects.filter(gp_id__id=game_id).values(
        'p_id__name', 'points'
    )
    result = [[r['p_id__name'], r['points']] for r in result]
    queryset = (
        Results.objects.filter(gp_id__name__id=bg_id)
        .filter(gp_id__with_results=True)
        .values(
            'gp_id', 'p_id__name', 'gp_id__NumberOfPlayers', 'points', 'order'
        )
        .order_by('-points')
    )
    maxws = queryset[0]['points']
    minws = queryset.filter(order=1).order_by('points')[0]['points']
    avgws = round(
        queryset.filter(order=1).aggregate(Avg('points'))['points__avg'], 2
    )
    avgtot = round(queryset.aggregate(Avg('points'))['points__avg'], 2)
    maxnws = queryset.filter(order=2)[0]['points']

    return JsonResponse(
        data={
            'result': result,
            'maxws': maxws,
            'minws': minws,
            'avgws': avgws,
            'avgtot': avgtot,
            'maxnws': maxnws,
        }
    )


def randomizer(request):
    games = list(Boardgames.objects.all().values_list('name', flat=True))
    return JsonResponse(data={'games': games})
