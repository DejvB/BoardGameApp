import django_tables2 as tables

from .models import Gameplay


class GameplayTable(tables.Table):
    NumberOfPlayers = tables.Column(verbose_name='NoP')
    players = tables.Column(accessor='get_players', verbose_name='Players')

    class Meta:
        model = Gameplay
        exclude = (
            'ID',
        )
        row_attrs = {
            # "data-id": lambda record: record.pk
            "onClick": lambda record: "document.location.href='/polls/add_results/{0}';".format(record.id)
        }