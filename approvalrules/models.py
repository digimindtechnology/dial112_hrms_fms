from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from masters.models import BaseModel
from tenant.models import Role, TenantProfile


class ApprovalType(models.Model):
    approval_type_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    sequence = models.IntegerField(default=0)
    redirect_url = models.CharField(max_length=1000, null=True, blank=True, help_text="Store redirect URL")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class ApprovalRule(BaseModel):
    approval_rule_id = models.AutoField(primary_key=True)
    sequence = models.IntegerField(default=0)
    approval_type = models.ForeignKey(ApprovalType, related_name="approval_rules", on_delete=models.CASCADE)
    role = models.ForeignKey(Role, related_name="approval_rules", null=True, blank=True, on_delete=models.CASCADE)
    approver = models.ForeignKey(User, related_name="approval_rules", null=True, blank=True, on_delete=models.CASCADE)
    sla_hrs = models.PositiveIntegerField(null=True, blank=True)
    tenantProfile = models.ForeignKey(TenantProfile, related_name="approval_rules", on_delete=models.CASCADE, verbose_name="Tenant")
    created_by = models.ForeignKey(User, related_name="created_approval_rules", on_delete=models.CASCADE)
    updated_by = models.ForeignKey(User, related_name="updated_approval_rules", null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        ordering = ("sequence",)

    def __str__(self):
        return f"{self.approval_type.name} - {self.sequence}"


class Approver(BaseModel):
    STATUS_CHOICES = (("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected"),)
    approver_id = models.AutoField(primary_key=True)
    approval_type = models.ForeignKey(ApprovalType, related_name="approvers", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="approvals", on_delete=models.CASCADE)
    role = models.ForeignKey(Role, related_name="approvers", null=True, blank=True, on_delete=models.CASCADE)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    display_name = models.CharField(max_length=100, null=True, blank=True, help_text="Display name in table/form")
    sequence = models.IntegerField(default=0)

    sla_hrs = models.PositiveIntegerField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    object_id = models.PositiveIntegerField(help_text="Related object ID")
    tenantProfile = models.ForeignKey(TenantProfile, related_name="approvers", on_delete=models.CASCADE, verbose_name="Tenant")
    created_by = models.ForeignKey(User, related_name="created_approvers", on_delete=models.CASCADE)
    updated_by = models.ForeignKey(User, related_name="updated_approvers", null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        ordering = ("sequence",)

    def __str__(self):
        if self.user:
            return self.user.get_full_name() or self.user.username
        return "No User"

    def save(self, *args, **kwargs):
        if self.sla_hrs:
            self.end_date = timezone.now() + timedelta(hours=self.sla_hrs)

        super().save(*args, **kwargs)

    @property
    def is_rule_active(self):
        return ApprovalRule.objects.filter(approval_type=self.approval_type, tenantProfile=self.tenantProfile, role=self.role, approver=self.user, is_active=True).exists()

    @property
    def is_current_approver(self):
        previous_approvers = Approver.objects.filter(object_id=self.object_id, sequence__lt=self.sequence, approval_type=self.approval_type, tenantProfile=self.tenantProfile, is_active=True)
        for approver in previous_approvers:
            if not approver.is_rule_active:
                continue
            if approver.status != "approved":
                return False
        return self.status == "pending"

    @property
    def is_fully_approved(self):
        approvers = Approver.objects.filter(object_id=self.object_id, approval_type=self.approval_type, tenantProfile=self.tenantProfile, is_active=True)
        for approver in approvers:
            if not approver.is_rule_active:
                continue
            if approver.status != "approved":
                return False
        return True
