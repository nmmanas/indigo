# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2019-12-05 08:53
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('indigo_api', '0121_country_italics_terms'),
    ]

    operations = [
        migrations.AddField(
            model_name='annotation',
            name='selectors',
            field=django.contrib.postgres.fields.jsonb.JSONField(null=True),
        ),
    ]