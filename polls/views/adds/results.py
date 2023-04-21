from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.forms import formset_factory, inlineformset_factory
from django.shortcuts import render, redirect

from polls.forms import ResultsForm

from ...models import Gameplay, Player, PlayerSpecifics, Results
from ..helpers import (
    compute_tournament,
    get_last_gameplay,
    my_view,
    show_success_tooltip,
    update_elo,
)


@login_required
def add_results(request, gp_id=None):
    userid = my_view(request)
    context = {}
    gameplay = get_last_gameplay(request, only_session=False)
    used_exp = gameplay.usedexpansion_set.filter(used=True).values('e_id')
    specifics = PlayerSpecifics.objects.filter(Q(bg_id_id=gameplay.name.id) |
                                                        Q(bg_id_id__in=used_exp))\
                                        .values_list('id', 'name')
    player_order = [(i, i) for i in range(gameplay.NumberOfPlayers + 1)]
    player_recent_choices = [(q.id, q.name) for q in Player.objects.get(id=userid).get_recent_comrades(id=userid)]
    player_friends = [(q.id, q.name) for q in Player.objects.filter(friend__id=userid).order_by('name')]
    player_all_choices = [(q.id, q.name) for q in Player.objects.all().order_by('name')]
    sep = [('-', '------')]
    player_choices = sep + player_recent_choices + sep + player_friends + sep + player_all_choices
    if gp_id:
        gameplay = Gameplay.objects.get(id=gp_id)
        extra = max(gameplay.NumberOfPlayers - gameplay.get_player_count(), 0)
        ResultsFormSet = inlineformset_factory(Gameplay, Results, extra=extra, exclude=())
        context['gp_id'] = gp_id
        formset = ResultsFormSet(request.POST or None, request.FILES or None, instance=gameplay)
    else:
        ResultsFormSet = formset_factory(ResultsForm, extra=0)
        if gameplay.with_results:
            initial = [
                    {'order': player_order[i + 1][0], 'gp_id': gameplay}
                    for i in range(gameplay.NumberOfPlayers)
                ]
        else:
            initial = [
                    {'order': player_order[0][0], 'gp_id': gameplay}
                    for i in range(gameplay.NumberOfPlayers)
                ]
        formset = ResultsFormSet(
            request.POST or None,
            initial=initial,
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
    context['bg_name'] = gameplay.name.name
    if formset.is_valid():
        messages.success(request, 'Form submission successful')
        for form in formset:
            r = form.save(commit=False)
            r.save()
        if formset.deleted_forms:
            for form in formset.deleted_forms:
                r = form.save(commit=False)
                r.delete()
            gameplay.NumberOfPlayers = max(gameplay.NumberOfPlayers - len(formset.deleted_forms), 1)
            gameplay.save(update_fields=['NumberOfPlayers'])
        show_success_tooltip(context)
        if gameplay.with_results:
            changes = compute_tournament(gameplay.results.all())
            update_elo(changes)
        return redirect('highscores')
    return render(request, 'polls/add_results.html', context)

