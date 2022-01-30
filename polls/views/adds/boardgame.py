from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render

from polls.forms import BoardgameForm
from polls.models import Boardgames, OwnBoardgame
from polls.views.helpers import scrape_bgg_info, search_for_bgg_id, show_success_tooltip, update_bg_info


@login_required  # type:ignore
def add_boardgame(request: HttpRequest) -> HttpResponse:
    context = {}
    form = BoardgameForm()
    context['form'] = form
    if request.method == 'POST':  # and 'run_script' in request.POST:
        search_query = request.POST['bg_name']
        _, bgg_ids = search_for_bgg_id(search_query)
        bgg_infos = []
        for bgg_id in bgg_ids:
            bgg_info = scrape_bgg_info(bgg_id)
            if bgg_info['type'] == 'boardgame':
                bgg_infos.append(bgg_info)
        context['bgg_infos'] = bgg_infos  # type: ignore
        request.session['bgg_infos'] = bgg_infos
    return render(request, 'polls/add_boardgame.html', context)


def bg_submit(request: HttpRequest) -> JsonResponse:
    print('You duck!')
    bgg_info = request.session['bgg_infos'][int(request.GET.get('bg_ind'))]
    bg, created = Boardgames.objects.get_or_create(
        name=bgg_info['name'],
        minNumberOfPlayers=int(bgg_info['minp']),
        maxNumberOfPlayers=int(bgg_info['maxp']),
        bgg_id=int(bgg_info['id']),
    )
    update_bg_info(bg.id, bgg_info)
    print(created, request.GET.get('own'))
    if created and request.GET.get('own') == 'true':
        OwnBoardgame.objects.create(p_id=request.user.player, bg_id=bg)
    return JsonResponse(data={'created': created})


@login_required  # type:ignore
def add_boardgame_old(request: HttpRequest) -> HttpResponse:
    context = {}
    form = BoardgameForm()
    context['form'] = form
    if request.method == 'POST':  # and 'run_script' in request.POST:
        form = BoardgameForm(request.POST)
        if form.is_valid():
            b = form.save()
            b.save()
            show_success_tooltip(context)
        return render(request, 'polls/add_boardgame_old.html', context)
    return render(request, 'polls/add_boardgame_old.html', context)
