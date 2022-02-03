from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render

from polls.forms import BoardgameForm

from ...models import Boardgames, OwnBoardgame
from ..helpers import (
    scrape_bgg_info,
    search_for_bgg_id,
    show_success_tooltip,
    update_bg_info,
)


@login_required
def add_boardgame(request):
    context = {}
    if request.method == 'POST':  # and 'run_script' in request.POST:
        search_query = request.POST['bg_name']
        _, bgg_ids = search_for_bgg_id(search_query)
        bgg_infos = []
        for bgg_id in bgg_ids:
            bgg_info = scrape_bgg_info(bgg_id)
            if bgg_info['type'] == 'boardgame':
                bgg_infos.append(bgg_info)
        context['bgg_infos'] = bgg_infos
        request.session['bgg_infos'] = bgg_infos
    return render(request, 'polls/add_boardgame.html', context)


def bg_submit(request):
    bgg_info = request.session['bgg_infos'][int(request.GET.get('bg_ind'))]
    bg, created = Boardgames.objects.get_or_create(
        name=bgg_info['name'],
        minNumberOfPlayers=int(bgg_info['minp']),
        maxNumberOfPlayers=int(bgg_info['maxp']),
        bgg_id=int(bgg_info['id']),
    )
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
def add_boardgame_old(request):
    context = {}
    form = BoardgameForm()
    context['form'] = form
    if request.method == 'POST':  # and 'run_script' in request.POST:
        form = BoardgameForm(request.POST)
        if form.is_valid():
            b = form.save()
            b.standalone = True
            b.save()
            show_success_tooltip(context)
        return render(request, 'polls/add_boardgame_old.html', context)
    return render(request, 'polls/add_boardgame_old.html', context)
