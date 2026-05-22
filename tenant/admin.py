from django.contrib import admin
from tenant.models import TenantProfile, TimeZone, DateFormat, TimeFormat, Role


admin.site.register(TenantProfile)
admin.site.register(TimeZone)
admin.site.register(DateFormat)
admin.site.register(TimeFormat)
@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('role_name', 'tenantProfile__tenant_name', 'get_assigned_group_name', 'is_active',)
    search_fields = ('role_name', 'tenantProfile__tenant_name')
    list_filter = ('is_active',)
    filter_horizontal = ('group',)
