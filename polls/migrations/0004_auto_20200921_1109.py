# Generated by Django 3.1.1 on 2020-09-21 09:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0003_boardgames_owner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gameplay',
            name='date',
            field=models.DateTimeField(),
        ),
    ]
