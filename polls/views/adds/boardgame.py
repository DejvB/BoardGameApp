from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from polls.forms import BoardgameForm

from ..helpers import show_success_tooltip


@login_required
def add_boardgame(request):
    context = {}
    form = BoardgameForm()
    context['form'] = form
    if request.method == 'POST':  # and 'run_script' in request.POST:
        form = BoardgameForm(request.POST)
        if form.is_valid():
            b = form.save()
            b.save()
            show_success_tooltip(context)
        return render(request, 'polls/add_boardgame.html', context)
    return render(request, 'polls/add_boardgame.html', context)
