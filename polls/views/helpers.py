import itertools
import time
from typing import Any, Collection, Dict, List, Optional, Tuple
from xml.etree import ElementTree

import numpy as np
import requests
from django.http import HttpRequest

from polls.models import Boardgames, Category, Designer, Gameplay, Mechanics, Player


def my_view(request: HttpRequest) -> Optional[int]:
    userid = None
    if request.user.is_authenticated:
        userid = request.user.player.id
        if 'fake_id' in request.session:
            userid = request.session['fake_id']
    return userid


def scrape_bgg_info(bgg_id: int) -> Dict[str, Any]:
    api_prefix = 'https://www.boardgamegeek.com/xmlapi2/'
    bg_info = {}
    req = requests.get(f'{api_prefix}thing?id={bgg_id}&stats=1')
    t = 1
    while req.status_code == 429 and t < 60:
        t *= 2
        time.sleep(t)
        req = requests.get(f'{api_prefix}thing?id={bgg_id}&stats=1')
    xml_root = ElementTree.fromstring(req.text)
    bg_info['name'] = xml_root.find('item//name').attrib['value']  # type: ignore
    bg_info['type'] = xml_root.find('item').attrib['type']  # type: ignore
    try:
        bg_info['img_link'] = xml_root.find('item//thumbnail').text  # type: ignore
    except AttributeError:
        bg_info['img_link'] = ''
    bg_info['minp'] = xml_root.find('item//minplayers').attrib['value']  # type: ignore
    bg_info['maxp'] = xml_root.find('item//maxplayers').attrib['value']  # type: ignore
    bg_info['minage'] = xml_root.find('item//minage').attrib['value']  # type: ignore
    bg_info['playtime'] = xml_root.find('item//playingtime').attrib['value']  # type: ignore
    bg_info['minplaytime'] = xml_root.find('item//minplaytime').attrib['value']  # type: ignore
    bg_info['maxplaytime'] = xml_root.find('item//maxplaytime').attrib['value']  # type: ignore
    bg_info['year'] = xml_root.find('item//yearpublished').attrib['value']  # type: ignore

    bg_info['id'] = xml_root.find('item').attrib['id']  # type: ignore
    rank = xml_root.find('item//statistics//ratings//average').attrib['value']  # type: ignore
    bg_info['rank'] = f'{float(rank):.2f}'
    weight = xml_root.find('item//statistics//ratings//averageweight').attrib['value']  # type: ignore
    bg_info['weight'] = f'{float(weight):.2f}'
    links = xml_root.findall("item//link[@type='boardgamecategory']")
    bg_info['category'] = [link.attrib['value'] for link in links]
    mechanics = xml_root.findall("item//link[@type='boardgamemechanic']")
    bg_info['mechanics'] = [m.attrib['value'] for m in mechanics]
    mechanics = xml_root.findall("item//link[@type='boardgamedesigner']")
    bg_info['designer'] = [m.attrib['value'] for m in mechanics]
    return bg_info


def get_bgg_info(bg_id: int) -> Dict[str, Any]:
    bgg_id = Boardgames.objects.get(id=bg_id).bgg_id
    if bgg_id == 1 or bgg_id == '1':
        bgg_id = update_bgg_id(bg_id)
    if Boardgames.objects.get(id=bg_id).weight != 0:
        return Boardgames.objects.get(id=bg_id).to_dict()  # type: ignore
    bg_info = scrape_bgg_info(bgg_id)
    update_bg_info(bg_id, bg_info)
    return bg_info


def get_bg_cmd(bg_id: int) -> Dict[str, Any]:
    bg_info = {}
    if Boardgames.objects.get(id=bg_id).weight != 0:
        bg_info['category'] = Boardgames.objects.get(id=bg_id).category.all()
        bg_info['mechanics'] = Boardgames.objects.get(id=bg_id).mechanics.all()
        bg_info['designer'] = Boardgames.objects.get(id=bg_id).designer.all()
        return bg_info
    return get_bgg_info(bg_id)


def update_bg_info(bg_id: int, bg_info: Dict[str, Any]) -> None:
    bg = Boardgames.objects.get(id=bg_id)
    # bg.name = bg_info['name']
    bg.min_number_of_players = bg_info['minp']
    bg.max_number_of_players = bg_info['maxp']
    bg.minage = bg_info['minage']
    bg.minplaytime = bg_info['minplaytime']
    bg.maxplaytime = bg_info['maxplaytime']
    bg.year = bg_info['year']
    bg.weight = bg_info['weight']
    bg.rank = bg_info['rank']
    bg.img_link = bg_info['img_link']
    bg.save()
    for category in bg_info['category']:
        cat, _ = Category.objects.get_or_create(name=category)
        cat.boardgame.add(bg_id)
    for mechanic in bg_info['mechanics']:
        mech, _ = Mechanics.objects.get_or_create(name=mechanic)
        mech.boardgame.add(bg_id)
    for designer in bg_info['designer']:
        des, _ = Designer.objects.get_or_create(name=designer)
        des.boardgame.add(bg_id)


def search_for_bgg_id(search_query: str) -> Tuple[List[str], List[int]]:
    api_prefix = 'https://www.boardgamegeek.com/xmlapi2/'
    xml_root = ElementTree.fromstring(requests.get(f'{api_prefix}search?query={search_query}&type=boardgame').text)
    neg_xml_root = ElementTree.fromstring(
        requests.get(f'{api_prefix}search?query={search_query}&type=boardgameexpansion').text
    )
    search_results = xml_root.findall('item')
    neg_search_results = neg_xml_root.findall('item')
    t_bgg_names = [bgg.find('name').attrib['value'] for bgg in search_results]  # type: ignore
    t_bgg_ids = [bgg.attrib['id'] for bgg in search_results]
    exp_ids = [bgg.attrib['id'] for bgg in neg_search_results]
    bgg_names, bgg_ids = [], []
    for name, nid in zip(t_bgg_names, t_bgg_ids):
        if nid not in exp_ids:
            bgg_names.append(name)
            bgg_ids.append(nid)
    return bgg_names, bgg_ids  # type: ignore


def update_bgg_id(bg_id: int) -> Optional[int]:  # type: ignore
    api_prefix = 'https://www.boardgamegeek.com/xmlapi2/'
    bg_name = Boardgames.objects.get(id=bg_id).name
    xml_root = ElementTree.fromstring(requests.get(f'{api_prefix}search?query={bg_name}&type=boardgame&exact=1').text)
    if xml_root.find('item'):
        bgg_id = xml_root.find('item').attrib['id']  # type: ignore
        if bgg_id:
            bg = Boardgames.objects.get(id=bg_id)
            bg.bgg_id = bgg_id
            bg.save(update_fields=['bgg_id'])
            return bgg_id  # type: ignore
    else:
        return 2


def update_elo(changes: Dict[int, int]) -> None:
    for key, value in changes.items():
        p = Player.objects.get(id=key)
        p.elo = p.elo + value
        p.save(update_fields=['elo'])
    return None


def compute_w(elo1: int, elo2: int) -> float:
    return 1 / (10 ** (-(elo1 - elo2) / 400) + 1)


def compute_kw(elo1: int, elo2: int, res: int, k: int = 60) -> int:
    return round(k * (res - compute_w(elo1, elo2)))


def compute_tournament(results: Collection[Any]) -> Dict[int, int]:
    changes = {p.p_id.id: 0 for p in results}
    for i, j in itertools.combinations(results, 2):
        elo_change = compute_kw(
            i.p_id.elo,
            j.p_id.elo,
            (np.sign(j.order - i.order) + 1) / 2,
            int(60 / len(results)),
        )  # i is winner -> i is smaller
        changes[i.p_id.id] = changes[i.p_id.id] + elo_change
        changes[j.p_id.id] = changes[j.p_id.id] - elo_change
    return changes


# def update_session(request: HttpRequest) -> HttpResponse:
#     if not request.is_ajax() or not request.method == 'POST':
#         return HttpResponseNotAllowed(['POST',])
#
#     request.session['fake_name'] = request.GET.get('fake_name')
#     return HttpResponse('ok')


def get_last_gameplay(request: HttpRequest, only_session: bool) -> Any:
    if 'gameplay_id' in request.session:
        gp_id = request.session['gameplay_id']
        last_game = Gameplay.objects.get(id=gp_id)
    elif not only_session:
        last_game = Gameplay.objects.latest('id')
    else:
        last_game = Gameplay.objects.none()
    return last_game


def show_success_tooltip(context: Dict[str, Any], tooltip: str = 'tooltip') -> Dict[str, Any]:
    context.update({tooltip: 'Submit was successful.'})
    return context
