from django.contrib import admin
from setup.models import CostCenterStatus, CostCenterBulkUploadHistory, CostCenter

admin.site.register(CostCenterStatus)
admin.site.register(CostCenter)
admin.site.register(CostCenterBulkUploadHistory)
