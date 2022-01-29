from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.forms import formset_factory
from django.shortcuts import render

from polls.forms import ResultsForm

from ...models import PlayerSpecifics
from ..helpers import compute_tournament, get_last_gameplay, show_success_tooltip, update_elo


@login_required
def add_results(request):
    context = {}
    last_game = get_last_gameplay(request, only_session=False)
    specifics = PlayerSpecifics.objects.filter(bg_id_id=last_game.name.id).values_list('id', 'name')
    player_order = [(i, i) for i in range(last_game.NumberOfPlayers + 1)]
    print(player_order)
    results_formset = formset_factory(ResultsForm, extra=0)
    if last_game.with_results:
        formset = results_formset(
            request.POST or None,
            initial=[{'order': i + 1, 'gp_id': last_game} for i in range(max(2, last_game.NumberOfPlayers))],
        )

        for form in formset:
            form.fields['player_order'].choices = player_order
            if specifics:
                form.fields['player_specifics'].choices = specifics
            else:
                form.fields.pop('player_specifics')
    else:
        formset = results_formset(
            request.POST or None,
            initial=[{'order': 0, 'gp_id': last_game} for _ in range(max(2, last_game.NumberOfPlayers))],
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
