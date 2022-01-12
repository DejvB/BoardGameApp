import itertools
from xml.etree import ElementTree as ET

import numpy as np
import requests

from ..models import Boardgames, Gameplay, Player


def my_view(request):
    userid = None
    if request.user.is_authenticated:
        userid = request.user.player.id
        if 'fake_id' in request.session:
            userid = request.session['fake_id']
    return userid


def get_bgg_info(bg_id):
    api_prefix = 'https://www.boardgamegeek.com/xmlapi2/'
    bg_info = {}
    bgg_id = Boardgames.objects.get(id=bg_id).bgg_id
    if bgg_id == 1 or bgg_id == '1':
        bgg_id = update_bgg_id(bg_id)
    xml_root = ET.fromstring(
        requests.get(f'{api_prefix}thing?id={bgg_id}&stats=1').text
    )
    bg_info['img'] = xml_root.find('item//thumbnail').text
    bg_info['id'] = xml_root.find('item').attrib['id']
    rank = xml_root.find('item//statistics//ratings//average').attrib['value']
    bg_info['rank'] = f'{float(rank):.2f}'
    weight = xml_root.find('item//statistics//ratings//averageweight').attrib[
        'value'
    ]
    bg_info['weight'] = f'{float(weight):.2f}'
    links = xml_root.findall("item//link[@type='boardgamecategory']")
    bg_info['category'] = [l.attrib['value'] for l in links]
    mechanics = xml_root.findall("item//link[@type='boardgamemechanic']")
    bg_info['mechanics'] = [m.attrib['value'] for m in mechanics]
    mechanics = xml_root.findall("item//link[@type='boardgamedesigner']")
    bg_info['designer'] = [m.attrib['value'] for m in mechanics]
    # print(bg_info)
    return bg_info


def update_bgg_id(bg_id):
    api_prefix = 'https://www.boardgamegeek.com/xmlapi2/'
    bg_name = Boardgames.objects.get(id=bg_id).name
    xml_root = ET.fromstring(
        requests.get(
            f'{api_prefix}search?query={bg_name}&type=boardgame&exact=1'
        ).text
    )
    if xml_root.find('item'):
        bgg_id = xml_root.find('item').attrib['id']
        if bgg_id:
            bg = Boardgames.objects.get(id=bg_id)
            bg.bgg_id = bgg_id
            bg.save(update_fields=['bgg_id'])
            return bgg_id
    else:
        return 2


def update_elo(changes):
    for key, value in changes.items():
        p = Player.objects.get(id=key)
        p.elo = p.elo + value
        p.save(update_fields=['elo'])
    return None


def computeW(elo1, elo2):
    return 1 / (10 ** (-(elo1 - elo2) / 400) + 1)


def computeKW(elo1, elo2, res, k=60):
    return round(k * (res - computeW(elo1, elo2)))


def compute_tournament(results):
    changes = {p.p_id.id: 0 for p in results}
    for i, j in itertools.combinations(results, 2):
        elo_change = computeKW(
            i.p_id.elo,
            j.p_id.elo,
            (np.sign(j.order - i.order) + 1) / 2,
            int(60 / len(results)),
        )  # i is winner -> i is smaller
        changes[i.p_id.id] = changes[i.p_id.id] + elo_change
        changes[j.p_id.id] = changes[j.p_id.id] - elo_change
    return changes


# def update_session(request):
#     if not request.is_ajax() or not request.method == 'POST':
#         return HttpResponseNotAllowed(['POST',])
#
#     request.session['fake_name'] = request.GET.get('fake_name')
#     return HttpResponse('ok')


def get_last_gameplay(request, only_session):
    if 'gameplay_id' in request.session:
        gp_id = request.session['gameplay_id']
        last_game = Gameplay.objects.get(id=gp_id)
    elif not only_session:
        last_game = Gameplay.objects.latest('id')
    else:
        last_game = Gameplay.objects.none()
    return last_game
