import django_tables2 as tables

from polls.models import Gameplay


class GameplayTable(tables.Table):
    NumberOfPlayers = tables.Column(verbose_name='NoP')
    players = tables.Column(accessor='get_players', verbose_name='Players')

    class Meta:
        model = Gameplay
        exclude = ('time', 'ID')
