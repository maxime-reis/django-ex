# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-01-18 14:49
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('software_configuration', '0001_initial'),
        ('techlab_systems', '0001_initial'),
        ('hardware_configuration', '0001_initial'),
        ('SSD', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='HEPSPEC06Run',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nb_workers', models.IntegerField()),
                ('score', models.DecimalField(decimal_places=2, max_digits=8)),
                ('active_energy', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('apparent_energy', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('system_configuration', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='benchmarks_hepspec06run', to='techlab_systems.SystemConfiguration')),
            ],
            options={
                'verbose_name': 'HEP-SPEC06 run',
                'verbose_name_plural': 'HEP-SPEC06 runs',
            },
        ),
        migrations.CreateModel(
            name='SSDBenchL2',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('percent_capacity_used', models.IntegerField(default=100, validators=[django.core.validators.MaxValueValidator(100), django.core.validators.MinValueValidator(0)])),
                ('access_type', models.IntegerField(choices=[(1, 'Sequential'), (2, 'Random')], default=1)),
                ('percent_write', models.IntegerField(default=100, validators=[django.core.validators.MaxValueValidator(100), django.core.validators.MinValueValidator(0)])),
                ('block_size', models.IntegerField()),
                ('threads', models.IntegerField(default=1)),
                ('qd_per_thread', models.IntegerField(default=1)),
                ('iops', models.IntegerField()),
                ('throughput', models.IntegerField()),
                ('read_latency', models.DecimalField(blank=True, decimal_places=10, max_digits=20, null=True)),
                ('write_latency', models.DecimalField(blank=True, decimal_places=10, max_digits=20, null=True)),
                ('test_description', models.CharField(max_length=1024)),
                ('comment', models.CharField(blank=True, max_length=1024, null=True)),
                ('cpu', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='benchmarks_ssdbenchl2', to='hardware_configuration.CPU', verbose_name='test bench cpu')),
                ('kernel', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='benchmarks_ssdbenchl2', to='software_configuration.LinuxKernel', verbose_name='test bench Linux kernel')),
                ('os', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='benchmarks_ssdbenchl2', to='software_configuration.OS', verbose_name='test bench OS')),
                ('ssd', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='benchmarks_ssdbenchl2', to='SSD.SSD')),
            ],
            options={
                'verbose_name': 'SSD bench run',
                'verbose_name_plural': 'SSD bench runs',
            },
        ),
        migrations.CreateModel(
            name='SSDBenchL2Stability',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cpu', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='benchmarks_ssdbenchl2stability', to='hardware_configuration.CPU', verbose_name='test bench cpu')),
                ('os', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='benchmarks_ssdbenchl2stability', to='software_configuration.OS', verbose_name='test bench OS')),
            ],
            options={
                'verbose_name': 'SSD IOPS stability benchmarks',
            },
        ),
    ]