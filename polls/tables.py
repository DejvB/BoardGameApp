import django_tables2 as tables

from .models import Gameplay


class GameplayTable(tables.Table):
    class Meta:
        model = Gameplay
        exclude = (
            'time',
            'ID',
        )
