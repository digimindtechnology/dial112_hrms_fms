import random
import string
from django.db import models
from django.contrib.auth.models import User
from masters.models import BaseModel
from tenant.models import TenantProfile


class CostCenterStatus(models.Model):
    cost_center_status_id = models.AutoField(primary_key=True)
    cost_center_status_name = models.CharField(max_length=500)
    cost_center_status_css = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.cost_center_status_name


class CostCenterBulkUploadHistory(models.Model):
    upload_history_id = models.AutoField(primary_key=True)
    file_name = models.CharField(max_length=1000)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='uploaded_cost_center_files')
    uploaded_on = models.DateTimeField(auto_now_add=True)
    total_records = models.IntegerField(default=0)
    processed_records = models.IntegerField(default=0)
    failed_records = models.IntegerField(default=0)
    pending_records = models.IntegerField(default=0)

    status = models.ForeignKey(CostCenterStatus, default=1, on_delete=models.CASCADE,
                               related_name='cost_center_upload_status')
    remarks = models.TextField(null=True, blank=True)
    tenantProfile = models.ForeignKey(TenantProfile, on_delete=models.CASCADE,
                                      related_name='tenant_cost_center_upload_history')
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-uploaded_on']

    def __str__(self):
        return self.file_name


def generate_unique_code():
    while True:
        code = ''.join(random.choices(string.digits, k=8))
        if not CostCenter.objects.filter(cost_center_code=code).exists():
            return code


class CostCenter(BaseModel):
    cost_center_id = models.AutoField(primary_key=True)
    cost_center_name = models.CharField(max_length=1000)
    cost_center_code = models.CharField(max_length=8, unique=True, default=generate_unique_code)
    description = models.TextField(null=True, blank=True)
    tenantProfile = models.ForeignKey(TenantProfile, related_name='tenant_cost_CostCenter', on_delete=models.CASCADE,
                                      verbose_name='Company')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_cost_CostCenter')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='updated_cost_CostCenter')
    costCenterBulkUpload = models.ForeignKey(CostCenterBulkUploadHistory, on_delete=models.SET_NULL, null=True,
                                             blank=True, related_name='costCenterBulkUpload_cost_centers')
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ('cost_center_name',)

    def __str__(self):
        return f"{self.cost_center_name} ({self.cost_center_code})"
