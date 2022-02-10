from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render

from polls.forms import PlayerSpecificsForm, ScoringSpecificsForm

from ...models import Boardgames, OwnBoardgame, ScoringSpecifics, PlayerSpecifics
from ..helpers import (
    scrape_bgg_info,
    search_for_bgg_id,
    show_success_tooltip,
    update_bg_info,
)


@login_required
def add_specifics(request):
    context = {}
    ss_form = ScoringSpecificsForm(prefix='ss')
    ps_form = PlayerSpecificsForm(prefix='ps')
    context['ss_form'] = ss_form
    context['ps_form'] = ps_form
    if request.method == 'POST':  # and 'run_script' in request.POST:
        if 'ss_submit' in request.POST:
            ss_form = ScoringSpecificsForm(request.POST, prefix='ss')
            if ss_form.is_valid():
                ss = ss_form.save()
                ss.save()
                show_success_tooltip(context, 'tooltip_ss')
        elif 'ps_submit' in request.POST:
            ps_form = PlayerSpecificsForm(request.POST, prefix='ps')
            if ps_form.is_valid():
                ps = ps_form.save()
                ps.save()
                show_success_tooltip(context, 'tooltip_ps')

    ss_list = ScoringSpecifics.objects.all().values('bg_id', 'bg_id__name').distinct()
    ps_list = PlayerSpecifics.objects.all().values('bg_id', 'bg_id__name').distinct()
    context['ss_list'] = ss_list
    context['ps_list'] = ps_list
    return render(request, 'polls/add_specifics.html', context)


def specifics_list(request):
    bg_id = request.GET.get('bg_id')
    if request.GET.get('el_id') == 'ss_id':
        spec_list = ScoringSpecifics.objects.filter(bg_id__id=bg_id).values_list('name', flat=True)
    else:
        spec_list = PlayerSpecifics.objects.filter(bg_id__id=bg_id).values_list('name', flat=True)
    return JsonResponse(data={'spec_list': list(spec_list)})
