from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.db import models

from manufacturer.models import Manufacturer


class SSD(models.Model):

    class Meta:
        verbose_name = _('SSD')
        verbose_name_plural = _('SSDs')
        ordering = ['manufacturer', 'series', 'capacity']
        permissions = {
            ('view_bench', 'View benchmarks for this hardware'),
        }

    def __unicode__(self):
        return "{} {} - {}GB - {}".format(
            self.manufacturer,
            self.series.name,
            self.capacity,
            self.form_factor
        )

    manufacturer = models.ForeignKey(
        Manufacturer,
        on_delete=models.SET_NULL,
        related_name='ssds',
        blank=True,
        null=True,
        limit_choices_to={'ssd': True}
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
        Manufacturer,
        on_delete=models.SET_NULL,
        related_name='ssd_series',
        null=True,
        blank=True,
        limit_choices_to={'ssd': True})
