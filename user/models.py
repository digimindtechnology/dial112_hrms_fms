from django.db import models
from django.contrib.auth.models import User
from masters.models import District
from tenant.models import TenantProfile


class UserDistrictMapping(models.Model):
    user_district_mapping_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_district_mappings')
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='district_user_mappings')
    tenantProfile = models.ForeignKey(TenantProfile, on_delete=models.CASCADE, related_name='tenant_user_district_mappings')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_user_district_mappings')
    created_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = [['user', 'district', 'tenantProfile']]
        ordering = ('district__district_name',)
        verbose_name = 'User District Mapping'
        verbose_name_plural = 'User District Mappings'

    def __str__(self):
        return f"{self.user.username} - {self.district.district_name}"
