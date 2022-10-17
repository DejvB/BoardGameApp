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
            "onClick": lambda record: f"document.location.href='/polls/{'edit_results_specifics' if record.name.has_scoring_category() else 'add_results'}/{record.id}';",  # NOQA
        }