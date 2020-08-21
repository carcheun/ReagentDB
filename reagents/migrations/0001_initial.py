# Generated by Django 3.1 on 2020-08-21 14:48

from django.db import migrations, models
import django.db.models.deletion


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
            ],
        ),
        migrations.CreateModel(
            name='PA',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fullname', models.TextField()),
                ('alias', models.TextField()),
                ('source', models.TextField()),
                ('catalog', models.TextField(blank=True, unique=True)),
                ('volume', models.IntegerField(default=0)),
                ('incub', models.IntegerField()),
                ('ar', models.TextField()),
                ('description', models.TextField()),
                ('factory', models.IntegerField(default=1)),
                ('date', models.DateField()),
                ('time', models.DateTimeField()),
                ('is_factory', models.BooleanField(default=False)),
            ],
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
    ]
