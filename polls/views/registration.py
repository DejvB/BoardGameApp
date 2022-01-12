from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from polls.forms import NewUserForm


@login_required
def register_request(request):
    if request.method == 'POST':
        form = NewUserForm(request.POST)
        if form.is_valid():
            # user = form.save()
            # login(request, user)
            messages.success(request, 'Registration successful.')
            return redirect('home')
        messages.error(
            request, 'Unsuccessful registration. Invalid information.'
        )
    form = NewUserForm()
    return render(
        request=request,
        template_name='polls/register.html',
        context={'register_form': form},
    )
