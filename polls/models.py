from django.db import models
import datetime

# class Question(models.Model):
#     question_text = models.CharField(max_length=200)
#     pub_date = models.DateTimeField('date published')
#
#
# class Choice(models.Model):
#     question = models.ForeignKey(Question, on_delete=models.CASCADE)
#     choice_text = models.CharField(max_length=200)
#     votes = models.IntegerField(default=0)


class Boardgames(models.Model):

    def __str__(self):
        return self.name

    def not_played_recently(self, d):
        return self.lastTimePlayed <= datetime.date.today() - datetime.timedelta(days=d)

    name = models.CharField(max_length=50)
    minNumberOfPlayers = models.IntegerField(default=0)
    maxNumberOfPlayers = models.IntegerField(default=0)

class Gameplay(models.Model):
    def __str__(self):
        return self.name

    name = models.ForeignKey(Boardgames, on_delete=models.CASCADE)
    NumberOfPlayers = models.IntegerField(default=0)
    time = models.DurationField(default=datetime.timedelta(days=0, seconds=0))
    date = models.DateField(auto_now=True)

class Player(models.Model):
    def __str__(self):
        return self.name

    name = models.CharField(max_length=10)


class Results(models.Model):
    gp_id = models.ForeignKey(Gameplay, on_delete=models.CASCADE)
    p_id = models.ForeignKey(Player, on_delete=models.CASCADE)
    order = models.IntegerField(default=0)
    points = models.IntegerField(default=0)
