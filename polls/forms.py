from django import forms
from .models import *

class BoardgameForm(forms.ModelForm):
    class Meta:
        model = Boardgames
        fields = ('name', 'owner', 'minNumberOfPlayers', 'maxNumberOfPlayers')


class GameplayForm(forms.ModelForm):
    name = forms.ModelChoiceField(Boardgames.objects.order_by('name'))
    class Meta:
        model = Gameplay
        exclude = ()
        widgets = {
            'date':  forms.widgets.DateTimeInput(format='%Y-%m-%d %H:%M', attrs={'class':'myDateClass',
                                                                                 'type':'datetime-local',}),
        }
        labels = {
            'NumberOfPlayers': 'Number of players',
        }

class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        exclude = ()



class ResultsForm(forms.ModelForm):
    class Meta:
        model = Results
        exclude = ()



        # field_order = ['username', 'custom_field', 'password']