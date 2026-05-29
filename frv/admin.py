from django.contrib import admin
from frv.models import FuelType, VehicleStatus

class VehicleStatusAdmin(admin.ModelAdmin):
    model = VehicleStatus
    list_display = ('__str__','is_active',)
    list_filter = (
        ('is_active', admin.BooleanFieldListFilter),
    )
admin.site.register(VehicleStatus,VehicleStatusAdmin)

class FuelTypeAdmin(admin.ModelAdmin):
    model = FuelType
    list_display = ('__str__','is_active',)
    list_filter = (
        ('is_active', admin.BooleanFieldListFilter),
    )
admin.site.register(FuelType,FuelTypeAdmin)