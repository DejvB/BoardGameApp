# Generated by Django 3.1.7 on 2022-02-01 08:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0023_auto_20220131_2054'),
    ]

    operations = [
        migrations.AlterField(
            model_name='boardgames',
            name='basegame',
            field=models.ManyToManyField(blank=True, related_name='expansion', to='polls.Boardgames'),
        ),
    ]
