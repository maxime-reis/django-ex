from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.db import models


class Manufacturer(models.Model):
    class Meta:
        verbose_name = _('Manufacturer')
        verbose_name_plural = _('Manufacturers')
        ordering = ['name']

    def __unicode__(self):
        return self.name

    name = models.CharField(max_length=255)
    cpu = models.BooleanField(default=False, verbose_name='builds cpus?')
    ssd = models.BooleanField(default=False, verbose_name='builds ssds?')
