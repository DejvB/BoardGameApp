# Generated by Django 3.1.7 on 2022-02-05 19:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0024_auto_20220201_0914'),
    ]

    operations = [
        migrations.CreateModel(
            name='ScoringSpecifics',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('bg_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='polls.boardgames')),
            ],
        ),
        migrations.CreateModel(
            name='ScoringTable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.IntegerField(default=0)),
                ('result_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='polls.results')),
                ('ss_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='polls.scoringspecifics')),
            ],
        ),
    ]