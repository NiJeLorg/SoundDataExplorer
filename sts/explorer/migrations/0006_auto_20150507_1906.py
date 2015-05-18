# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('explorer', '0005_weatherdata'),
    ]

    operations = [
        migrations.RenameField(
            model_name='weatherdata',
            old_name='PrecipitationSumIn',
            new_name='PrecipitationIn',
        ),
        migrations.RemoveField(
            model_name='weatherdata',
            name='DewpointAvgF',
        ),
        migrations.RemoveField(
            model_name='weatherdata',
            name='DewpointHighF',
        ),
        migrations.RemoveField(
            model_name='weatherdata',
            name='DewpointLowF',
        ),
        migrations.RemoveField(
            model_name='weatherdata',
            name='GustSpeedMaxMPH',
        ),
        migrations.RemoveField(
            model_name='weatherdata',
            name='HumidityAvg',
        ),
        migrations.RemoveField(
            model_name='weatherdata',
            name='HumidityHigh',
        ),
        migrations.RemoveField(
            model_name='weatherdata',
            name='HumidityLow',
        ),
        migrations.RemoveField(
            model_name='weatherdata',
            name='PressureMaxIn',
        ),
        migrations.RemoveField(
            model_name='weatherdata',
            name='PressureMinIn',
        ),
        migrations.RemoveField(
            model_name='weatherdata',
            name='TemperatureAvgF',
        ),
        migrations.RemoveField(
            model_name='weatherdata',
            name='TemperatureHighF',
        ),
        migrations.RemoveField(
            model_name='weatherdata',
            name='TemperatureLowF',
        ),
        migrations.RemoveField(
            model_name='weatherdata',
            name='WindSpeedAvgMPH',
        ),
        migrations.RemoveField(
            model_name='weatherdata',
            name='WindSpeedMaxMPH',
        ),
    ]
