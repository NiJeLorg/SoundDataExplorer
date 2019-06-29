# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2019-06-28 21:02
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('explorer', '0022_hourlyweatherdata_hourlyweatherdatapws'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hourlyweatherdatapws',
            name='Station',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='explorer.WeatherStationsPWS'),
        ),
    ]
