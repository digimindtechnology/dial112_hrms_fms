import uuid

from django.db import models
from django.contrib.auth.models import User, Group
from django.utils import timezone
from masters.models import BaseModel, District
from setup.models import FRVType, PoliceStation, ShiftCategory, ViolationType
from tenant.models import TenantProfile


# ==================== ABSTRACT BASE CLASS ====================

class MaintenanceType(models.Model):
    """Maintenance Type - Preventive, Breakdown, Scheduled, Accident Repair, Emergency, Periodic"""
    id = models.AutoField(primary_key=True)
    maintenance_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ('maintenance_name',)

    def __str__(self):
        return self.maintenance_name

class MaintenancePriority(models.Model):
    """Maintenance Priority - Low, Medium, High, Critical"""
    id = models.AutoField(primary_key=True)
    priority_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ('priority_name',)

    def __str__(self):
        return self.priority_name
   
class MaintenanceStatus(models.Model):
    """Maintenance Status - Scheduled, In Progress, Completed, Cancelled, Delayed"""
    id = models.AutoField(primary_key=True)
    status_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ('status_name',)

    def __str__(self):
        return self.status_name


class HandoverTakeoverStatus(models.Model):
    """Handover/Takeover Status - Pending, Completed"""
    id = models.AutoField(primary_key=True)
    status_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ('status_name',)

    def __str__(self):
        return self.status_name

class AccidentType(models.Model):
    """Accident Type - Minor, Major, Fatal, Property Damage"""
    id = models.AutoField(primary_key=True)
    accident_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ('accident_name',)

    def __str__(self):
        return self.accident_name

class GuidelineCategory(models.Model):
    """Guideline Category - Operations, Maintenance, Safety, Emergency, Other"""
    id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ('category_name',)

    def __str__(self):
        return self.category_name

class FuelType(models.Model): # Add in SuperUser
    """Fuel Type - Petrol, Diesel, CNG, EV"""
    id = models.AutoField(primary_key=True)
    fuel_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ('fuel_name',)

    def __str__(self):
        return self.fuel_name


class VehicleStatus(models.Model):
    """Vehicle Status - On Road, Off Road, Under Repair, Accident, Decommissioned"""
    id = models.AutoField(primary_key=True)
    status_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ('status_name',)

    def __str__(self):
        return self.status_name
    
class FRVServiceCenter(BaseModel):
    """List of Authorized Service Centers"""
    frv_service_center_id = models.AutoField(primary_key=True)
    frv_service_center_unique_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    server_center_name = models.CharField(max_length=200)
    
    address = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=100)
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, related_name='district_FRVServiceCenter')
    state = models.CharField(max_length=100,null=True, blank=True)
    pincode = models.CharField(max_length=10,null=True, blank=True)
    
    contact_person = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=20,null=True, blank=True,)
    email = models.EmailField(blank=True)
    
    tenantProfile = models.ForeignKey(TenantProfile, on_delete=models.CASCADE, related_name='tenantProfile_FRVServiceCenter')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_by_FRVServiceCenter')
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='updated_by_FRVServiceCenter')
    
    class Meta:
        indexes = [
            models.Index(fields=['tenantProfile']),
            models.Index(fields=['server_center_name']),
        ]
    
    def __str__(self):
        return f"{self.server_center_name} - {self.city}"

class FRVInspectionCheckList(BaseModel):
    """FRV Inspection Check List"""
    frv_inspection_checklist_id = models.AutoField(primary_key=True)
    checklist_item = models.CharField(max_length=255)
    is_checked = models.BooleanField(default=False)

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_by_FRVInspectionCheckList")
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="updated_by_FRVInspectionCheckList")

    class Meta:
        ordering = ['checklist_item']

        verbose_name = 'FRV Inspection Checklist'
        verbose_name_plural = 'FRV Inspection Checklists'

    def __str__(self):
        return self.checklist_item

class FRVGuideline(BaseModel):
    """FRV Operating Guidelines & Manuals"""
    frv_guideline_id = models.AutoField(primary_key=True)
    frv_guideline_unique_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    category = models.ForeignKey(GuidelineCategory, on_delete=models.SET_NULL, null=True,related_name='category_FRVGuideline')
    
    document_file = models.CharField(max_length=100, null=True, blank=True)
    version = models.CharField(max_length=20)
    effective_date = models.DateField()
    
    tenantProfile = models.ForeignKey(TenantProfile, on_delete=models.CASCADE, related_name='tenantProfile_FRVGuideline')

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_by_FRVGuideline')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_by_FRVGuideline')
    
    class Meta:
        indexes = [
            models.Index(fields=['tenantProfile']),
        ]
    
    def __str__(self):
        return f"{self.title} - v{self.version}"


# ==================== MAIN MODELS ====================

class FRV(BaseModel):
    """Main FRV/Vehicle Master Table"""
    frv_id = models.AutoField(primary_key=True)
    frv_unique_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    vehicle_id = models.CharField(max_length=50, unique=True, help_text="FRV Identifier/Registration Number")
    
    registration_number = models.CharField(max_length=50, unique=True)
    registration_date = models.DateField(blank=True, null=True)
    registration_valid_upto = models.DateField(blank=True, null=True)

    chassis_number = models.CharField(max_length=50, blank=True, null=True)
    engine_number = models.CharField(max_length=50, blank=True, null=True)
    
    # Foreign keys to lookup tables (instead of TextChoices)
    frvType = models.ForeignKey(FRVType, on_delete=models.SET_NULL, null=True, related_name='frvType_FRV')
    
    make = models.CharField(max_length=100,blank=True, null=True, help_text="Manufacturer/Brand")
    model = models.CharField(max_length=100,blank=True, null=True, help_text="Model/Variant")
    year_of_manufacture = models.IntegerField(blank=True, null=True, help_text="Year of Manufacture")
    
    fuelType = models.ForeignKey(FuelType, on_delete=models.SET_NULL, null=True, related_name='fuelType_FRV')
    engine_cc = models.CharField(max_length=20, blank=True)
    seating_capacity = models.IntegerField(default=4, blank=True, null=True)
    
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, related_name='district_FRV')
    policeStation = models.ForeignKey(PoliceStation, on_delete=models.SET_NULL, null=True, blank=True, related_name='policeStation_FRV')
    status = models.ForeignKey(VehicleStatus, on_delete=models.SET_NULL, null=True, related_name='status_FRV')
    
    insurance_policy_number = models.CharField(max_length=100, blank=True)
    insurance_valid_upto = models.DateField(null=True, blank=True)
    pollution_certificate_valid_upto = models.DateField(null=True, blank=True)
    fitness_certificate_valid_upto = models.DateField(null=True, blank=True)

    frv_images = models.JSONField(default=dict, blank=True, help_text="Store vehicle images with metadata")
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_by_FRV")
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="updated_by_FRV")
    
    # Tenant
    tenantProfile = models.ForeignKey(TenantProfile, on_delete=models.CASCADE, related_name='tenantProfile_FRV')
    
    class Meta:
        ordering = ['frv_id']
        indexes = [
            models.Index(fields=['registration_number']),
            models.Index(fields=['district', 'status']),
            models.Index(fields=['status']),
            models.Index(fields=['tenantProfile']),
        ]
    
    def __str__(self):
        return f"{self.vehicle_id} - {self.registration_number}"


class FRVTakeoverhandover(models.Model):
    """FRV Handover/Takeover Logs with Odometer Readings & 4-Side Images"""
    frv_handover_takeover_id = models.AutoField(primary_key=True)
    frv_handover_takeover_unique_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    frv = models.ForeignKey(FRV, on_delete=models.CASCADE, related_name='frv_FRVTakeoverhandover')

    # ========== Takeover Details ==========
    takeover_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='takeover_by_FRVTakeoverhandover')
    takeover_odometer = models.DecimalField(max_digits=12, decimal_places=2)
    takeover_fuel_level = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    takeover_time = models.DateTimeField(auto_now_add=True)
    
    # Takeover - 4 Side Images (Front, Rear, LHS, RHS)
    takeover_front_image = models.CharField(max_length=1000, null=True, blank=True, help_text="FRV Front view image URL")
    takeover_rear_image = models.CharField(max_length=1000, null=True, blank=True, help_text="FRV Rear view image URL")
    takeover_lhs_image = models.CharField(max_length=1000, null=True, blank=True, help_text="FRV Left Hand Side image URL")
    takeover_rhs_image = models.CharField(max_length=1000, null=True, blank=True, help_text="FRV Right Hand Side image URL")
    
    # Takeover - Additional Images
    takeover_flashing_lights_image = models.CharField(max_length=1000, null=True, blank=True, help_text="Flashing lights working condition image URL")
    takeover_interior_condition_image = models.CharField(max_length=1000, null=True, blank=True, help_text="Interior condition image URL")
    takeover_odometer_image = models.CharField(max_length=1000, null=True, blank=True, help_text="Odometer reading image URL")
    takeover_vehicle_condition_image = models.CharField(max_length=1000, null=True, blank=True, help_text="Overall vehicle condition image URL")
    
    takeover_remarks = models.TextField(blank=True)
    
    # ========== Handover Details ==========
    handover_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='handover_by_FRVTakeoverhandover')
    handover_odometer = models.DecimalField(max_digits=12, decimal_places=2, null = True, blank = True, help_text="Odometer reading at handover")
    handover_fuel_level = models.DecimalField(max_digits=5, decimal_places=2, null = True, blank = True, help_text="Fuel level in liters or percentage")
    handover_time = models.DateTimeField(null = True, blank = True)

    # Handover - 4 Side Images (Front, Rear, LHS, RHS)
    handover_front_image = models.CharField(max_length=1000, null=True, blank=True, help_text="FRV Front view image URL")
    handover_rear_image = models.CharField(max_length=1000, null=True, blank=True, help_text="FRV Rear view image URL")
    handover_lhs_image = models.CharField(max_length=1000, null=True, blank=True, help_text="FRV Left Hand Side image URL")
    handover_rhs_image = models.CharField(max_length=1000, null=True, blank=True, help_text="FRV Right Hand Side image URL")
    
    # Handover - Additional Images
    handover_flashing_lights_image = models.CharField(max_length=1000, null=True, blank=True, help_text="Flashing lights working condition image URL")
    handover_interior_condition_image = models.CharField(max_length=1000, null=True, blank=True, help_text="Interior condition image URL")
    handover_odometer_image = models.CharField(max_length=1000, null=True, blank=True, help_text="Odometer reading image URL")
    handover_vehicle_condition_image = models.CharField(max_length=1000, null=True, blank=True, help_text="Overall vehicle condition image URL")
    
    handover_remarks = models.TextField(blank=True)
    
    # ========== Calculated Fields ==========
    distance_traveled = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    fuel_consumed = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    
    # ========== Shift & Status ==========
    shiftCategory = models.ForeignKey(ShiftCategory, on_delete=models.SET_NULL, related_name='shiftCategory_FRVTakeoverhandover', null=True)
    status = models.ForeignKey(HandoverTakeoverStatus, on_delete=models.SET_NULL, null=True, related_name='status_FRVTakeoverhandover')
    
    # ========== Audit Fields ==========
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_by_FRVTakeoverhandover')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_by_FRVTakeoverhandover')

    class Meta:
        ordering = ['-takeover_time']
        verbose_name = 'FRV Takeover Handover'
        verbose_name_plural = 'FRV Takeover Handovers'
    
    def save(self, *args, **kwargs):
        # Calculate distance traveled
        if self.handover_odometer and self.takeover_odometer:
            self.distance_traveled = self.handover_odometer - self.takeover_odometer
        
        # Calculate fuel consumed
        if self.takeover_fuel_level and self.handover_fuel_level:
            self.fuel_consumed = self.takeover_fuel_level - self.handover_fuel_level
        
        super().save(*args, **kwargs)

    @property
    def takeover_images(self):
        """Return all takeover images as a dictionary"""
        return {
            'front': self.takeover_front_image,
            'rear': self.takeover_rear_image,
            'lhs': self.takeover_lhs_image,
            'rhs': self.takeover_rhs_image,
            'flashing_lights': self.takeover_flashing_lights_image,
            'interior': self.takeover_interior_condition_image,
            'odometer': self.takeover_odometer_image,
            'condition': self.takeover_vehicle_condition_image,
        }
    
    @property
    def handover_images(self):
        """Return all handover images as a dictionary"""
        return {
            'front': self.handover_front_image,
            'rear': self.handover_rear_image,
            'lhs': self.handover_lhs_image,
            'rhs': self.handover_rhs_image,
            'flashing_lights': self.handover_flashing_lights_image,
            'interior': self.handover_interior_condition_image,
            'odometer': self.handover_odometer_image,
            'condition': self.handover_vehicle_condition_image,
        }
    
    def __str__(self):
        return f"FRV {self.frv.vehicle_id} - Takeover: {self.takeover_time} - Handover: {self.handover_time or 'Pending'}"


class FRVMaintenance(BaseModel):
    """Vehicle Maintenance Records (Service Book)"""
    frv_maintenance_id = models.AutoField(primary_key=True)
    frv_maintenance_unique_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    frv = models.ForeignKey(FRV, on_delete=models.CASCADE, related_name='frv_FRVMaintenance')
    
    maintenanceType = models.ForeignKey(MaintenanceType, on_delete=models.SET_NULL, null=True, related_name='maintenanceType_FRVMaintenance')
    priority = models.ForeignKey(MaintenancePriority, on_delete=models.SET_NULL, null=True, related_name='priority_FRVMaintenance')

    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    
    odometer_at_maintenance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    scheduled_date = models.DateField(null=True, blank=True)
    actual_date = models.DateField(null=True, blank=True)
    
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    actual_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    serviceCenter = models.ForeignKey(FRVServiceCenter, on_delete=models.SET_NULL, null=True, blank=True, related_name='serviceCenter_FRVMaintenance')
    invoice_number = models.CharField(max_length=100, blank=True)
    parts_replaced = models.TextField(help_text="List of parts replaced with details",null=True, blank=True)
    
    status = models.ForeignKey(MaintenanceStatus, on_delete=models.SET_NULL, null=True, related_name='status_FRVMaintenance')
    
    maintenance_images = models.JSONField(default=dict, null=True, blank=True, help_text="Images of maintenance/repair work")
    documents = models.JSONField(default=dict, null=True, blank=True, help_text="Invoices, bills, etc.")
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_by_FRVMaintenance")
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="updated_by_FRVMaintenance")
    
    class Meta:
        ordering = ['-scheduled_date']
        indexes = [
            models.Index(fields=['frv', 'status']),
            models.Index(fields=['scheduled_date']),
        ]
    
    def __str__(self):
        return f"{self.frv.vehicle_id} - {self.maintenanceType} - {self.scheduled_date}"


class FRVInspection(BaseModel):
    """Periodic Vehicle Inspection Reports (Weekly minimum)"""
    frv_inspection_id = models.AutoField(primary_key=True)
    frv_inspection_unique_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    frv = models.ForeignKey(FRV, on_delete=models.CASCADE, related_name='frv_FRVInspection')
    
    inspection_date = models.DateField(auto_now_add=True)
    inspected_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='inspected_by_FRVInspection')
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_by_FRVInspection")
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="updated_by_FRVInspection")
    
    class Meta:
        ordering = ['-inspection_date']
        unique_together = [('frv', 'inspection_date')]
        indexes = [
            models.Index(fields=['frv', 'inspection_date']),
        ]

    def __str__(self):
        return f"Inspection - {self.frv.vehicle_id} - {self.inspection_date}"
    


class FRVInspectionCheckListValue(BaseModel):
    """FRV Inspection Values - Detailed inspection metrics"""
    frv_inspection_value_id = models.AutoField(primary_key=True)
    frv_inspection = models.ForeignKey(FRVInspection, on_delete=models.CASCADE, related_name='frv_inspection_FRVInspectionValue')
    frv_inspection_checklist = models.ForeignKey(FRVInspectionCheckList, on_delete=models.CASCADE, related_name='frv_inspection_checklist_FRVInspectionValue')
    is_checked_value = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_by_FRVInspectionValue")
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="updated_by_FRVInspectionValue")
    
    class Meta:
        indexes = [
            models.Index(fields=['frv_inspection']),
        ]

        verbose_name = 'FRV Inspection Value'
        verbose_name_plural = 'FRV Inspection Values'

    def __str__(self):
        return (
            f"Inspection Value - "f"{self.frv_inspection.frv.vehicle_id} - " f"{self.frv_inspection.inspection_date}")


class FRVFuel(BaseModel):
    """Fuel Records Management"""
    frv_fuel_id = models.AutoField(primary_key=True)
    frv_fuel_unique_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    frv = models.ForeignKey(FRV, on_delete=models.CASCADE, related_name='frv_FRVFuel')

    fuel_date = models.DateTimeField()
    fuelType = models.ForeignKey(FuelType, on_delete=models.SET_NULL, null=True, related_name='fuelType_FRVFuel')
    
    quantity_liters = models.DecimalField(max_digits=8, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    
    odometer_reading = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="Odometer at time of refueling")
    refill_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='refill_by_FRVFuel')
    
    fuel_station_name = models.CharField(max_length=200,null=True, blank=True)
    fuel_station_location = models.CharField(max_length=200, blank=True)
    
    receipt_image = models.CharField(max_length=1000, null=True, blank=True, )
    odometer_image = models.CharField(max_length=1000, null=True, blank=True, help_text="Odometer reading image URL")
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_by_FRVFuel")
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="updated_by_FRVFuel")
    
    
    class Meta:
        ordering = ['-fuel_date']
        indexes = [
            models.Index(fields=['frv', 'fuel_date']),
        ]
    
    def save(self, *args, **kwargs):
        if self.quantity_liters and self.unit_price:
            self.total_cost = self.quantity_liters * self.unit_price
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.frv.vehicle_id} - {self.quantity_liters}L - {self.fuel_date}"


class FRVAccident(BaseModel):
    """Accident/Incident Reports"""
    frv_accident_id = models.AutoField(primary_key=True)
    frv_accident_unique_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    frv = models.ForeignKey(FRV, on_delete=models.CASCADE, related_name='frv_FRVAccident')
   
    accident_date = models.DateTimeField(null=True, blank=True)
    accident_location = models.TextField(null=True, blank=True)
    accident_description = models.TextField(null=True, blank=True)
    accidentType = models.ForeignKey(AccidentType, on_delete=models.SET_NULL, null=True, related_name='accidentType_FRVAccident')
    
    driver_at_time = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='driver_at_time_FRVAccident')
    police_at_time = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='police_at_time_FRVAccident')
    other_vehicle_number = models.CharField(max_length=50, null=True, blank=True)
    accident_images = models.JSONField(default=dict, null=True, blank=True, help_text="Accident scene images")
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_by_FRVAccident")
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="updated_by_FRVAccident")
    
    
    class Meta:
        ordering = ['-accident_date']
        indexes = [
            models.Index(fields=['frv', 'accident_date']),
        ]
    
    def __str__(self):
        return f"Accident - {self.frv.vehicle_id} - {self.accident_date}"


class FRVConsumable(BaseModel):
    """Consumables Inventory Tracking"""
    frv_consumable_id = models.AutoField(primary_key=True)
    frv_consumable_unique_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    frv = models.ForeignKey(FRV, on_delete=models.CASCADE, related_name='frv_FRVConsumable')
    consumable_type = models.CharField(max_length=255, null=True, blank=True)
    quantity = models.DecimalField(max_digits=8, decimal_places=2)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='consumable_created')
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='updated_by_FRVConsumable')
    
    def __str__(self):
        return f"{self.frv.vehicle_id} - {self.consumable_type}"
    
class FRVConsumableTransaction(BaseModel):
    """Consumable Usage / Inventory Tracking"""

    frv_consumable_transaction_id = models.AutoField(primary_key=True)
    frv_consumable_transaction_unique_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    frv = models.ForeignKey(FRV,on_delete=models.CASCADE,related_name='frv_FRVConsumableTransaction')

    consumable = models.ForeignKey(FRVConsumable,on_delete=models.CASCADE,related_name='consumable_FRVConsumableTransaction')
    transaction_date = models.DateTimeField(auto_now_add=True)

    quantity = models.DecimalField(max_digits=8,decimal_places=2)
    unit_cost = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    total_cost = models.DecimalField(max_digits=10,decimal_places=2,default=0)

    created_by = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name='created_by_FRVConsumableTransaction')
    updated_by = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True,related_name='updated_by_FRVConsumableTransaction')

    class Meta:
        ordering = ['-transaction_date']

        indexes = [
            models.Index(fields=['frv']),
            models.Index(fields=['consumable']),
        ]

    def save(self, *args, **kwargs):
        self.total_cost = self.quantity * self.unit_cost
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.frv.vehicle_id} - {self.consumable.consumable_name}"


class FRVCodeViolation(BaseModel):
    """Code Violations related to FRV"""
    frv_code_violation_id = models.AutoField(primary_key=True)
    frv_code_violation_unique_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    frv = models.ForeignKey(FRV, on_delete=models.CASCADE, related_name='frv_FRVCodeViolation')
    
    violation_date = models.DateTimeField(null=True, blank=True)
    violationType = models.ForeignKey(ViolationType, on_delete=models.SET_NULL, null=True, related_name='violationType_FRVCodeViolation')
    violation_description = models.TextField(null=True, blank=True)
    
    violation_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='violation_by_FRVCodeViolation')
    evidence_images = models.JSONField(default=dict, help_text="Violation evidence images", null=True, blank=True)
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_by_FRVCodeViolation')
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='updated_by_FRVCodeViolation')
    
    class Meta:
        indexes = [
            models.Index(fields=['frv']),  # For faster FRV-specific violation queries
            models.Index(fields=['violation_date']),  # For date-based searches
            models.Index(fields=['violationType']),  # For filtering by violation type
        ]
    
    def __str__(self):
        return f"Violation - {self.frv.vehicle_id} - {self.violation_date}"


class FRVClaim(BaseModel):
    """Claims related to FRV Operations"""
    frv_claim_id = models.AutoField(primary_key=True)
    frv_claim_unique_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    frv = models.ForeignKey(FRV, on_delete=models.CASCADE, related_name='frv_FRVClaim')
    
    claim_type = models.TextField(max_length=255,null=True, blank=True)
    claim_date = models.DateField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_by_FRVClaim')
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='updated_by_FRVClaim')
    
    class Meta:
        indexes = [
            models.Index(fields=['frv']),  
            models.Index(fields=['claim_date']),  # For date-based searches
            models.Index(fields=['claim_type']),  # For filtering by claim type
        ]
    
    def __str__(self):
        return f"Claim - {self.frv.vehicle_id} - {self.claim_type} - {self.claim_date}"