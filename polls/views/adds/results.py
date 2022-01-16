from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.forms import formset_factory
from django.shortcuts import render

from polls.forms import ResultsForm

from ..helpers import (
    compute_tournament,
    get_last_gameplay,
    show_success_tooltip,
    update_elo,
)


@login_required
def add_results(request):
    context = {}
    last_game = get_last_gameplay(request, only_session=False)
    ResultsFormSet = formset_factory(ResultsForm, extra=0)
    if last_game.with_results:
        formset = ResultsFormSet(
            request.POST or None,
            initial=[
                {'order': i + 1, 'gp_id': last_game}
                for i in range(max(2, last_game.NumberOfPlayers))
            ],
        )
    else:
        formset = ResultsFormSet(
            request.POST or None,
            initial=[
                {'order': 0, 'gp_id': last_game}
                for _ in range(max(2, last_game.NumberOfPlayers))
            ],
        )
    context['formset'] = formset
    if formset.is_valid():
        messages.success(request, 'Form submission successful')
        for form in formset:
            r = form.save()
            r.save()
            show_success_tooltip(context)
        if last_game.with_results:
            changes = compute_tournament(last_game.results.all())
            update_elo(changes)
        return render(request, 'polls/add_results.html', context)
    return render(request, 'polls/add_results.html', context)
