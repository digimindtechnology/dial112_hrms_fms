import uuid
from django.db import models
from django.contrib.auth.models import User

from setup.models import TrainerType
from tenant.models import TenantProfile
from masters.models import Gender, BaseModel





class Trainer(BaseModel):
    trainer_id = models.AutoField(primary_key=True)
    trainer_unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    trainer_or_organization_name = models.CharField(max_length=500)
    trainerType = models.ForeignKey(TrainerType, on_delete=models.CASCADE, related_name='trainers')
    email = models.EmailField(blank=True, null=True)
    mobile_no = models.CharField(max_length=20, blank=True)
    specialization = models.TextField(blank=True)
    designation = models.CharField(max_length=100, blank=True, null=True)
    gender = models.ForeignKey(Gender, on_delete=models.SET_NULL, null=True)
    picture = models.CharField(max_length=500, blank=True, null=True)
    rate_per_hour = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    address = models.TextField(blank=True)
    description = models.TextField(blank=True)
    tenantProfile = models.ForeignKey(TenantProfile, blank=True, null=True, on_delete=models.CASCADE, related_name='tenantProfile_trainer')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_by_trainer')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_by_trainer')

    class Meta:
        ordering = ['trainer_or_organization_name']

    def __str__(self):
        return self.trainer_or_organization_name


class TrainingStatus(models.Model):
    """
    Pending, In Progress, Overdue,
    Completed, Cancelled
    """
    training_status_id = models.AutoField(primary_key=True)
    training_status_name = models.CharField(max_length=100, unique=True)
    training_status_css = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ('training_status_id',)

    def __str__(self):
        return self.training_status_name


class TrainingType(models.Model):
    training_type_id = models.AutoField(primary_key=True)
    training_name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ('training_name',)

    def __str__(self):
        return self.training_name


class TrainingWiseTrainer(models.Model):
    training_wise_trainer_id = models.AutoField(primary_key=True)
    trainingType = models.ForeignKey(TrainingType, on_delete=models.CASCADE, related_name='trainingType_TrainingWiseTrainer')
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE, related_name='trainer_TrainingWiseTrainer')
    description = models.TextField(blank=True)
    is_available = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ('training_wise_trainer_id',)

    def __str__(self):
        return self.trainingType.training_name


class TrainingProgram(BaseModel):
    training_program_id = models.AutoField(primary_key=True)
    training_program_unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    training_title = models.CharField(max_length=500)

    training_program_picture = models.CharField(max_length=500, blank=True, null=True)
    batch_size = models.PositiveIntegerField(default=0)
    training_content = models.TextField()

    venue = models.CharField(max_length=500)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    start_date = models.DateField()
    end_date = models.DateField()

    start_time = models.TimeField()
    end_time = models.TimeField()

    total_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    rate_per_hour = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_payable_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0) ##total_hours * rate_per_hour

    trainingType = models.ForeignKey(TrainingType, on_delete=models.CASCADE, related_name='trainingType_training_programs')
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE, related_name='trainer_training_programs')
    trainingStatus = models.ForeignKey(TrainingStatus, on_delete=models.CASCADE, related_name='trainingStatus_training_programs')
    training_program_doc = models.CharField(max_length=500, blank=True, null=True)
    description = models.TextField(blank=True)
    tenantProfile = models.ForeignKey(TenantProfile, blank=True, null=True, on_delete=models.CASCADE, related_name='training_programs')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_training_programs')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_training_programs')

    class Meta:
        ordering = ['training_title']

    def __str__(self):
        return self.training_title


class TrainingProgramAttendee(BaseModel):
    training_program_attendee_id = models.AutoField(primary_key=True)
    trainingProgram = models.ForeignKey(TrainingProgram, on_delete=models.CASCADE, related_name='attendees')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='training_programs')
    total_days = models.IntegerField(default=0)
    no_of_day_attendant = models.IntegerField(default=0)
    no_of_day_not_attendant = models.IntegerField(default=0)
    feedback = models.TextField(blank=True)
    remark_feedback = models.TextField(blank=True)
    rating = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['training_program_attendee_id']

    def __str__(self):
        return f"{self.employee} - {self.trainingProgram}"
