from operator import itemgetter

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render

from ..models import Player

from .helpers import my_view, get_bgg_info


@login_required
def gamebrary(request, sort_key='name'):
    context = {}
    if 'HTTP_REFERER' in request.META and request.META.get('HTTP_REFERER').split('/')[-2] == sort_key:
        request.session['reverse'] = not request.session['reverse']
    else:
        request.session['reverse'] = False
    if 'bgg_infos' in request.session:
        gamebrary = request.session['bgg_infos']
        context['gamebrary'] = gamebrary
        request.session['bgg_infos'] = sorted(gamebrary, key=itemgetter(sort_key), reverse=request.session['reverse'])
    else:
        userid = my_view(request)
        bg_owned_list = Player.objects.get(id=userid).get_owned(userid)
        gamebrary = []
        for bg_id in bg_owned_list:
            gamebrary.append(get_bgg_info(bg_id))
        gamebrary = sorted(gamebrary, key=itemgetter(sort_key))
        context = {'gamebrary': gamebrary}
        request.session['bgg_infos'] = gamebrary
    return render(request, 'polls/gamebrary.html', context)
