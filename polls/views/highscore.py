import random

from django.db.models import Avg, Count
from django.http import JsonResponse
from django.shortcuts import render

from ..models import Gameplay, Player, Results
from .helpers import get_bgg_info, my_view


def highscores(request):
    if 'test' in request.session:
        print(request.session['test'])
    userid = my_view(request)
    gameplays = Gameplay.objects.all()
    if userid:
        played_list = Results.objects.filter(p_id__id=userid).values('gp_id__id')
        gameplays = gameplays.filter(id__in=played_list)
        if userid in ['6', '7']:
            played_list = Results.objects.all().values('gp_id__id')
            gameplays = Gameplay.objects.filter(id__in=played_list)
    else:
        gp_ids = random.choices(list(Gameplay.objects.all().values_list('id', flat=True)), k=3)
        gameplays = gameplays.filter(id__in=gp_ids)

    context = {
        'boardgames': gameplays.values('name__name', 'name__id').distinct().order_by('name__name'),
        'lastgame': gameplays.latest('date').name,
    }
    return render(request, 'polls/highscores.html', context)


def load_chart_data(request):
    userid = my_view(request)
    labels = []
    data = []
    colors = []
    display = []
    names = []
    position = []
    diff = []

    bg_id = request.GET.get('id')
    bg_info = get_bgg_info(bg_id)
    chk = request.GET.get('chk')
    p_colors = Player.objects.all()
    p_colors = {p_c.name: p_c.color for p_c in p_colors}

    gameplays = Gameplay.objects.filter(name__id=bg_id)
    queryset = (
        Results.objects.filter(gp_id__name__id=bg_id)
        .filter(gp_id__with_results=True)
        .values('gp_id', 'p_id__name', 'gp_id__NumberOfPlayers', 'points', 'order')
        .order_by('-points')
    )
    if userid and chk != 'true':
        played_list = Results.objects.filter(p_id__id=userid).values('gp_id__id')
        queryset = queryset.filter(gp_id__in=played_list)
        gameplays = gameplays.filter(id__in=played_list)

    for query in queryset:
        if (str(query['gp_id__NumberOfPlayers'])) in labels:
            display.append(False)
        else:
            display.append(True)
        data.append([query['points']])
        # colors.append(c[query['p_id__name']])
        colors.append(p_colors[query['p_id__name']])
        labels.append(str(query['gp_id__NumberOfPlayers']))
        names.append(query['p_id__name'])
        position.append(query['order'])

    maxws = queryset[0]['points']
    minws = queryset.filter(order=1).order_by('points')[0]['points']
    avgws = round(queryset.filter(order=1).aggregate(Avg('points'))['points__avg'], 2)
    avgtot = round(queryset.aggregate(Avg('points'))['points__avg'], 2)
    try:
        maxnws = queryset.filter(order=2)[0]['points']
    except IndexError:
        maxnws = 0
    queryset_gp = gameplays.values('time')
    longest_gp = str(queryset_gp.order_by('-time')[0]['time'])
    sg = str(queryset_gp.order_by('time')[0]['time'])
    avgg = str(queryset_gp.aggregate(Avg('time'))['time__avg'])

    gp_id_queryset = list(gameplays.values_list('id', flat=True))
    for gp_id in gp_id_queryset:
        q = queryset.filter(gp_id=gp_id)
        try:
            diff.append(q.filter(order=1)[0]['points'] - q.filter(order=2)[0]['points'])
        except IndexError:
            diff = [0]
    avgmp = round(sum(diff) / len(diff), 2)
    uw = (
        queryset.filter(order=1)
        .values('p_id__name')
        .annotate(Count('p_id__name'))
        .order_by('-p_id__name__count')[0]['p_id__name']
    )
    avgp = []
    pp = sorted(list(gameplays.values('NumberOfPlayers').distinct().values_list('NumberOfPlayers', flat=True)))
    for i in pp:
        avgp.append(
            list(
                queryset.filter(gp_id__NumberOfPlayers=i)
                .values('p_id__name', 'gp_id__NumberOfPlayers')
                .annotate(Avg('points'))
                .order_by('-points__avg')
                .values_list('p_id__name', 'points__avg')
            )
        )
    gp_list = list(gameplays.order_by('date').values_list('date', flat=True))
    first_gp = gp_list[0].date()
    last_gp = gp_list[-1].date()
    nogp = len(gp_list)

    order_data = []
    for p in Player.objects.all():
        player_exists = False
        count = 0
        p_order = [{'x': 0, 'y': 'Nan'}]
        p_points = [{'x': 0, 'y': 'Nan'}]
        for ids in list(queryset.values('gp_id').order_by('gp_id').distinct().values_list('gp_id', flat=True)):
            count += 1
            order = queryset.filter(p_id__name=p).filter(gp_id=ids).values('order')
            points = queryset.filter(p_id__name=p).filter(gp_id=ids).values('points')
            if order:
                for o, pl in zip(order, points):
                    # print(o)
                    p_order.append({'x': count, 'y': o['order']})
                    p_points.append({'x': count, 'y': pl['points']})

                # p_order.append({'x': count, 'y': order[0]['order']})
                # p_points.append({'x': count, 'y': points[0]['points']})
                player_exists = True
            else:
                p_order.append({'x': count, 'y': 'Nan'})
                p_points.append({'x': count, 'y': 'Nan'})
        p_order.append({'x': count + 1, 'y': 'Nan'})
        p_points.append({'x': count + 1, 'y': 'Nan'})
        if player_exists:
            order_data.append([p.name, p.color, p_order, p_points])

    return JsonResponse(
        data={
            'labels': labels,
            'data': data,
            'colors': colors,
            'display': display,
            'names': names,
            'position': position,
            'maxws': maxws,
            'minws': minws,
            'avgws': avgws,
            'avgtot': avgtot,
            'maxnws': maxnws,
            'longest_gp': longest_gp,
            'sg': sg,
            'avgg': avgg,
            'avgmp': avgmp,
            'uw': uw,
            'pp': pp,
            'avgp': avgp,
            'first_gp': first_gp,
            'last_gp': last_gp,
            'nogp': nogp,
            'order_data': order_data,
            'bg_img': bg_info['img_link'],
            'bg_rank': bg_info['rank'],
            'bg_weight': bg_info['weight'],
        }
    )
