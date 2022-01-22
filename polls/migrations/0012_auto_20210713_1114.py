# Generated by Django 3.1.7 on 2021-07-13 09:14

import datetime

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0011_auto_20201205_1306'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='elo',
            field=models.IntegerField(default=1000),
        ),
        migrations.AlterField(
            model_name='gameplay',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2021, 7, 13, 11, 14, 34, 409120)),
        ),
        migrations.AlterField(
            model_name='results',
            name='gp_id',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='results',
                to='polls.gameplay',
            ),
        ),
    ]
