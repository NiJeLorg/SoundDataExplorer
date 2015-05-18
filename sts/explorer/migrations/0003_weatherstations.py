# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('explorer', '0002_auto_20150426_2256'),
    ]

    operations = [
        migrations.CreateModel(
            name='WeatherStations',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('Neighborhood', models.CharField(max_length=200, null=True, blank=True)),
                ('City', models.CharField(max_length=200, null=True, blank=True)),
                ('State', models.CharField(max_length=200, null=True, blank=True)),
                ('Country', models.CharField(max_length=200, null=True, blank=True)),
                ('Icao', models.CharField(max_length=4, null=True, blank=True)),
                ('Lat', models.FloatField(null=True, blank=True)),
                ('Lon', models.FloatField(null=True, blank=True)),
                ('PwsId', models.CharField(max_length=20, null=True, blank=True)),
                ('DistanceKm', models.IntegerField(null=True, blank=True)),
                ('DistanceMi', models.IntegerField(null=True, blank=True)),
                ('BeachID', models.ForeignKey(to='explorer.Beaches')),
            ],
        ),
    ]
