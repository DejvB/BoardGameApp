from datetime import datetime, timedelta
from typing import List

from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.forms import formset_factory
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render

from polls.forms import GameplayForm, UsedExpansionForm
from polls.models import Boardgames, Expansion, Gameplay, Results
from polls.views.helpers import get_last_gameplay


def get_time_length(req: HttpRequest) -> int:
    return sum(int(req.POST[f'{i}']) for i in range(8) if f'{i}' in req.POST)


def get_nearest_to_5(minutes: int) -> int:
    if minutes % 5 == 0:
        return 0
    elif minutes % 5 == 1:
        return -1
    elif minutes % 5 == 2:
        return -2
    elif minutes % 5 == 3:
        return 2
    else:
        return 1


def get_now() -> str:
    d = datetime.now()
    d = d + timedelta(minutes=get_nearest_to_5(d.minute))
    return d.strftime('%Y-%m-%dT%H:%M')


@login_required  # type:ignore
def add_play(request: HttpRequest) -> HttpResponse:
    last_game = get_last_gameplay(request, only_session=True)
    if last_game and not last_game.results.all():
        return redirect('add_results')
    context = {}
    gp_form = GameplayForm(request.POST or None, initial={'date': get_now()})
    expansions: List[str] = []
    expansionformset = formset_factory(UsedExpansionForm, extra=0)
    e_formset = expansionformset(
        request.POST or None,
        initial=[{'e_id': expansions[i], 'gp_id': 0} for i in range(len(expansions))],
    )
    if request.method == 'POST':
        gp_form = GameplayForm(request.POST)
        minutes = get_time_length(request)
        if gp_form.is_valid() and e_formset.is_valid():
            gp = gp_form.save(commit=False)
            gp.time = timedelta(minutes=minutes)
            gp.save()
            for e_form in e_formset:
                e = e_form.save()
                e.gp_id = gp
                e.save()
            request.session['gameplay_id'] = gp.id
            if gp.with_results:
                return redirect('add_results')
            else:
                return redirect('add_results')
    context['gp_form'] = gp_form
    context['e_formset'] = e_formset
    context['boardgame'] = Boardgames.objects.all()
    return render(request, 'polls/add_game.html', context)


def expansions_select_options(request: HttpRequest) -> HttpResponse:
    bg_id = request.GET.get('id')
    expansions = list(Expansion.objects.filter(basegame__id=bg_id).order_by('name').values_list('id', flat=True))
    expansion_names = list(Expansion.objects.filter(basegame__id=bg_id).order_by('name').values_list('name', flat=True))
    expansion_formset = formset_factory(UsedExpansionForm, extra=0)  # len(Expansions))
    gameplays = list(Gameplay.objects.all().order_by('name').values_list('name', flat=True))
    e_formset = expansion_formset(
        request.POST or None,
        initial=[{'e_id': expansions[i], 'gp_id': gameplays[0]} for i in range(len(expansions))],
    )

    return render(
        request,
        'polls/expansions_select_options.html',
        {
            'e_formset': e_formset,
            'Expansions': expansions,
            'ExpansionsNames': expansion_names,
            'tex': 'haha',
        },
    )


def load_player_count(request: HttpRequest) -> HttpResponse:
    bg_id = request.GET.get('id')
    players_range = Boardgames.objects.filter(id=bg_id).values('minNumberOfPlayers', 'maxNumberOfPlayers')[0]
    min_p = players_range['minNumberOfPlayers']
    max_p = players_range['maxNumberOfPlayers']
    possible_number_of_players = range(min_p, max_p + 1)

    return render(
        request,
        'polls/players_dropdown_options.html',
        {'PossibleNumberOfPlayers': possible_number_of_players},
    )


def basic_stats(request: HttpRequest) -> JsonResponse:
    # basic stats for new gameplay page
    bg_id = request.GET.get('id')
    game_id = Gameplay.objects.filter(name__id=bg_id).values('id').order_by('-id')[0]['id']
    result = Results.objects.filter(gp_id__id=game_id).values('p_id__name', 'points')
    result = [[r['p_id__name'], r['points']] for r in result]
    queryset = (
        Results.objects.filter(gp_id__name__id=bg_id)
        .filter(gp_id__with_results=True)
        .values('gp_id', 'p_id__name', 'gp_id__NumberOfPlayers', 'points', 'order')
        .order_by('-points')
    )
    maxws = queryset[0]['points']
    minws = queryset.filter(order=1).order_by('points')[0]['points']
    avgws = round(queryset.filter(order=1).aggregate(Avg('points'))['points__avg'], 2)
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


def randomizer(request: HttpRequest) -> JsonResponse:
    games = list(Boardgames.objects.all().values_list('name', flat=True))
    return JsonResponse(data={'games': games})
