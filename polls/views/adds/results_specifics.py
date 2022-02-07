from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django import forms
from django.forms import formset_factory
from django.shortcuts import render, redirect

from polls.forms import ResultsForm, ScoringTableForm

from ...models import PlayerSpecifics, ScoringSpecifics, ScoringTable, Gameplay
from ..helpers import (
    compute_tournament,
    get_last_gameplay,
    show_success_tooltip,
    update_elo,
)

@login_required
def add_results_specifics(request):
    context = {}
    last_game = get_last_gameplay(request, only_session=False)
    used_exp = last_game.usedexpansion_set.filter(used=True).values('e_id')
    player_specifics = PlayerSpecifics.objects.filter(bg_id_id=last_game.name.id).values_list('id', 'name')
    scoring_specifics = ScoringSpecifics.objects.filter(Q(bg_id_id=last_game.name.id) |
                                                        Q(bg_id_id__in=used_exp))\
        .values_list('id', 'name')
    scoring_total = [ss for ss in scoring_specifics if ss[1] == 'Total'][0]
    scoring_specifics = [ss for ss in scoring_specifics if ss[1] != 'Total']
    scoring_specifics.append(scoring_total)
    ResultsFormSet = formset_factory(ResultsForm, extra=0)
    ScoringTableFormSet = formset_factory(ScoringTableForm, extra=0)
    if not scoring_specifics:
        return redirect('add_results')
    initials = []
    player_order = [(i, i) for i in range(last_game.NumberOfPlayers + 1)]
    for _ in range(last_game.NumberOfPlayers):
        initials.append({'gp_id': last_game, 'points': 0, 'order': 0, 'player_order': player_order[0][0]})
    result_formset = ResultsFormSet(request.POST or None,
                                    initial=initials,
                                    prefix='results')
    for result_form in result_formset:
        result_form.fields['gp_id'].widget = forms.HiddenInput()
        result_form.fields['order'].widget = forms.HiddenInput()
        result_form.fields['points'].widget = forms.HiddenInput()
        result_form.fields['player_order'].choices = player_order
        if player_specifics:
            result_form.fields['player_specifics'].choices = player_specifics
        else:
            result_form.fields.pop('player_specifics')
    initials = []
    for _ in result_formset:
        for ss in scoring_specifics:
            initials.append({'score': 0, 'ss_id': ss[0]})
    st_formset = ScoringTableFormSet(request.POST or None, initial=initials, prefix='scores')
    for i, st_form in enumerate(st_formset):
        st_form.fields['ss_id'].disabled = True
        st_form.fields['ss_id'].help_text = scoring_specifics[i % len(scoring_specifics)][1]
        st_form.fields['ss_id'].choices = scoring_specifics
        st_form.fields['result_id'].required = False
        st_form.fields['score'].widget = forms.NumberInput(attrs={'style': 'width:10ch'})
    context['st_formset'] = st_formset
    context['result_formset'] = result_formset
    context['NoSS'] = len(scoring_specifics)
    if result_formset.is_valid() and st_formset.is_valid():
        messages.success(request, 'Form submission successful')
        show_success_tooltip(context)
        points = []
        for i in range(len(result_formset)):
            points.append(sum([st_formset[context['NoSS'] * i + j].clean()['score'] for j in range(context['NoSS'])]))
        for i, result_form in enumerate(result_formset):
            r = result_form.save(commit=False)
            r.points = points[i]
            r.order = sum([r.points < point for point in points]) + 1
            r.save()
            for st_form in st_formset[context['NoSS'] * i: context['NoSS'] * (i + 1)]:
                st = st_form.save(commit=False)
                st.result_id = r
                if st.ss_id.name == 'Total':
                    st.score = points[i]
                st.save()
        if last_game.with_results:
            changes = compute_tournament(last_game.results.all())
            update_elo(changes)
        return redirect('highscores')
    return render(request, 'polls/add_results_specifics.html', context)




