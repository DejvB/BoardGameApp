import datetime

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import (
    Boardgames,
    Gameplay,
    OwnBoardgame,
    Player,
    PlayerSpecifics,
    Results,
    ScoringSpecifics,
    ScoringTable,
    UsedExpansion,
)


class BoardgameForm(forms.ModelForm):
    class Meta:
        model = Boardgames
        fields = ('name', 'minNumberOfPlayers', 'maxNumberOfPlayers')


time_choices = (
    (120, '2h'),
    (60, '1h'),
    (45, '45m'),
    (30, '30m'),
    (15, '15m'),
    (10, '10m'),
    (5, '5m'),
)


class GameplayForm(forms.ModelForm):
    name = forms.ModelChoiceField(Boardgames.objects
                                  .filter(standalone=True)
                                  .order_by('name'))
    time = forms.MultipleChoiceField(
        choices=time_choices,
        required=False,
        widget=forms.CheckboxSelectMultiple(),
    )

    class Meta:
        model = Gameplay
        exclude = ()
        widgets = {
            'NumberOfPlayers': forms.widgets.Select(),
            'date': forms.widgets.DateTimeInput(
                format='%Y-%m-%d %H:%M',
                attrs={
                    'class': 'myDateClass',
                    'type': 'datetime-local',
                },
            ),
        }
        labels = {
            'NumberOfPlayers': 'Number of players',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['NumberOfPlayers'].queryset = range(2, 5)


class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        exclude = ()


class UsedExpansionForm(forms.ModelForm):
    class Meta:
        model = UsedExpansion
        fields = ('used', 'gp_id', 'e_id')
        widgets = {'gp_id': forms.HiddenInput(), 'e_id': forms.HiddenInput()}
        # widgets = {'e_id': forms.HiddenInput()}


class ResultsForm(forms.ModelForm):
    player_specifics = forms.ModelChoiceField(
        PlayerSpecifics.objects.order_by('name')
    )
    gp_id = forms.ModelChoiceField(Gameplay.objects.filter(date__gte=datetime.datetime.now() - datetime.timedelta(days=7)).order_by('-id'))
    p_id = forms.ModelChoiceField(Player.objects.order_by('name'))
    player_order = forms.ChoiceField()
    order = forms.ChoiceField()

    class Meta:
        model = Results
        exclude = ()
        widgets = {'points': forms.NumberInput(attrs={'style': 'width:10ch'})}


class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

        # field_order = ['username', 'custom_field', 'password']


class OwnBoardgameForm(forms.ModelForm):
    bg_id = forms.ModelChoiceField(Boardgames.objects.filter(standalone=True).order_by('name'))

    class Meta:
        model = OwnBoardgame
        exclude = ()
        widgets = {'p_id': forms.HiddenInput()}


class OwnExpansionForm(forms.ModelForm):
    basegame = forms.ModelChoiceField(Boardgames.objects.filter(standalone=True).order_by('name'))
    expansion = forms.ModelChoiceField(Boardgames.objects.all().order_by('name'))

    class Meta:
        model = OwnBoardgame
        fields = ('basegame', 'expansion', 'p_id')
        widgets = {'p_id': forms.HiddenInput()}


class ScoringTableForm(forms.ModelForm):
    class Meta:
        model = ScoringTable
        fields = ('ss_id', 'score', 'result_id')
        widgets = {'result_id': forms.HiddenInput(), 'score': forms.NumberInput(attrs={'style': 'width:10ch'})}
        disabled = ('ss_id',)


class PlayerSpecificsForm(forms.ModelForm):

    class Meta:
        model = PlayerSpecifics
        exclude = ()

    def __init__(self, *args, **kwargs):
        super(PlayerSpecificsForm, self).__init__(*args, **kwargs)
        self.fields['bg_id'].queryset = self.fields['bg_id'].queryset.order_by('name')


class ScoringSpecificsForm(forms.ModelForm):
    class Meta:
        model = ScoringSpecifics
        exclude = ()

    def __init__(self, *args, **kwargs):
        super(ScoringSpecificsForm, self).__init__(*args, **kwargs)
        self.fields['bg_id'].queryset = self.fields['bg_id'].queryset.order_by('name')


class GameplaysWithPossibleScoringResultsForm(forms.Form):
    gameplays = forms.ChoiceField(choices=[['0', '0'], ])
