# Generated by Django 3.1.1 on 2020-12-05 10:57

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0009_auto_20201014_2159'),
    ]

    operations = [
        migrations.AddField(
            model_name='boardgames',
            name='type',
            field=models.CharField(choices=[('Classic', 'Classic'), ('Cooperative', 'Cooperative'), ('Party', 'Party'), ('Strategy', 'Strategy'), ('Family', 'Family')], default='Strategy', max_length=50),
        ),
        migrations.AlterField(
            model_name='gameplay',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2020, 12, 5, 11, 57, 6, 155102)),
        ),
    ]
