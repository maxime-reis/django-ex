from django.contrib import admin

from bulk_admin import BulkModelAdmin

from .models import OS, LinuxKernel


@admin.register(OS)
class OSAdmin(BulkModelAdmin):
    pass


@admin.register(LinuxKernel)
class LinuxKernelAdmin(BulkModelAdmin):
    pass
