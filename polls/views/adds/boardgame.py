from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from polls.forms import BoardgameForm


@login_required
def add_boardgame(request):
    context = {}
    form = BoardgameForm()
    if request.method == 'POST':  # and 'run_script' in request.POST:
        form = BoardgameForm(request.POST)
        if form.is_valid():
            b = form.save()
            b.save()
        return redirect('home')
    context['form'] = form
    return render(request, 'polls/add_boardgame.html', context)
