from django.contrib import admin

from bulk_admin import BulkModelAdmin

from guardian.admin import GuardedModelAdmin
from hardwarelabs_core.admin import GuardedModelAdminMod

from .models import (
    SSD, SSDFormFactor, SSDInterface, SSDFlashType, SSDProcessSize,
    SSDController, SSDSeries
)


@admin.register(SSD)
class SSDAdmin(GuardedModelAdminMod, BulkModelAdmin):
    pass


@admin.register(SSDFormFactor)
class SSDFormFactorAdmin(BulkModelAdmin):
    pass


@admin.register(SSDInterface)
class SSDInterfaceAdmin(BulkModelAdmin):
    pass


@admin.register(SSDFlashType)
class SSDFlashTypeAdmin(BulkModelAdmin):
    pass


@admin.register(SSDProcessSize)
class SSDProcessSizeAdmin(BulkModelAdmin):
    pass


@admin.register(SSDController)
class SSDControllerAdmin(BulkModelAdmin):
    pass


@admin.register(SSDSeries)
class SSDSeriesAdmin(BulkModelAdmin):
    pass
