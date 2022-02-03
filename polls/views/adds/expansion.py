from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render

from polls.forms import BoardgameForm

from ...models import Boardgames, OwnBoardgame
from ..helpers import (
    scrape_bgg_info,
    search_for_exp_id,
    show_success_tooltip,
    update_bg_info,
)


@login_required
def add_expansion(request):
    context = {}
    boardgames = Boardgames.objects.filter(standalone=True).order_by('name')
    context['boardgames'] = boardgames
    context['selected'] = boardgames[0].bgg_id
    if request.method == 'POST':  # and 'run_script' in request.POST:
        bgg_id = request.POST['bg_name']
        context['selected'] = int(bgg_id)
        _, bgg_ids = search_for_exp_id(bgg_id)
        bgg_infos = []
        for bgg_id in bgg_ids:
            bgg_info = scrape_bgg_info(bgg_id)
            if bgg_info['type'] == 'boardgameexpansion':
                bgg_infos.append(bgg_info)
        context['bgg_infos'] = bgg_infos
        request.session['bgg_infos'] = bgg_infos
    return render(request, 'polls/add_expansion.html', context)


def exp_submit(request):
    bgg_info = request.session['bgg_infos'][int(request.GET.get('bg_ind'))]
    bg, created = Boardgames.objects.get_or_create(
        name=bgg_info['name'],
        minNumberOfPlayers=int(bgg_info['minp']),
        maxNumberOfPlayers=int(bgg_info['maxp']),
        bgg_id=int(bgg_info['id']),
    )
    bg.standalone = False
    bg.basegame.add(Boardgames.objects.get(bgg_id=request.GET.get('basegame')))
    bg.save()
    update_bg_info(bg.id, bgg_info)
    added = False
    if request.GET.get('own') == 'true':
        _, added = OwnBoardgame.objects\
                               .get_or_create(p_id=request.user.player,
                                              bg_id=bg)

    return JsonResponse(data={'created': created,
                              'added': added,
                              'own': request.GET.get('own') == 'true'})


@login_required
def add_expansion_old(request):
    context = {}
    form = BoardgameForm()
    context['form'] = form
    if request.method == 'POST':  # and 'run_script' in request.POST:
        form = BoardgameForm(request.POST)
        if form.is_valid():
            b = form.save()
            b.standalone = False
            b.save()
            show_success_tooltip(context)
        return render(request, 'polls/add_expansion_old.html', context)
    return render(request, 'polls/add_expansion_old.html', context)