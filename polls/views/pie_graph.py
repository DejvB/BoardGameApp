from django.db.models import Count
from django.shortcuts import render

from polls.models import Gameplay, Player, Results


def compute_score(o, n):
    return (n - o + 1) / n


def pie_chart(request):
    labels = []
    data = []
    colors = []
    context = {}
    players = Player.objects.order_by('name').values_list('name', flat=True)
    gp_queryset = list(Gameplay.objects.values_list('id', flat=True))

    # points
    points = []
    for player in players:
        p_sum = 0
        queryset = (
            Results.objects.filter(p_id__name=player)
            .filter(order__gte=1)
            .values('p_id__name', 'gp_id__NumberOfPlayers', 'order')
        )
        for query in queryset:
            p_sum = p_sum + compute_score(query['order'], query['gp_id__NumberOfPlayers'])
        points.append([player, round(p_sum / len(queryset), 3)])
    context['points'] = sorted(points, key=lambda x: -x[1])
    for i in range(6):
        data.append([])

        queryset = (
            Results.objects.filter(gp_id__in=gp_queryset)
            .filter(order=i + 1)
            .values('p_id__name')
            .annotate(total=Count('p_id__name'))
        )

        for player in players:
            if (
                len(Results.objects.filter(p_id__name=player).values('p_id__name')) < 10
            ):  # this is kind of stupid - I could filter players before
                continue
            p = queryset.filter(p_id__name=player)
            try:
                data[i].append(p[0]['total'])
            except IndexError:
                data[i].append(0)
            if i == 0:
                labels.append(player)
                colors.append(Player.objects.filter(name=player).values_list('color', flat=True)[0])
    context['labels'] = labels
    context['colors'] = colors
    context['data0'] = data[0]
    context['data1'] = data[1]
    context['data2'] = data[2]
    context['data3'] = data[3]
    context['data4'] = data[4]
    context['data5'] = data[5]
    return render(request, 'polls/pie_chart.html', context)
