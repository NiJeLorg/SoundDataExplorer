# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-08-01 20:02
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('explorer', '0014_beachstorypage_beach_id'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='beaches',
            options={'ordering': ['BeachName']},
        ),
    ]
