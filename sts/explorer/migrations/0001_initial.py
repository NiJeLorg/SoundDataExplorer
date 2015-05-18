# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Beaches',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('State', models.CharField(max_length=2)),
                ('County', models.CharField(max_length=100)),
                ('BeachID', models.CharField(max_length=8)),
                ('BeachName', models.CharField(max_length=200)),
                ('OwnAccess', models.CharField(max_length=200)),
                ('BeachLength', models.FloatField()),
                ('BeachTier', models.IntegerField()),
                ('StartLatitude', models.FloatField()),
                ('StartLongitude', models.FloatField()),
                ('EndLatitude', models.FloatField()),
                ('EndLongitude', models.FloatField()),
            ],
        ),
    ]
