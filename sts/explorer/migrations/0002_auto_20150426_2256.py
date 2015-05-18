# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('explorer', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BeachWQSamples',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('StateCode', models.CharField(max_length=2)),
                ('BeachName', models.CharField(max_length=200)),
                ('StationID', models.CharField(max_length=200)),
                ('StationName', models.CharField(max_length=200)),
                ('CountyName', models.CharField(max_length=200)),
                ('Identifier', models.CharField(max_length=200)),
                ('StartDate', models.DateField()),
                ('StartTime', models.TimeField()),
                ('ZoneCode', models.CharField(max_length=200)),
                ('ActivityTypeCode', models.CharField(max_length=200)),
                ('CharacteristicName', models.CharField(max_length=200)),
                ('ResultValue', models.FloatField()),
                ('ResultMeasureUnit', models.CharField(max_length=200)),
                ('ResultComment', models.CharField(max_length=200)),
                ('ActivityDepthValue', models.CharField(max_length=200)),
                ('ActivityDepthUnitCode', models.CharField(max_length=200)),
                ('SampleCollectionMethodIdentifier', models.CharField(max_length=200)),
                ('SampleCollectionMethodName', models.CharField(max_length=200)),
                ('FieldGear', models.CharField(max_length=200)),
                ('AnalysisDateTime', models.CharField(max_length=200)),
                ('DetectionQuantitationLimit', models.CharField(max_length=200)),
            ],
        ),
        migrations.AlterField(
            model_name='beaches',
            name='BeachID',
            field=models.CharField(unique=True, max_length=8),
        ),
        migrations.AddField(
            model_name='beachwqsamples',
            name='BeachID',
            field=models.ForeignKey(to='explorer.Beaches', to_field=b'BeachID'),
        ),
    ]
