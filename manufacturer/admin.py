from django.contrib import admin

from bulk_admin import BulkModelAdmin

from .models import Manufacturer


@admin.register(Manufacturer)
class ManufacturerAdmin(BulkModelAdmin):
    pass
