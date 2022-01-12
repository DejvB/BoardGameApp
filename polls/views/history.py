from django.shortcuts import render

from ..models import Gameplay
from ..tables import GameplayTable


def history(request):
    context = {}
    context['games'] = GameplayTable(Gameplay.objects.all().order_by('-date'))
    return render(request, 'polls/history.html', context)


def get_history(request):
    fromdate = request.GET.get('from')
    todate = request.GET.get('to')
    games = GameplayTable(
        Gameplay.objects.filter(date__range=[fromdate, todate])
    )
    return render(request, 'polls/get_history.html', {'games': games})
