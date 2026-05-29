from django.contrib import admin
from setup.models import CostCenterStatus, CostCenterBulkUploadHistory, CostCenter, FRVType

admin.site.register(CostCenterStatus)
admin.site.register(CostCenter)
admin.site.register(CostCenterBulkUploadHistory)

class FRVTypeAdmin(admin.ModelAdmin):
    model = FRVType
    list_display = ('__str__','is_active',)
    list_filter = (
        ('is_active', admin.BooleanFieldListFilter),
    )
admin.site.register(FRVType,FRVTypeAdmin)
