# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('explorer', '0008_auto_20150518_0412'),
    ]

    operations = [
        migrations.CreateModel(
            name='WeatherDataPWS',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('Date', models.DateField()),
                ('PrecipitationIn', models.CharField(max_length=10, null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='WeatherStationsPWS',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('PwsId', models.CharField(max_length=20, null=True, blank=True)),
                ('Neighborhood', models.CharField(max_length=200, null=True, blank=True)),
                ('City', models.CharField(max_length=200, null=True, blank=True)),
                ('State', models.CharField(max_length=200, null=True, blank=True)),
                ('Country', models.CharField(max_length=200, null=True, blank=True)),
                ('Lat', models.CharField(max_length=50, null=True, blank=True)),
                ('Lon', models.CharField(max_length=50, null=True, blank=True)),
                ('DistanceKm', models.CharField(max_length=20, null=True, blank=True)),
                ('DistanceMi', models.CharField(max_length=20, null=True, blank=True)),
                ('BeachID', models.ForeignKey(to='explorer.Beaches')),
            ],
        ),
        migrations.RemoveField(
            model_name='weatherstations',
            name='PwsId',
        ),
        migrations.AddField(
            model_name='weatherdatapws',
            name='Station',
            field=models.ForeignKey(to='explorer.WeatherStationsPWS'),
        ),
    ]
