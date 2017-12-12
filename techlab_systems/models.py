# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.db import models


class SystemConfiguration(models.Model):

    class Meta:
        verbose_name = _('System configurations')
        verbose_name_plural = _('System configurations')

    def __unicode__(self):
        return "{hardware_configuration} — {software_configuration}".format(
            hardware_configuration=self.hardware_configuration.name,
            software_configuration=self.software_configuration.name,
        )

    hardware_configuration = models.ForeignKey(
        'HardwareConfiguration',
        on_delete=models.CASCADE,
        related_name='system_configurations'
    )
    software_configuration = models.ForeignKey(
        'SoftwareConfiguration',
        on_delete=models.CASCADE,
        related_name='system_configurations',
        blank=True,
        null=True
    )


class Node(models.Model):

    class Meta:
        verbose_name = _('Node')
        verbose_name_plural = _('Nodes')
        ordering = ('hostname',)

    def __unicode__(self):
        return "{hostname}".format(hostname=self.hostname)

    hostname = models.CharField(max_length=255, primary_key=True)
    hardware_configuration = models.ForeignKey(
        'HardwareConfiguration',
        on_delete=models.CASCADE,
        related_name='nodes',
        blank=True,
        null=True
    )
    software_configuration = models.ForeignKey(
        'SoftwareConfiguration',
        on_delete=models.CASCADE,
        related_name='nodes',
        blank=True,
        null=True
    )


class HardwareConfiguration(models.Model):

    class Meta:
        verbose_name = _('Hardware configuration')
        verbose_name_plural = _('Hardware configurations')
        permissions = {
            ('view_bench', 'View benchmarks for this hardware'),
        }

    def __unicode__(self):
        return "{} - {}".format(self.owner, self.name)

    name = models.CharField(max_length=255)
    architecture = models.ForeignKey(
        'Architecture',
        blank=True,
        null=True,
        related_name='node_families',
        on_delete=models.CASCADE
    )

    visible = models.BooleanField(default=False)
    owner = models.CharField(max_length=255)
    vendor = models.CharField(max_length=255)


class ByteOrder(models.Model):

    class Meta:
        verbose_name = _('byte order')
        verbose_name = _('byte orders')

    def __unicode__(self):
        return self.endianness

    endianness = models.CharField(max_length=255)


class SoftwareConfiguration(models.Model):

    class Meta:
        verbose_name = _('Software configuration')
        verbose_name_plural = _('Software configurations')

    def __unicode__(self):
        return "{name} — {os} {os_version}".format(
            name=self.name,
            os=self.os.name,
            os_version=self.os.version,
        )

    name = models.CharField(max_length=255)
    os = models.ForeignKey('OS', on_delete=models.CASCADE)


class OS(models.Model):

    class Meta:
        verbose_name = _('Operating system')
        verbose_name_plural = _('Operating systems')

    def __unicode__(self):
        return "{name} — {version}".format(
            name=self.name,
            version=self.version
        )

    name = models.CharField(max_length=255)
    version = models.CharField(max_length=255)


class Architecture(models.Model):

    class Meta:
        verbose_name = _('Architecture')
        verbose_name_plural = _('Architectures')

    def __unicode__(self):
        return "{name} ({shortname})".format(
            name=self.name,
            shortname=self.shortname
        )

    name = models.CharField(max_length=255)
    shortname = models.CharField(max_length=255)


class Alias(models.Model):

    class Meta:
        verbose_name = _('Alias')
        verbose_name_plural = _('Aliases')

    def __unicode__(self):
        return "{name} — {host}".format(
            name=self.name,
            host=self.node.hostname
        )

    name = models.CharField(max_length=255)
    node = models.ForeignKey(
        'Node',
        on_delete=models.CASCADE,
        related_name='aliases'
    )


class SSD(models.Model):

    class Meta:
        verbose_name = _('SSD')
        verbose_name_plural = _('SSDs')
        ordering = ['manufacturer', 'series', 'capacity']

    def __unicode__(self):
        return "{} {} - {}GB - {}".format(
            self.manufacturer,
            self.series.name,
            self.capacity,
            self.form_factor
        )

    manufacturer = models.ForeignKey(
        'Manufacturer',
        on_delete=models.CASCADE,
        related_name='ssds'
    )
    series = models.ForeignKey(
        'SSDSeries',
        on_delete=models.CASCADE,
        related_name='ssds'
    )
    capacity = models.IntegerField(verbose_name="capacity (GB)")
    model_name = models.CharField(max_length=255, null=True, blank=True)
    form_factor = models.ForeignKey(
        'SSDFormFactor',
        on_delete=models.SET_NULL,
        related_name='ssds',
        verbose_name="form factor",
        null=True,
        blank=True
    )
    interface = models.ForeignKey(
        'SSDInterface',
        on_delete=models.SET_NULL,
        related_name='ssds',
        null=True,
        blank=True
    )
    flash_type = models.ForeignKey(
        'SSDFlashType',
        on_delete=models.SET_NULL,
        related_name='ssds',
        verbose_name="flash type",
        null=True,
        blank=True
    )
    process_size = models.ForeignKey(
        'SSDProcessSize',
        on_delete=models.SET_NULL,
        related_name='ssds',
        verbose_name="process size",
        null=True,
        blank=True
    )
    controller = models.ForeignKey(
        'SSDController',
        on_delete=models.SET_NULL,
        related_name='ssds',
        null=True,
        blank=True
    )
    endurance = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="endurance (DWPD)",
        null=True,
        blank=True
    )


class Manufacturer(models.Model):
    class Meta:
        verbose_name = _('SSD manufacturer')
        verbose_name_plural = _('SSD manufacturers')

    def __unicode__(self):
        return self.name

    name = models.CharField(max_length=255)


class SSDFormFactor(models.Model):
    class Meta:
        verbose_name = _('SSD form factor')
        verbose_name_plural = _('SSD form factors')

    def __unicode__(self):
        return self.name

    name = models.CharField(max_length=255)


class SSDInterface(models.Model):
    class Meta:
        verbose_name = _('SSD interface')
        verbose_name_plural = _('SSD interfaces')

    def __unicode__(self):
        return self.name

    name = models.CharField(max_length=255)


class SSDFlashType(models.Model):
    class Meta:
        verbose_name = _('SSD flash type')
        verbose_name_plural = _('SSD flash types')

    def __unicode__(self):
        return self.name

    name = models.CharField(max_length=255)


class SSDProcessSize(models.Model):
    class Meta:
        verbose_name = _('SSD process size')
        verbose_name_plural = _('SSD process sizes')

    def __unicode__(self):
        return "{} nm".format(self.size)

    size = models.IntegerField(verbose_name="size (nm)")


class SSDController(models.Model):
    class Meta:
        verbose_name = _('SSD controller')
        verbose_name_plural = _('SSD controllers')

    def __unicode__(self):
        return self.name

    name = models.CharField(max_length=255)


class SSDSeries(models.Model):
    class Meta:
        verbose_name = _('SSD series')
        verbose_name_plural = _('SSD series')

    def __unicode__(self):
        return "{} {}".format(self.manufacturer, self.name)

    name = models.CharField(max_length=255)
    manufacturer = models.ForeignKey(
        'Manufacturer',
        on_delete=models.CASCADE,
        related_name='ssd_series'
    )
