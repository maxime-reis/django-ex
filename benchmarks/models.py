# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.postgres.fields import ArrayField

from techlab_systems.models import (
    HardwareConfiguration, SoftwareConfiguration, SystemConfiguration
)
from software_configuration.models import OS, LinuxKernel
from hardware_configuration.models import CPU
from SSD.models import SSD

import datetime


class HEPSPEC06Run(models.Model):

    class Meta:
        verbose_name = _('HEP-SPEC06 run')
        verbose_name_plural = _('HEP-SPEC06 runs')

    def __unicode__(self):
        return "{hw_conf} / {nb_workers} — {score} — {active_energy}".format(
            hw_conf=self.system_configuration.hardware_configuration.name,
            nb_workers=self.nb_workers,
            score=self.score,
            active_energy=self.active_energy,
        )

    system_configuration = models.ForeignKey(
        SystemConfiguration,
        on_delete=models.CASCADE,
        related_name='%(app_label)s_%(class)s'
    )
    nb_workers = models.IntegerField()
    score = models.DecimalField(max_digits=8, decimal_places=2)
    active_energy = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True
    )
    apparent_energy = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True
    )


class SSDBenchmark(models.Model):
    class Meta:
        abstract = True

    ssd = models.ForeignKey(
        SSD,
        on_delete=models.CASCADE,
        related_name='%(app_label)s_%(class)s'
    )

    # Test Bench Specifications
    os = models.ForeignKey(
        OS,
        on_delete=models.SET_NULL,
        related_name='%(app_label)s_%(class)s',
        verbose_name='test bench OS',
        null=True,
        blank=True
    )
    cpu = models.ForeignKey(
        CPU,
        on_delete=models.SET_NULL,
        related_name='%(app_label)s_%(class)s',
        verbose_name='test bench cpu',
        null=True,
        blank=True
    )
    kernel = models.ForeignKey(
        LinuxKernel,
        on_delete=models.SET_NULL,
        related_name='%(app_label)s_%(class)s',
        verbose_name='test bench Linux kernel',
        null=True,
        blank=True
    )


class SSDBenchL2(SSDBenchmark):
    UNDEFINED = 0
    SEQUENTIAL = 1
    RANDOM = 2
    ACCESS_TYPE_CHOICES = (
        (SEQUENTIAL, 'Sequential'),
        (RANDOM, 'Random'),
    )

    class Meta:
        verbose_name = _("ssdbench_l2 run")
        verbose_name_plural = _("ssdbench_l2 runs")

    @staticmethod
    def import_access_type(read_arg):
        if read_arg == "Seq":
            return SSDBenchL2.SEQUENTIAL
        if read_arg == "Rand":
            return SSDBenchL2.RANDOM
        return SSDBenchL2.UNDEFINED

    def __unicode__(self):
        return "{ssd} - {test_description} - {access_type} - {percent_write} - {block_size} - {threads} - {qd_per_thread}".format(
            ssd=self.ssd,
            test_description=self.test_description,
            access_type=self.access_type,
            percent_write=self.percent_write,
            block_size=self.block_size,
            threads=self.threads,
            qd_per_thread=self.qd_per_thread
        )

    percent_capacity_used = models.IntegerField(
        default=100,
        validators=[MaxValueValidator(100), MinValueValidator(0)]
    )
    access_type = models.IntegerField(
        choices=ACCESS_TYPE_CHOICES,
        default=SEQUENTIAL
    )
    percent_write = models.IntegerField(
        default=100,
        validators=[MaxValueValidator(100), MinValueValidator(0)]
    )
    block_size = models.IntegerField()
    threads = models.IntegerField(default=1)
    qd_per_thread = models.IntegerField(default=1)
    iops = models.IntegerField()
    throughput = models.IntegerField()
    read_latency = models.DecimalField(
        max_digits=20,
        decimal_places=10,
        blank=True,
        null=True
    )
    write_latency = models.DecimalField(
        max_digits=20,
        decimal_places=10,
        blank=True,
        null=True
    )
    test_description = models.CharField(max_length=1024)

    comment = models.CharField(max_length=1024, blank=True, null=True)


class SSDBenchL2Stability(SSDBenchmark):
    class Meta:
        verbose_name = _("ssdbench_l2 IOPS stability run")
        verbose_name_plural = _("ssdbench_l2 IOPS stability runs")

    def __unicode__(self):
        return "{} iops stability test".format(self.ssd)

    iops = ArrayField(models.IntegerField(), verbose_name="IOPS per second")


class SSDBenchL3Base(SSDBenchmark):
    rdmbps = models.DecimalField(
        max_digits=30,
        decimal_places=10,
        verbose_name="read speed (MB/s)"
    )
    wrmbps = models.DecimalField(
        max_digits=30,
        decimal_places=10,
        verbose_name="write speed (MB/s)"
    )
    rdiops = models.IntegerField(verbose_name="read IOPS")
    wriops = models.IntegerField(verbose_name="write IOPS")


class SSDBenchL3Analytics(SSDBenchL3Base):
    class Meta:
        verbose_name = _("ssdbench_l3 analytics run")
        verbose_name_plural = _("ssdbench_l3 analytics runs")

    def __unicode__(self):
        return "{} ssdbench_l3 analytics - {} rd IOPS / {} wr IOPS - {} rd MB/s / {} wr MB/s".format(self.ssd, self.rdmbps, self.wrmbps, self.rdiops, self.wriops)


class SSDBenchL3Checkpointing(SSDBenchL3Base):
    class Meta:
        verbose_name = _("ssdbench_l3 checkpointing run")
        verbose_name_plural = _("ssdbench_l3 checkpointing runs")

    def __unicode__(self):
        return "{} ssdbench_l3 checkpointing - {} rd IOPS / {} wr IOPS - {} rd MB/s / {} wr MB/s".format(self.ssd, self.rdmbps, self.wrmbps, self.rdiops, self.wriops)


class SSDBenchL3HFT(SSDBenchL3Base):
    class Meta:
        verbose_name = _("ssdbench_l3 HFT run")
        verbose_name_plural = _("ssdbench_l3 HFT runs")

    def __unicode__(self):
        return "{} ssdbench_l3 HFT - {} rd IOPS / {} wr IOPS - {} rd MB/s / {} wr MB/s".format(self.ssd, self.rdmbps, self.wrmbps, self.rdiops, self.wriops)


class SSDBenchL3Db8kpage(SSDBenchL3Base):
    class Meta:
        verbose_name = _("ssdbench_l3 db8kpage run")
        verbose_name_plural = _("ssdbench_l3 db8kpage runs")

    def __unicode__(self):
        return "{} ssdbench_l3 db8kpage - {} rd IOPS / {} wr IOPS - {} rd MB/s / {} wr MB/s".format(self.ssd, self.rdmbps, self.wrmbps, self.rdiops, self.wriops)


class SSDBenchL3BigBlock(SSDBenchL3Base):
    class Meta:
        verbose_name = _("ssdbench_l3 bigblock run")
        verbose_name_plural = _("ssdbench_l3 bigblock runs")

    def __unicode__(self):
        return "{} ssdbench_l3 bigblock - {} rd IOPS / {} wr IOPS - {} rd MB/s / {} wr MB/s".format(self.ssd, self.rdmbps, self.wrmbps, self.rdiops, self.wriops)


class SSDBenchL3OLTP(SSDBenchmark):
    class Meta:
        verbose_name = _("ssdbench_l3 OLTP run")
        verbose_name_plural = _("ssdbench_l3 OLTP runs")

    def __unicode__(self):
        return "{} ssdbench_l3 OLTP - {} p99rd? / {} p99wr?".format(
            self.ssd,
            self.p99rd,
            self.p99wr
        )

    p99rd = models.IntegerField()
    p99wr = models.IntegerField()


class SSDBenchL3Metadata(SSDBenchmark):
    class Meta:
        verbose_name = _("ssdbench_l3 metadata run")
        verbose_name_plural = _("ssdbench_l3 metadata runs")

    def __unicode__(self):
        return "{} ssdbench_l3 metadata - {} file creations / {} file deletions".format(self.ssd, self.creation, self.deletion)

    creation = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="average file creations per second"
    )
    deletion = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="average file deletions per second"
    )
