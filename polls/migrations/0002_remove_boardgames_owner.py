# Generated by Django 3.1.1 on 2020-09-20 08:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='boardgames',
            name='owner',
        ),
    ]
