from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.db import models

from manufacturer.models import Manufacturer


class CPU(models.Model):

    class Meta:
        verbose_name = _('CPU')
        verbose_name_plural = _('CPUs')

    def __unicode__(self):
        return "{} {} {}GHz".format(
            self.manufacturer.name,
            self.model_name,
            self.base_frequency
        )

    manufacturer = models.ForeignKey(
        Manufacturer,
        on_delete=models.CASCADE,
        related_name='cpus',
        limit_choices_to={'cpu': True}
    )
    model_name = models.CharField(max_length=255, verbose_name='model name')
    nb_cores = models.IntegerField(
        verbose_name="number of cores",
        null=True, blank=True
    )

    # lscpu
    architecture = models.ForeignKey(
        'Architecture',
        related_name='cpus',
        on_delete=models.CASCADE
    )
#    byte_order = models.ForeignKey('ByteOrder', related_name='cpus', on_delete=models.CASCADE)
#    cpus = models.IntegerField()
#    on_line_cpus_list_min = models.IntegerField()
#    on_line_cpus_list_max = models.IntegerField()
#    threads_per_core = models.IntegerField()
#    cores_per_socket = models.IntegerField()
#    sockets = models.IntegerField()

    # lscpu - optional fields
#    numa_nodes = models.IntegerField(blank=True, null=True)
#    l1d_cache = models.IntegerField(blank=True, null=True)
#    l1i_cache = models.IntegerField(blank=True, null=True)
#    l2_cache = models.IntegerField(blank=True, null=True)
#    l3_cache = models.IntegerField(blank=True, null=True)
    base_frequency = models.DecimalField(
        verbose_name="base frequency (GHz)",
        max_digits=5,
        decimal_places=2
    )
    max_frequency = models.DecimalField(
        verbose_name="max frequency (GHz)",
        max_digits=5,
        decimal_places=2,
        null=True, blank=True
    )


class Architecture(models.Model):

    class Meta:
        verbose_name = _('Architecture')
        verbose_name_plural = _('Architectures')
        ordering = ['name']

    def __unicode__(self):
        return "{name} ({shortname})".format(
            name=self.name,
            shortname=self.shortname
        )

    name = models.CharField(max_length=255)
    shortname = models.CharField(max_length=255)
