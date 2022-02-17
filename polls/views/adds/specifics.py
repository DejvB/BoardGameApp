from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render

from polls.forms import GameplaysWithPossibleScoringResultsForm, PlayerSpecificsForm, ScoringSpecificsForm

from ...models import Gameplay, Results, ScoringSpecifics, PlayerSpecifics
from ..helpers import my_view, show_success_tooltip


@login_required
def add_specifics(request):
    userid = my_view(request)
    context = {}
    ss_form = ScoringSpecificsForm(prefix='ss')
    ps_form = PlayerSpecificsForm(prefix='ps')
    gp_form = GameplaysWithPossibleScoringResultsForm(prefix='gp')
    context['ss_form'] = ss_form
    context['ps_form'] = ps_form

    ss_list = ScoringSpecifics.objects.all().values('bg_id', 'bg_id__name').order_by('bg_id__name').distinct()
    ps_list = PlayerSpecifics.objects.all().values('bg_id', 'bg_id__name').order_by('bg_id__name').distinct()
    context['ss_list'] = ss_list
    context['ps_list'] = ps_list

    gp_ids = Results.objects.filter(p_id=userid).values_list('gp_id', flat=True)
    bg_ids_with_ss = [bg['bg_id'] for bg in ss_list]
    gameplay_list = Gameplay.objects\
                            .filter(id__in=gp_ids, name__id__in=bg_ids_with_ss)\
                            .order_by('id')\
                            .values('id', 'name__id', 'name__name')
    for a in gameplay_list:
        a['res'] = Gameplay.objects.get(id=a['id']).get_players_w_results()
    context['gp_list'] = gameplay_list
    gp_form.fields['gameplays'].choices = [[a['id'], f"{a['name__name']}: {a['res']}"] for a in gameplay_list]
    context['gp_form'] = gp_form

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
        elif 'gp_submit' in request.POST:
            gp_form = GameplaysWithPossibleScoringResultsForm(request.POST, prefix='gp')
            gp_form.fields['gameplays'].choices = [[a['id'], f"{a['name__name']}: {a['res']}"] for a in gameplay_list]
            print(gp_form)
            if gp_form.is_valid():
                print('haha')
                gp = gp_form.cleaned_data
                print(gp)
                request.session['gameplay_id'] = gp.get('gameplays')
                return redirect('add_results_specifics')
    return render(request, 'polls/add_specifics.html', context)


def specifics_list(request):
    bg_id = request.GET.get('bg_id')
    if request.GET.get('el_id') == 'ss_id':
        spec_list = ScoringSpecifics.objects.filter(bg_id__id=bg_id).values_list('name', flat=True)
    else:
        spec_list = PlayerSpecifics.objects.filter(bg_id__id=bg_id).values_list('name', flat=True)
    return JsonResponse(data={'spec_list': list(spec_list)})


def add_results_specifics_to_existing_game(request):
    request.session['gameplay_id'] = request.GET.get('gp_id')
    return
