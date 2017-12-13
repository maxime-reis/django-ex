from django.contrib import admin
from bulk_admin import BulkModelAdmin
from guardian.admin import GuardedModelAdmin

from hardwarelabs_core.admin import GuardedModelAdminMod

from .models import (
    Node, HardwareConfiguration, SoftwareConfiguration, OS, Architecture,
    Alias, SystemConfiguration, SSD, Manufacturer, SSDFormFactor, SSDInterface,
    SSDFlashType, SSDProcessSize, SSDController, SSDSeries
)


class AliasInline(admin.TabularInline):
    model = Alias
    extra = 1


@admin.register(Node)
class NodeAdmin(BulkModelAdmin):
    inlines = [
        AliasInline,
    ]


@admin.register(Alias)
class AliasAdmin(BulkModelAdmin):
    pass


@admin.register(OS)
class OSAdmin(BulkModelAdmin):
    pass


@admin.register(SoftwareConfiguration)
class SoftwareConfigurationAdmin(BulkModelAdmin):
    pass


@admin.register(HardwareConfiguration)
class HardwareConfigurationAdmin(GuardedModelAdminMod, BulkModelAdmin):
    pass


@admin.register(SystemConfiguration)
class SystemConfigurationAdmin(BulkModelAdmin):
    pass
