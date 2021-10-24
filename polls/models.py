from django.db import models
import datetime
from django.contrib.auth.models import User


class Player(models.Model):

    def __str__(self):
        return self.name

    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, default=None, blank=True)
    name = models.CharField(max_length=10)
    color = models.CharField(max_length=7, default='#000000')
    elo = models.IntegerField(default=1000)


class Boardgames(models.Model):

    def __str__(self):
        return self.name

    def not_played_recently(self, d):
        return self.lastTimePlayed <= datetime.date.today() - datetime.timedelta(days=d)

    gametype_choices = [('Classic','Classic'), ('Cooperative','Cooperative'), ('Party','Party'), ('Strategy','Strategy'), ('Family','Family')]

    name = models.CharField(max_length=50)
    owner = models.ForeignKey(Player, on_delete=models.CASCADE)
    minNumberOfPlayers = models.IntegerField(default=2)
    maxNumberOfPlayers = models.IntegerField(default=4)
    type = models.CharField(max_length=50, default='Strategy', choices=gametype_choices)
    # ordering = ['name']

class Expansion(models.Model):
    def __str__(self):
        return self.name
    basegame = models.ForeignKey(Boardgames, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)


class Gameplay(models.Model):

    def __str__(self):
        return self.name.name

    name = models.ForeignKey(Boardgames, on_delete=models.CASCADE)
    NumberOfPlayers = models.IntegerField(default=0)
    time = models.DurationField(default=datetime.timedelta(days=0, seconds=0))
    date = models.DateTimeField(default=datetime.datetime.now())
    with_results = models.BooleanField(default=True)

class Results(models.Model):

    def __str__(self):
        return self.gp_id.name.name

    gp_id = models.ForeignKey(Gameplay, on_delete=models.CASCADE, related_name = "results")
    p_id = models.ForeignKey(Player, on_delete=models.CASCADE)
    order = models.IntegerField(default=0)
    points = models.IntegerField(default=0)


class UsedExpansion(models.Model):
    def __str__(self):
        return self.gp_id.name.name

    gp_id = models.ForeignKey(Gameplay, on_delete=models.CASCADE)
    e_id = models.ForeignKey(Expansion, on_delete=models.CASCADE)
    used = models.BooleanField(default=False)
