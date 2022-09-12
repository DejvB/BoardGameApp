from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.forms import formset_factory
from django.shortcuts import render, redirect

from polls.forms import ResultsForm

from ...models import Player, PlayerSpecifics
from ..helpers import (
    compute_tournament,
    get_last_gameplay,
    my_view,
    show_success_tooltip,
    update_elo,
)


@login_required
def add_results(request):
    userid = my_view(request)
    context = {}
    last_game = get_last_gameplay(request, only_session=False)
    specifics = PlayerSpecifics.objects.filter(
        bg_id_id=last_game.name.id
    ).values_list('id', 'name')
    player_order = [(i, i) for i in range(last_game.NumberOfPlayers + 1)]
    player_recent_choices = [(q.id, q.name) for q in Player.objects.get(id=userid).get_recent_comrades(id=userid)]
    player_all_choices = [(q.id, q.name) for q in Player.objects.all().order_by('name')]
    player_choices = [('-', '------')] + player_recent_choices + [('-', '------')] + player_all_choices
    ResultsFormSet = formset_factory(ResultsForm, extra=0)
    if last_game.with_results:
        formset = ResultsFormSet(
            request.POST or None,
            initial=[
                {'order': player_order[i + 1][0], 'gp_id': last_game}
                for i in range(last_game.NumberOfPlayers)
            ],
        )

    else:
        formset = ResultsFormSet(
            request.POST or None,
            initial=[
                {'order': player_order[0][0], 'gp_id': last_game}
                for i in range(last_game.NumberOfPlayers)
            ],
        )

    for form in formset:
        form.fields['gp_id'].disabled = True
        form.fields['p_id'].choices = player_choices
        form.fields['player_order'].choices = player_order
        form.fields['order'].choices = player_order
        if specifics:
            form.fields['player_specifics'].choices = specifics
        else:
            form.fields.pop('player_specifics')
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
        return redirect('highscores')
    return render(request, 'polls/add_results.html', context)

