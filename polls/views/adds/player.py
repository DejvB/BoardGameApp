from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from polls.forms import PlayerForm
from polls.views.helpers import show_success_tooltip


@login_required  # type:ignore
def add_player(request: HttpRequest) -> HttpResponse:
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
