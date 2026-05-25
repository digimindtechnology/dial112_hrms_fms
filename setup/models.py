import random
import string
from django.db import models
from django.contrib.auth.models import User
from masters.models import BaseModel, State, Division, District, Zone,City
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


class SetupLookupBase(BaseModel):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    tenantProfile = models.ForeignKey(TenantProfile, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='%(class)s_created')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='%(class)s_updated')

    class Meta:
        abstract = True
        ordering = ('name',)

    def __str__(self):
        return self.name


class EmployeeType(SetupLookupBase):
    class Meta(SetupLookupBase.Meta):
        verbose_name = 'Employee Type'
        verbose_name_plural = 'Employee Types'
        constraints = [
            models.UniqueConstraint(fields=['tenantProfile', 'name'], name='setup_employee_type_tenant_name_uniq')
        ]


class Designation(SetupLookupBase):
    class Meta(SetupLookupBase.Meta):
        verbose_name = 'Designation'
        verbose_name_plural = 'Designations'
        constraints = [
            models.UniqueConstraint(fields=['tenantProfile', 'name'], name='setup_designation_tenant_name_uniq')
        ]


class Grade(SetupLookupBase):
    class Meta(SetupLookupBase.Meta):
        verbose_name = 'Grade'
        verbose_name_plural = 'Grades'
        constraints = [
            models.UniqueConstraint(fields=['tenantProfile', 'name'], name='setup_grade_tenant_name_uniq')
        ]


class Language(SetupLookupBase):
    class Meta(SetupLookupBase.Meta):
        verbose_name = 'Language'
        verbose_name_plural = 'Languages'
        constraints = [
            models.UniqueConstraint(fields=['tenantProfile', 'name'], name='setup_language_tenant_name_uniq')
        ]


class Dialect(SetupLookupBase):
    class Meta(SetupLookupBase.Meta):
        verbose_name = 'Dialect'
        verbose_name_plural = 'Dialects'
        constraints = [
            models.UniqueConstraint(fields=['tenantProfile', 'name'], name='setup_dialect_tenant_name_uniq')
        ]


class LeaveType(SetupLookupBase):
    class Meta(SetupLookupBase.Meta):
        verbose_name = 'Leave Type'
        verbose_name_plural = 'Leave Types'
        constraints = [
            models.UniqueConstraint(fields=['tenantProfile', 'name'], name='setup_leave_type_tenant_name_uniq')
        ]


class ShiftCategory(SetupLookupBase):
    how_many_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    class Meta(SetupLookupBase.Meta):
        verbose_name = 'Shift Category'
        verbose_name_plural = 'Shift Categories'
        constraints = [
            models.UniqueConstraint(fields=['tenantProfile', 'name'], name='setup_shift_category_tenant_name_uniq')
        ]


class ViolationType(SetupLookupBase):
    class Meta(SetupLookupBase.Meta):
        verbose_name = 'Violation Type'
        verbose_name_plural = 'Violation Types'
        constraints = [
            models.UniqueConstraint(fields=['tenantProfile', 'name'], name='setup_violation_type_tenant_name_uniq')
        ]


class TrainerType(SetupLookupBase):
    class Meta(SetupLookupBase.Meta):
        verbose_name = 'Trainer Type'
        verbose_name_plural = 'Trainer Types'
        constraints = [
            models.UniqueConstraint(fields=['tenantProfile', 'name'], name='setup_trainer_type_tenant_name_uniq')
        ]


class FRVType(SetupLookupBase):
    class Meta(SetupLookupBase.Meta):
        verbose_name = 'FRV Type'
        verbose_name_plural = 'FRV Types'
        constraints = [
            models.UniqueConstraint(fields=['tenantProfile', 'name'], name='setup_frv_type_tenant_name_uniq')
        ]

class FRVMaintenanceType(SetupLookupBase):
    class Meta(SetupLookupBase.Meta):
        verbose_name = 'FRV Maintenance Type'
        verbose_name_plural = 'FRV Maintenance Types'
        constraints = [
            models.UniqueConstraint(fields=['tenantProfile', 'name'], name='setup_frv_maintenance_type_tenant_name_uniq')
        ]


class PoliceStation(BaseModel):
    police_station_id = models.AutoField(primary_key=True)
    police_station_name = models.CharField(max_length=500)
    station_code = models.CharField(max_length=50, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    state = models.ForeignKey(State, related_name='state_PoliceStation', on_delete=models.CASCADE, verbose_name="State") ##Remove
    division = models.ForeignKey(Division, related_name='division_PoliceStation', on_delete=models.CASCADE, verbose_name="Division")  ##Remove
    district = models.ForeignKey(District, related_name='district_PoliceStation', on_delete=models.CASCADE, verbose_name="District")
    zone = models.ForeignKey(Zone,blank=True, null=True, related_name='zone_PoliceStation', on_delete=models.CASCADE, verbose_name="Zone")  ##Remove
    City = models.ForeignKey(City,blank=True, null=True, related_name='City_PoliceStation', on_delete=models.CASCADE, verbose_name="City")  ##Remove
    address = models.TextField(null=True, blank=True)
    pincode = models.CharField(max_length=10,null=True, blank=True)
    picture_url = models.CharField(max_length=1000, null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    established_date = models.DateField(blank=True, null=True)
    tenantProfile = models.ForeignKey(TenantProfile, related_name='tenantProfile_PoliceStation', on_delete=models.CASCADE, verbose_name="Tenant")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_by_PoliceStation")
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="updated_by_PoliceStation")
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'police_station'
        ordering = ['police_station_name']

    def __str__(self):
        return self.police_station_name

class Holiday(BaseModel):
    holiday_id = models.AutoField(primary_key=True)
    holiday_name = models.CharField(max_length=500)
    holiday_date = models.DateField()
    description = models.TextField(blank=True, null=True)
    is_national_holiday = models.BooleanField(default=False)
    tenantProfile = models.ForeignKey(TenantProfile, related_name='tenantProfile_Holiday', on_delete=models.CASCADE, verbose_name="Tenant")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE,related_name="created_by_Holiday")
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True,related_name="updated_by_Holiday")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['holiday_date']
        verbose_name = "Holiday"
        verbose_name_plural = "Holidays"
    def __str__(self):
        return f"{self.holiday_name} - {self.holiday_date}"

##add Holiday  distict wise SS