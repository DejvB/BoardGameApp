from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from polls.forms import ExpansionForm

from ..helpers import show_success_tooltip


@login_required
def add_expansion(request):
    context = {}
    form = ExpansionForm()
    context['form'] = form
    if request.method == 'POST':
        form = ExpansionForm(request.POST)
        if form.is_valid():
            e = form.save()
            e.save()
            show_success_tooltip(context)
            return render(request, 'polls/add_expansion.html', context)
    return render(request, 'polls/add_expansion.html', context)
