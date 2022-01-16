# Generated by Django 3.1.7 on 2022-01-16 17:51

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0017_auto_20220116_1802'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gameplay',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 1, 16, 18, 51, 55, 428869)),
        ),
        migrations.CreateModel(
            name='Designer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('boardgame', models.ManyToManyField(related_name='designer', to='polls.Boardgames')),
            ],
        ),
    ]
