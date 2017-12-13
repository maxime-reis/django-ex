from django.contrib import admin

import bulk_admin

from .models import (
    HEPSPEC06Run, SSDBenchL2, SSDBenchL2Stability, SSDBenchL3Analytics,
    SSDBenchL3Checkpointing, SSDBenchL3HFT, SSDBenchL3Db8kpage,
    SSDBenchL3BigBlock, SSDBenchL3OLTP, SSDBenchL3Metadata
)


@admin.register(HEPSPEC06Run)
class HEPSPEC06RunAdmin(bulk_admin.BulkModelAdmin):
    pass


@admin.register(SSDBenchL2)
class SSDBenchL2Admin(bulk_admin.BulkModelAdmin):
    pass


@admin.register(SSDBenchL2Stability)
class SSDBenchL2StabilityAdmin(bulk_admin.BulkModelAdmin):
    pass


@admin.register(SSDBenchL3Analytics)
class SSDBenchL3AnalyticsAdmin(bulk_admin.BulkModelAdmin):
    pass


@admin.register(SSDBenchL3Checkpointing)
class SSDBenchL3CheckpointingAdmin(bulk_admin.BulkModelAdmin):
    pass


@admin.register(SSDBenchL3HFT)
class SSDBenchL3HFTAdmin(bulk_admin.BulkModelAdmin):
    pass


@admin.register(SSDBenchL3Db8kpage)
class SSDBenchL3Db8kpageAdmin(bulk_admin.BulkModelAdmin):
    pass


@admin.register(SSDBenchL3BigBlock)
class SSDBenchL3BigBlockAdmin(bulk_admin.BulkModelAdmin):
    pass


@admin.register(SSDBenchL3OLTP)
class SSDBenchL3OLTPAdmin(bulk_admin.BulkModelAdmin):
    pass


@admin.register(SSDBenchL3Metadata)
class SSDBenchL3MetadataAdmin(bulk_admin.BulkModelAdmin):
    pass
