import datetime

from django.contrib.auth.models import User
from django.db import models
from django.forms.models import model_to_dict


class Player(models.Model):
    def __str__(self):
        return self.name

    def get_owned(self, id):
        return OwnBoardgame.objects.filter(p_id__id=id).values_list(
            'bg_id__id', flat=True
        )

    def get_played(self, id):
        return Gameplay.objects.filter(
            id__in=list(
                Results.objects.filter(p_id=id).values_list('gp_id', flat=True)
            )
        )

    user = models.OneToOneField(
        User, on_delete=models.SET_NULL, null=True, default=None, blank=True
    )
    name = models.CharField(max_length=10)
    color = models.CharField(max_length=7, default='#000000')
    elo = models.IntegerField(default=1000)

no_image = 'https://cf.geekdo-images.com/zxVVmggfpHJpmnJY9j-k1w__square100/img/siQ9W5848OomWFJZY_SWYef6rpw=/100x100/filters:strip_icc()/pic1657689.jpg' # NOQA


class Boardgames(models.Model):
    def __str__(self):
        return self.name

    def not_played_recently(self, d):
        return (
            self.lastTimePlayed
            <= datetime.date.today() - datetime.timedelta(days=d)
        )

    def to_dict(self):
        data = model_to_dict(self)
        data['mechanics'] = self.mechanics.all()
        data['category'] = self.category.all()
        data['designer'] = self.designer.all()
        return data

    name = models.CharField(max_length=50)
    minNumberOfPlayers = models.IntegerField(default=2)
    maxNumberOfPlayers = models.IntegerField(default=4)
    minage = models.IntegerField(default=10)
    minplaytime = models.IntegerField(default=30)
    maxplaytime = models.IntegerField(default=60)
    year = models.IntegerField(default=2000)
    weight = models.DecimalField(default=0, max_digits=4, decimal_places=2)
    rank = models.DecimalField(default=5.5, max_digits=4, decimal_places=2)
    bgg_id = models.IntegerField(default=1)
    img_link = models.URLField(default=no_image, max_length=300)
    basegame = models.ManyToManyField('self',
                                      related_name='expansion',
                                      symmetrical=False,
                                      blank=True)
    standalone = models.BooleanField(default=True)


class OwnBoardgame(models.Model):
    def __str__(self):
        return f'{self.bg_id.name} - {self.p_id.name}'

    bg_id = models.ForeignKey(Boardgames, on_delete=models.CASCADE)
    p_id = models.ForeignKey(Player, on_delete=models.CASCADE)


class Gameplay(models.Model):
    def __str__(self):
        return self.name.name

    def get_players(self):
        return ', '.join(
            list(self.results.all().values_list('p_id__name', flat=True))
        )

    name = models.ForeignKey(Boardgames, on_delete=models.CASCADE)
    NumberOfPlayers = models.IntegerField(default=0)
    date = models.DateTimeField(default=datetime.datetime.now)
    time = models.DurationField(default=datetime.timedelta(days=0, seconds=0))
    with_results = models.BooleanField(default=True)


class PlayerSpecifics(models.Model):
    def __str__(self):
        return self.name

    name = models.CharField(max_length=50)
    bg_id = models.ForeignKey(Boardgames, on_delete=models.CASCADE)


class Results(models.Model):
    def __str__(self):
        return self.gp_id.name.name

    gp_id = models.ForeignKey(
        Gameplay, on_delete=models.CASCADE, related_name='results'
    )
    p_id = models.ForeignKey(Player, on_delete=models.CASCADE)
    order = models.IntegerField(default=0)
    points = models.IntegerField(default=0)
    player_order = models.IntegerField(default=0)
    player_specifics = models.ForeignKey(
        PlayerSpecifics, blank=True, null=True, on_delete=models.SET_NULL
    )


class UsedExpansion(models.Model):
    def __str__(self):
        return self.gp_id.name.name

    gp_id = models.ForeignKey(Gameplay, on_delete=models.CASCADE)
    e_id = models.ForeignKey(Boardgames, on_delete=models.CASCADE, null=True)
    used = models.BooleanField(default=False)


class Mechanics(models.Model):
    def __str__(self):
        return self.name

    name = models.CharField(max_length=50)
    boardgame = models.ManyToManyField(Boardgames, related_name='mechanics')


class Category(models.Model):
    def __str__(self):
        return self.name

    name = models.CharField(max_length=50)
    boardgame = models.ManyToManyField(Boardgames, related_name='category')


class Designer(models.Model):
    def __str__(self):
        return self.name

    name = models.CharField(max_length=50)
    boardgame = models.ManyToManyField(Boardgames, related_name='designer')
