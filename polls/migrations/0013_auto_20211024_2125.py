# Generated by Django 3.1.7 on 2021-10-24 19:25

import datetime

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('polls', '0012_auto_20210713_1114'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='user',
            field=models.OneToOneField(
                default=None,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name='gameplay',
            name='date',
            field=models.DateTimeField(
                default=datetime.datetime(2021, 10, 24, 21, 25, 3, 773596)
            ),
        ),
    ]
