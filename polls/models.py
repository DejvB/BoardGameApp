from django.db import models
import datetime


class Player(models.Model):

    def __str__(self):
        return self.name

    name = models.CharField(max_length=10)


class Boardgames(models.Model):

    def __str__(self):
        return self.name

    def not_played_recently(self, d):
        return self.lastTimePlayed <= datetime.date.today() - datetime.timedelta(days=d)

    name = models.CharField(max_length=50)
    owner = models.ForeignKey(Player, on_delete=models.CASCADE)
    minNumberOfPlayers = models.IntegerField(default=2)
    maxNumberOfPlayers = models.IntegerField(default=4)


class Gameplay(models.Model):

    def __str__(self):
        return self.name.name

    name = models.ForeignKey(Boardgames, on_delete=models.CASCADE)
    NumberOfPlayers = models.IntegerField(default=0)
    time = models.DurationField(default=datetime.timedelta(days=0, seconds=0))
    date = models.DateTimeField(auto_now=True)


class Results(models.Model):

    def __str__(self):
        return self.gp_id

    gp_id = models.ForeignKey(Gameplay, on_delete=models.CASCADE)
    p_id = models.ForeignKey(Player, on_delete=models.CASCADE)
    order = models.IntegerField(default=0)
    points = models.IntegerField(default=0)
