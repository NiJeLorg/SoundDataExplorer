# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('explorer', '0004_auto_20150506_2205'),
    ]

    operations = [
        migrations.CreateModel(
            name='WeatherData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('Date', models.DateField()),
                ('TemperatureHighF', models.IntegerField(null=True, blank=True)),
                ('TemperatureAvgF', models.IntegerField(null=True, blank=True)),
                ('TemperatureLowF', models.IntegerField(null=True, blank=True)),
                ('DewpointHighF', models.IntegerField(null=True, blank=True)),
                ('DewpointAvgF', models.IntegerField(null=True, blank=True)),
                ('DewpointLowF', models.IntegerField(null=True, blank=True)),
                ('HumidityHigh', models.IntegerField(null=True, blank=True)),
                ('HumidityAvg', models.IntegerField(null=True, blank=True)),
                ('HumidityLow', models.IntegerField(null=True, blank=True)),
                ('PressureMaxIn', models.FloatField(null=True, blank=True)),
                ('PressureMinIn', models.FloatField(null=True, blank=True)),
                ('WindSpeedMaxMPH', models.IntegerField(null=True, blank=True)),
                ('WindSpeedAvgMPH', models.IntegerField(null=True, blank=True)),
                ('GustSpeedMaxMPH', models.IntegerField(null=True, blank=True)),
                ('PrecipitationSumIn', models.FloatField(null=True, blank=True)),
                ('Station', models.ForeignKey(to='explorer.WeatherStations')),
            ],
        ),
    ]
