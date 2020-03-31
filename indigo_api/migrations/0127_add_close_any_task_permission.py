# -*- coding: utf-8 -*-
# Generated by Django 1.11.27 on 2020-03-24 16:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('indigo_api', '0126_drop_commencement_details_from_work'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='task',
            options={'permissions': (('submit_task', 'Can submit an open task for review'), ('cancel_task', 'Can cancel a task that is open or has been submitted for review'), ('reopen_task', 'Can reopen a task that is closed or cancelled'), ('unsubmit_task', 'Can unsubmit a task that has been submitted for review'), ('close_task', 'Can close a task that has been submitted for review'), ('close_any_task', 'Can close any task that has been submitted for review, regardless of who submitted it'))},
        ),
        migrations.AlterField(
            model_name='task',
            name='labels',
            field=models.ManyToManyField(related_name='tasks', to='indigo_api.TaskLabel'),
        ),
    ]