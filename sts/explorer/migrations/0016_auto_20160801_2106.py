# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-08-01 21:06
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('explorer', '0015_auto_20160801_2002'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='beachstorypage',
            name='beach_id',
        ),
        migrations.AddField(
            model_name='beachstorypage',
            name='beach',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='explorer.Beaches'),
            preserve_default=False,
        ),
    ]