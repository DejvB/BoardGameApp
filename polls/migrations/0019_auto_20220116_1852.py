# Generated by Django 3.1.7 on 2022-01-16 17:52

import datetime

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0018_auto_20220116_1851'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gameplay',
            name='date',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
    ]