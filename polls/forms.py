from django import forms
from .models import *

class BoardgameForm(forms.ModelForm):
    class Meta:
        model = Boardgames
        fields = ('name', 'owner', 'minNumberOfPlayers', 'maxNumberOfPlayers')


class GameplayForm(forms.ModelForm):
    class Meta:
        model = Gameplay
        # name = forms.ModelChoiceField(label="Boardgame", queryset= Boardgames.objects.all())
        # name = forms.ChoiceField(label="Boardgame",widget=forms.Select(choices=Boardgames.objects.all()))
        # NoP = forms.ChoiceField(label="Number of players", widget=forms.Select(choices=range(Boardgames.objects.all())))
        fields = ('name', 'NumberOfPlayers', 'time')

        # def __init__(self, *args, **kwargs):
        #     super().__init__(*args, **kwargs)
        #     self.fields['NumberOfPlayers'].queryset = Boardgames.objects.none()

class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        exclude = ()




class ResultsForm(forms.ModelForm):
    class Meta:
        model = Results
        exclude = ()

            # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['city'].queryset = Boardgames.objects.none()

        # name = models.CharField(max_length=50)
        # minNumberOfPlayers = models.IntegerField(default=0)
        # maxNumberOfPlayers = models.IntegerField(default=0)
        # numberOfGames = models.IntegerField(default=0)
        # totalTime = models.DurationField(default=datetime.timedelta(days=0, seconds=0))
        # lastTimePlayed = models.DateField(auto_now=True)