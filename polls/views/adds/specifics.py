from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render

from polls.forms import PlayerSpecificsForm, ScoringSpecificsForm

from ...models import Boardgames, OwnBoardgame
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
        print(request.POST)
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
    return render(request, 'polls/add_specifics.html', context)
