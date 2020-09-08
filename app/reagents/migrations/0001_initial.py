# Generated by Django 3.1 on 2020-09-01 21:02

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AutoStainerStation',
            fields=[
                ('autostainer_sn', models.TextField(primary_key=True, serialize=False)),
                ('name', models.TextField()),
                ('latest_sync_time_PA', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='PA',
            fields=[
                ('fullname', models.TextField()),
                ('alias', models.TextField()),
                ('source', models.TextField()),
                ('volume', models.IntegerField(default=0)),
                ('incub', models.IntegerField(default=15)),
                ('ar', models.TextField(default='NO')),
                ('description', models.TextField()),
                ('is_factory', models.BooleanField(default=False)),
                ('catalog', models.TextField(primary_key=True, serialize=False)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'ordering': ['catalog'],
            },
        ),
        migrations.CreateModel(
            name='QP',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Reagent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reagent_sn', models.TextField(unique=True)),
                ('reag_name', models.TextField()),
                ('catalog', models.TextField()),
                ('r_type', models.TextField()),
                ('size', models.TextField()),
                ('log', models.TextField()),
                ('vol', models.IntegerField()),
                ('vol_cur', models.IntegerField()),
                ('sequence', models.IntegerField()),
                ('reserved', models.IntegerField()),
                ('mfg_date', models.DateField()),
                ('exp_date', models.DateField()),
                ('edit_date', models.DateTimeField()),
                ('factory', models.BooleanField(default=False)),
                ('autostainer_sn', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='reagents.autostainerstation')),
            ],
        ),
        migrations.CreateModel(
            name='PADelta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fullname', models.TextField()),
                ('alias', models.TextField()),
                ('source', models.TextField()),
                ('volume', models.IntegerField(default=0)),
                ('incub', models.IntegerField(default=15)),
                ('ar', models.TextField(default='NO')),
                ('description', models.TextField()),
                ('is_factory', models.BooleanField(default=False)),
                ('catalog', models.TextField()),
                ('operation', models.TextField()),
                ('update_at', models.DateTimeField()),
                ('autostainer_sn', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='reagents.autostainerstation')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]