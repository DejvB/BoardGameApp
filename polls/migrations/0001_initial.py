# Generated by Django 3.1.1 on 2020-09-20 08:30

import datetime

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Boardgames',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                ('name', models.CharField(max_length=50)),
                ('minNumberOfPlayers', models.IntegerField(default=2)),
                ('maxNumberOfPlayers', models.IntegerField(default=4)),
            ],
        ),
        migrations.CreateModel(
            name='Gameplay',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                ('NumberOfPlayers', models.IntegerField(default=0)),
                ('time', models.DurationField(default=datetime.timedelta(0))),
                ('date', models.DateTimeField(auto_now=True)),
                (
                    'name',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to='polls.boardgames',
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                ('name', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Results',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                ('order', models.IntegerField(default=0)),
                ('points', models.IntegerField(default=0)),
                (
                    'gp_id',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to='polls.gameplay',
                    ),
                ),
                (
                    'p_id',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to='polls.player',
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name='boardgames',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='polls.player'),
        ),
    ]
