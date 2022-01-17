from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import (
    Boardgames,
    Expansion,
    Gameplay,
    OwnBoardgame,
    OwnExpansion,
    Player,
    PlayerSpecifics,
    Results,
    UsedExpansion,
)


class BoardgameForm(forms.ModelForm):
    class Meta:
        model = Boardgames
        fields = ('name', 'type', 'minNumberOfPlayers', 'maxNumberOfPlayers')


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
    name = forms.ModelChoiceField(Boardgames.objects.order_by('name'))
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


class ExpansionForm(forms.ModelForm):
    basegame = forms.ModelChoiceField(Boardgames.objects.order_by('name'))

    class Meta:
        model = Expansion
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
    player_order = forms.ChoiceField()

    class Meta:
        model = Results
        exclude = ()


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
    class Meta:
        model = OwnBoardgame
        exclude = ()
        widgets = {'p_id': forms.HiddenInput()}


class OwnExpansionForm(forms.ModelForm):
    class Meta:
        model = OwnExpansion
        exclude = ()
        widgets = {'p_id': forms.HiddenInput()}
