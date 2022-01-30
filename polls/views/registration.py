from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from polls.forms import NewUserForm


@login_required  # type: ignore
def register_request(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()  # noqa: F841
            # login(request, user)
            messages.success(request, 'Registration successful.')
            return redirect('home')
        messages.error(request, 'Unsuccessful registration. Invalid information.')
    form = NewUserForm()
    return render(
        request=request,
        template_name='polls/register.html',
        context={'register_form': form},
    )
