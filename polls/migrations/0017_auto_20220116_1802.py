# Generated by Django 3.1.7 on 2022-01-16 17:02

import datetime

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0016_auto_20220105_1914'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gameplay',
            name='date',
            field=models.DateTimeField(
                default=datetime.datetime(2022, 1, 16, 18, 2, 48, 644993)
            ),
        ),
        migrations.CreateModel(
            name='Mechanics',
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
                (
                    'boardgame',
                    models.ManyToManyField(
                        related_name='mechanics', to='polls.Boardgames'
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name='Category',
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
                (
                    'boardgame',
                    models.ManyToManyField(
                        related_name='category', to='polls.Boardgames'
                    ),
                ),
            ],
        ),
    ]
