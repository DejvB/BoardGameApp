from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from polls.forms import PlayerForm

from ..helpers import show_success_tooltip


@login_required
def add_player(request):
    context = {}
    form = PlayerForm()
    context['form'] = form
    if request.method == 'POST':
        form = PlayerForm(request.POST)
        if form.is_valid():
            p = form.save()
            p.save()
            show_success_tooltip(context)
        return render(request, 'polls/add_player.html', context)
    return render(request, 'polls/add_player.html', context)
