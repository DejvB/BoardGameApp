# Generated by Django 3.1.7 on 2022-01-05 19:14

import datetime

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0015_auto_20220102_1509'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='boardgames',
            name='owner',
        ),
        migrations.AlterField(
            model_name='gameplay',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 1, 5, 19, 14, 30, 891086)),
        ),
    ]
