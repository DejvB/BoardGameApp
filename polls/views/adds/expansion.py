from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from polls.forms import ExpansionForm


@login_required
def add_expansion(request):
    context = {}
    form = ExpansionForm()
    if request.method == 'POST':
        form = ExpansionForm(request.POST)
        if form.is_valid():
            e = form.save()
            e.save()
            return redirect('home')
    context['form'] = form
    return render(request, 'polls/add_expansion.html', context)
