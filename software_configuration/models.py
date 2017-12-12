from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.db import models


class OS(models.Model):

    class Meta:
        verbose_name = _('Operating System')
        verbose_name_plural = _('Operating Systems')

    def __unicode__(self):
        return "{} - {}".format(self.name, self.version)

    name = models.CharField(max_length=255)
    version = models.CharField(max_length=255)
    release_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='release_name'
    )


class LinuxKernel(models.Model):

    class Meta:
        verbose_name = _('Linux kernel')
        verbose_name_plural = _('Linux kernels')

    def __unicode__(self):
        return self.version

    version = models.CharField(max_length=255)
