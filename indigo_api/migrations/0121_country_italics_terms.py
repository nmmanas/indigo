# -*- coding: utf-8 -*-
# Generated by Django 1.11.24 on 2019-12-04 13:35
from __future__ import unicode_literals

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('indigo_api', '0120_bulk_export_work_permission'),
    ]

    operations = [
        migrations.AddField(
            model_name='country',
            name='italics_terms',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=1024), blank=True, null=True, size=None),
        ),
    ]
