# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('explorer', '0003_weatherstations'),
    ]

    operations = [
        migrations.AlterField(
            model_name='weatherstations',
            name='DistanceKm',
            field=models.CharField(max_length=20, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='weatherstations',
            name='DistanceMi',
            field=models.CharField(max_length=20, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='weatherstations',
            name='Lat',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='weatherstations',
            name='Lon',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
    ]
