# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-08-21 15:59
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('indigo_app', '0013_country_force_primary_language'),
    ]

    database_operations = [
        migrations.AlterModelTable('country', 'indigo_api_country'),
        migrations.AlterModelTable('language', 'indigo_api_language'),
    ]

    # Don't modify the Django 'state' yet
    state_operations = [
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=database_operations,
            state_operations=state_operations
        )
    ]
