# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('explorer', '0006_auto_20150507_1906'),
    ]

    operations = [
        migrations.CreateModel(
            name='MonthlyScores',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('MonthYear', models.DateField()),
                ('NumberOfSamples', models.IntegerField()),
                ('TotalPassSamples', models.IntegerField()),
                ('DryWeatherPassSamples', models.IntegerField()),
                ('WetWeatherPassSamples', models.IntegerField()),
                ('BeachID', models.ForeignKey(to='explorer.Beaches')),
            ],
        ),
        migrations.AlterField(
            model_name='weatherdata',
            name='PrecipitationIn',
            field=models.CharField(max_length=10, null=True, blank=True),
        ),
    ]
