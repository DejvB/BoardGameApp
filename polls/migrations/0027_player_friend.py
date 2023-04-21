# Generated by Django 4.1 on 2023-04-21 09:38

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("polls", "0026_alter_boardgames_name_alter_gameplay_date_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="player",
            name="friend",
            field=models.ManyToManyField(
                blank=True, related_name="friend", to="polls.player"
            ),
        ),
    ]
