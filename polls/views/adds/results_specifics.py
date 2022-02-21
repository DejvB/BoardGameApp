from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django import forms
from django.forms import formset_factory
from django.shortcuts import render, redirect

from polls.forms import ResultsForm, ScoringTableForm

from ...models import PlayerSpecifics, ScoringSpecifics, Results
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
    er = Results.objects.filter(gp_id=last_game)
    used_exp = last_game.usedexpansion_set.filter(used=True).values('e_id')
    player_specifics = PlayerSpecifics.objects.filter(bg_id_id=last_game.name.id).values_list('id', 'name')
    scoring_specifics = ScoringSpecifics.objects.filter(Q(bg_id_id=last_game.name.id) |
                                                        Q(bg_id_id__in=used_exp))\
        .values_list('id', 'name')
    if not scoring_specifics:
        return redirect('add_results')
    scoring_total = [ss for ss in scoring_specifics if ss[1] == 'Total'][0]
    scoring_specifics = [ss for ss in scoring_specifics if ss[1] != 'Total']
    scoring_specifics.append(scoring_total)
    ResultsFormSet = formset_factory(ResultsForm, extra=0)
    ScoringTableFormSet = formset_factory(ScoringTableForm, extra=0)
    initials = []
    player_order = [(i, i) for i in range(last_game.NumberOfPlayers + 1)]
    for i in range(last_game.NumberOfPlayers):
        if er:
            initials.append({'gp_id': last_game,
                             'points': er[i].points,
                             'order': er[i].order,
                             'player_order': er[i].player_order,
                             'p_id': er[i].p_id,
                             'player_specifics': er[i].player_specifics})
        else:
            initials.append({'gp_id': last_game,
                             'points': 0,
                             'order': 0,
                             'player_order': player_order[0][0]})
    result_formset = ResultsFormSet(request.POST or None,
                                    initial=initials,
                                    prefix='results')
    for result_form in result_formset:
        result_form.fields['gp_id'].widget = forms.HiddenInput()
        result_form.fields['points'].widget = forms.HiddenInput()
        result_form.fields['player_order'].choices = player_order
        result_form.fields['order'].choices = player_order
        if player_specifics:
            result_form.fields['player_specifics'].choices = player_specifics
        else:
            result_form.fields.pop('player_specifics')
    initials = []
    for i, _ in enumerate(result_formset):
        for ss in scoring_specifics:
            if ss[1] == 'Total' and er:
                initials.append({'score': er[i].points, 'ss_id': ss[0]})
            else:
                initials.append({'score': 0, 'ss_id': ss[0]})
    st_formset = ScoringTableFormSet(request.POST or None, initial=initials, prefix='scores')
    for i, st_form in enumerate(st_formset):
        st_form.fields['ss_id'].disabled = True
        st_form.fields['ss_id'].help_text = scoring_specifics[i % len(scoring_specifics)][1]
        st_form.fields['ss_id'].choices = scoring_specifics
        st_form.fields['result_id'].required = False
    context['st_formset'] = st_formset
    context['result_formset'] = result_formset
    context['player_specifics'] = player_specifics
    context['NoSS'] = len(scoring_specifics)
    if result_formset.is_valid() and st_formset.is_valid():
        messages.success(request, 'Form submission successful')
        show_success_tooltip(context)
        points = []
        for i in range(len(result_formset)):
            NoSS = context['NoSS']
            points.append(get_sum_without_total(st_formset, NoSS, i))
        for i, result_form in enumerate(result_formset):
            r, created = Results.objects.get_or_create(**result_form.cleaned_data)
            if created:
                r.points = points[i]
                r.order = sum([r.points < point for point in points]) + 1
                r.save()
            for st_form in st_formset[context['NoSS'] * i: context['NoSS'] * (i + 1)]:
                st = st_form.save(commit=False)
                st.result_id = r
                if st.ss_id.name == 'Total' and st.score == 0:
                    st.score = points[i]
                st.save()
        if last_game.with_results:
            changes = compute_tournament(last_game.results.all())
            update_elo(changes)
        return redirect('highscores')
    return render(request, 'polls/add_results_specifics.html', context)


def get_sum_without_total(fs, NoSS, i):
    total_temp = 0
    total_test = 0
    for j in range(NoSS):
        if fs[NoSS * i + j].clean()['ss_id'].name != 'Total':
            print(fs[NoSS * i + j].clean()['ss_id'].name)
            total_temp += fs[NoSS * i + j].clean()['score']
        else:
            total_test = fs[NoSS * i + j].clean()['score']
    if total_temp != total_test:
        print('Check failed!')
    return total_temp


