from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from polls.forms import PlayerForm


@login_required
def add_player(request):
    context = {}
    form = PlayerForm()
    if request.method == 'POST':
        form = PlayerForm(request.POST)
        if form.is_valid():
            p = form.save()
            p.save()
        return redirect('home')
    context['form'] = form
    return render(request, 'polls/add_player.html', context)
