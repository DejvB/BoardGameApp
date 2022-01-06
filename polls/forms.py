from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import (
    Boardgames,
    Expansion,
    Gameplay,
    Player,
    Results,
    UsedExpansion,
)


class BoardgameForm(forms.ModelForm):
    class Meta:
        model = Boardgames
        fields = ('name', 'type', 'minNumberOfPlayers', 'maxNumberOfPlayers')


class GameplayForm(forms.ModelForm):
    name = forms.ModelChoiceField(Boardgames.objects.order_by('name'))

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
