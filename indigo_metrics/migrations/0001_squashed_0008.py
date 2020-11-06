# Generated by Django 2.2.12 on 2020-11-02 08:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    replaces = [('indigo_metrics', '0001_initial'), ('indigo_metrics', '0002_dailyworkmetrics'), ('indigo_metrics', '0003_auto_20190510_2007'), ('indigo_metrics', '0004_auto_20190511_0643'), ('indigo_metrics', '0005_backfill_completeness'), ('indigo_metrics', '0006_auto_20190901_1340'), ('indigo_metrics', '0007_dailyplacemetrics'), ('indigo_metrics', '0008_backfill_daily_place_metrics')]

    initial = True

    dependencies = [
        ('indigo_api', '0001_squashed_0137'),
    ]

    operations = [
        migrations.CreateModel(
            name='WorkMetrics',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('n_languages', models.IntegerField(help_text='Number of languages in published documents', null=True)),
                ('n_expressions', models.IntegerField(help_text='Number of published documents', null=True)),
                ('n_points_in_time', models.IntegerField(help_text='Number of recorded points in time', null=True)),
                ('n_expected_expressions', models.IntegerField(help_text='Expected number of published documents', null=True)),
                ('work', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='metrics', to='indigo_api.Work')),
                ('p_breadth_complete', models.IntegerField(help_text='Percentage breadth complete', null=True)),
                ('p_complete', models.IntegerField(help_text='Percentage complete', null=True)),
                ('p_depth_complete', models.IntegerField(help_text='Percentage depth complete', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='DailyPlaceMetrics',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(db_index=True)),
                ('place_code', models.CharField(db_index=True, max_length=20)),
                ('n_activities', models.IntegerField(default=0)),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='indigo_api.Country')),
                ('locality', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='indigo_api.Locality')),
            ],
            options={
                'db_table': 'indigo_metrics_daily_placemetrics',
                'unique_together': {('date', 'place_code')},
            },
        ),
        migrations.CreateModel(
            name='DailyWorkMetrics',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(db_index=True)),
                ('place_code', models.CharField(db_index=True, max_length=20)),
                ('country', models.CharField(max_length=20)),
                ('locality', models.CharField(max_length=20, null=True)),
                ('n_works', models.IntegerField()),
                ('n_expressions', models.IntegerField(null=True)),
                ('n_points_in_time', models.IntegerField(null=True)),
                ('n_expected_expressions', models.IntegerField(null=True)),
                ('n_complete_works', models.IntegerField(null=True)),
                ('p_breadth_complete', models.IntegerField(null=True)),
                ('p_complete', models.IntegerField(null=True)),
                ('p_depth_complete', models.IntegerField(null=True)),
            ],
            options={
                'db_table': 'indigo_metrics_daily_workmetrics',
                'unique_together': {('date', 'place_code')},
            },
        ),
    ]