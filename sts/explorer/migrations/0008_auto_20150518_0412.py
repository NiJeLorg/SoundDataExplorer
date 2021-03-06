# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('explorer', '0007_auto_20150512_2217'),
    ]

    operations = [
        migrations.AddField(
            model_name='monthlyscores',
            name='TotalDryWeatherSamples',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='monthlyscores',
            name='TotalWetWeatherSamples',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
