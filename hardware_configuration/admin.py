from django.contrib import admin

from bulk_admin import BulkModelAdmin

from .models import CPU, Architecture


@admin.register(CPU)
class CPUAdmin(BulkModelAdmin):
    pass


@admin.register(Architecture)
class ArchitectureAdmin(BulkModelAdmin):
    pass
