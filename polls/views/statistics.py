import itertools

import numpy as np
from django.http import JsonResponse
from django.shortcuts import render

from ..models import Gameplay, Player, Results
from .helpers import computeKW, my_view


elos = {}
elo_history = {}


def playerstats(request):
    global elos
    global elo_history
    elo_history = {p.id: [] for p in Player.objects.all()}
    elos = {p.id: 1000 for p in Player.objects.all()}
    numbers = [10, 20, 50, 100, 'all']
    context = {
        'players': Player.objects.all().values('name', 'id').distinct().order_by('name'),
        'players_elo': Player.objects.all().values('name', 'elo').distinct().order_by('-elo'),
        'numbers': numbers,
    }
    return render(request, 'polls/playerstats.html', context)


def load_playerstats(request):
    userid = my_view(request)
    # reset_all_elo()
    elo_history = elo()
    set_elo(elo_history)
    # compute_tournament(Gameplay.objects.get(id = 336).results.all())
    # print_all_elo()
    p_id = request.GET.get('p_id')
    number = request.GET.get('number')
    if number == 'all':
        number = 9999
    else:
        number = int(number)
    if not userid:  # only five games for not logged user
        number = 5
    p_name = Player.objects.filter(id=p_id).values('name')[0]['name']
    results = (
        Results.objects.filter(p_id__id=p_id)
        .filter(order__gte=1)
        .values(
            'gp_id__name__name',
            'gp_id__NumberOfPlayers',
            'order',
            'gp_id__date',
        )
        .order_by('-gp_id__date')[:number]
    )
    date = list(results.values_list('gp_id__date', flat=True))[::-1]
    order = list(results.values_list('order', flat=True))[::-1]
    NoP = list(results.values_list('gp_id__NumberOfPlayers', flat=True))[::-1]
    g_name = list(results.values_list('gp_id__name__name', flat=True))[::-1]
    try:
        lws = max(len(list(y)) for (c, y) in itertools.groupby(order) if c == 1)
    except ValueError:
        lws = 0
    try:
        lls = max(len(list(y)) for (c, y) in itertools.groupby(([a == b for a, b in zip(order, NoP)])) if c)
    except ValueError:
        lls = 0
    try:
        lnws = max(len(list(y)) for (c, y) in itertools.groupby(([a != 1 for a in order])) if c)
    except ValueError:
        lnws = 0
    try:
        lbl = max(len(list(y)) for (c, y) in itertools.groupby(order) if c == 2)
    except ValueError:
        lbl = 0

    base = elo_history[int(p_id)]
    if base[0] < 100:
        base[0] = 1000 + base[0]
    cummean = np.cumsum(base).tolist()[-number:]

    meanelo = round(np.mean(cummean), 2)
    celo = cummean[-1]
    maxelo = max(cummean)
    minelo = min(cummean)

    # print_all_elo()
    return JsonResponse(
        data={
            'p_id': p_id,
            'p_name': p_name,
            'g_name': g_name,
            'order': order,
            'date': date,
            'NoP': NoP,
            'cummean': cummean,
            'lws': lws,
            'lls': lls,
            'lbl': lbl,
            'lnws': lnws,
            'meanelo': meanelo,
            'celo': celo,
            'maxelo': maxelo,
            'minelo': minelo,
        }
    )


def update_elo_local(elos, changes):
    for key, value in changes.items():
        elos[key] = elos[key] + value
    return None


def elo():
    if any([v != 1000 for v in elos.values()]):
        return elo_history
    # elo_history = {p.id: [] for p in Player.objects.all()}
    # elos = {p.id: 1000 for p in Player.objects.all()}
    gms = Gameplay.objects.filter(with_results=True).order_by('date')
    for g in gms:
        changes = compute_tournament_local(g.results.all(), elos)
        update_elo_local(elos, changes)
        add_to_history(elo_history, changes)
    return elo_history


def add_to_history(hist, changes):
    for key, value in changes.items():
        hist[key].append(value)
    return None


def compute_tournament_local(results, elos):
    changes = {p.p_id.id: 0 for p in results}
    for i, j in itertools.combinations(results, 2):
        elo_change = computeKW(
            elos[i.p_id.id],
            elos[j.p_id.id],
            (np.sign(j.order - i.order) + 1) / 2,
            int(60 / len(results)),
        )  # i is winner -> i is smaller
        changes[i.p_id.id] = changes[i.p_id.id] + elo_change
        changes[j.p_id.id] = changes[j.p_id.id] - elo_change
    if 17 in changes.keys():  # Automa
        changes[17] = 0
    if 33 in changes.keys():  # Guest
        changes[33] = 0
    return changes


def set_elo(elo):
    for key, value in elo.items():
        p = Player.objects.get(id=key)
        if value[0] < 100:
            value[0] += 1000
        if sum(value) != p.elo:
            p.elo = sum(value)
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
