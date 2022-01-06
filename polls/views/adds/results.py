from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.forms import formset_factory
from django.shortcuts import redirect, render
from polls.forms import ResultsForm

from ...models import Gameplay
from ..helpers import update_elo, compute_tournament


@login_required
def add_results(request):
    lastGame = Gameplay.objects.order_by('-id')[0]
    ResultsFormSet = formset_factory(ResultsForm, extra=0)
    if lastGame.with_results:
        formset = ResultsFormSet(
            request.POST or None,
            initial=[
                {'order': i + 1, 'gp_id': lastGame}
                for i in range(max(2, lastGame.NumberOfPlayers))
            ],
        )
    else:
        formset = ResultsFormSet(
            request.POST or None,
            initial=[
                {'order': 0, 'gp_id': lastGame}
                for _ in range(max(2, lastGame.NumberOfPlayers))
            ],
        )
    if formset.is_valid():
        messages.success(request, 'Form submission successful')
        for form in formset:
            r = form.save()
            r.save()
        if lastGame.with_results:
            changes = compute_tournament(lastGame.results.all())
            update_elo(changes)
            print(changes)
        return redirect('home')
    return render(request, 'polls/add_results.html', {'formset': formset})
